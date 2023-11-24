import os
import json
import datetime
import time
import requests
import aiohttp
import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import logging
from functools import wraps
from pathlib import Path

# from pytz import timezone
from urllib.parse import urljoin, quote_plus
from websockets import connect
import asyncio
import ssl
import certifi
from ccdxt.base import Transaction

# from pypac import PACSession
# from scrapy import Selector

from ccdxt.base.utils.retry import retry, retry_normal
from ccdxt.base.utils.type import is_dict, is_list
from ccdxt.base import Chain, Market, Pool, Token, Transaction
from ccdxt.base.utils.errors import (
    ABIFunctionNotFound,
    RevertError,
    NotSupported,
)

# from ccdxt.base.utils.validation import *
from ccdxt.base.utils import SafeMath

from decimal import Decimal
from typing import Optional, Union, Tuple, Callable, Any
from eth_typing.evm import Address

# from eth_typing import ChecksumAddressd

from web3 import Web3, middleware
from web3.eth import AsyncEth
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS
from web3._utils.abi import get_abi_output_types, map_abi_data
from web3.middleware import (
    async_geth_poa_middleware,
    geth_poa_middleware,
    construct_sign_and_send_raw_middleware,
)

from web3.exceptions import BadResponseFormat

from web3.types import (
    TxParams,
    FunctionIdentifier,
    BlockIdentifier,
    ABI,
    ABIFunction,
    CallOverrideParams,
)
from web3._utils.contracts import prepare_transaction, find_matching_fn_abi

# from web3.contract import Contract, ContractFunction, ACCEPTABLE_EMPTY_STRINGS
from web3.exceptions import BadFunctionCallOutput
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.providers.auto import (
    load_provider_from_uri,
)


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


class Exchange(Transaction):
    """Base exchange class"""

    def __init__(self):
        # chain info
        self.chains: Optional[dict] = None
        self.network_path: Optional[str] = None
        self.baseDecimal = 18

        # market info
        self.host = 0
        self.total_node = 1
        self.proxy = False
        self.chainName: Optional[str] = None
        self.exchangeName: Optional[str] = None
        self.rateLimit: Optional[int] = 2000  # milliseconds = seconds * 1000
        self.markets: Optional[dict] = None
        self.tokens: Optional[dict] = None
        self.timeOut = 3600
        self.retries = 1

        # etc
        self.unlimit = (
            115792089237316195423570985008687907853269984665640564039457584007913129639935
        )
        self.additionalGasFee = 0
        self.endurable_gasFee = 1
        self.gas_price = 0
        self.least_balance = 0.1

        # private info
        self.privateKey: Optional[str] = None  # a "0x"-prefixed hexstring private key for a wallet
        self.account: Union[Address, str, None] = None  # the wallet address "0x"-prefixed hexstring

        self.set_logger(None)

    # @retry
    async def partial_balance(self, tokenSymbol: str) -> dict:
        """
        Info
        ----------
        Returns the balance of a given token for a given account.

        Parameters
        ----------
        tokenSymbol: str
            The symbol of the token to get the balance for.

        Returns
        -------
        result: dict
            A dictionary containing the symbol and balance of the token.
        """

        token = self.tokens[tokenSymbol]

        accountAddress = self.set_checksum(self.account)

        if tokenSymbol == self.chains["baseCurrency"]:
            balance = await self.w3.eth.get_balance(accountAddress)

            balance = self.to_value(balance, self.baseDecimal)

        else:
            tokenAaddress = self.set_checksum(token["contract"])

            tokenContract = await self.get_contract(tokenAaddress, self.chains["chainAbi"])

            balance = await tokenContract.functions.balanceOf(accountAddress).call()

            balance = self.to_value(balance, int(token["decimals"]))

        result = {"symbol": token["symbol"], "balance": balance}

        return result

    def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None):
        raise NotSupported("create_swap() is not supported yet")

    def create_reuqest_detail(self, base_url, site_config_list=[]):
        if site_config_list:
            full_params = ""

            for config in site_config_list:
                params = config[0] + config[0].join(
                    "{}={}".format(k, config[1][k]) for k in sorted(config[1])
                )

                full_params += params

        else:
            full_params = ""

        full_site = base_url + full_params

        return full_site

    @retry
    async def create_request(self, base_url, params={}, *args, **kwargs):
        requst_args = ""
        requst_kwargs = ""
        request_method = "get"
        proxy = False

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        }

        if args:
            requst_args = "/".join(args)

        if kwargs:
            if "header" in kwargs:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    kwargs["header"][0]: kwargs["header"][1],
                }

                kwargs.pop("header", None)

            if "request_method" in kwargs:
                request_method = kwargs["request_method"]
                kwargs.pop("request_method", None)

            if "proxy" in kwargs:
                proxy = kwargs["proxy"]
                kwargs.pop("proxy", None)

            for kwarg in kwargs:
                requst_kwargs += f"{kwarg}={kwargs[kwarg]}"

        full_url = base_url + requst_args + requst_kwargs

        if request_method == "get":
            if proxy:
                async with aiohttp.ClientSession() as session:
                    proxies = {"http": proxy, "https": proxy}
                    async with session.get(
                        full_url, headers=headers, params=params, proxy=proxies, timeout=3
                    ) as response:
                        r = response

                        if r.status == 200:
                            result = await r.text()
                            result = json.loads(result)

                        else:
                            logging.warning(
                                f"api failed request, detail -> url : {full_url}, params : {params}"
                            )

                            raise BadResponseFormat(f"api failed , status_code : {r.status}")
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(full_url, headers=headers, params=params) as response:
                        r = response

                        if r.status == 200:
                            result = await r.text()
                            result = json.loads(result)

                        else:
                            logging.warning(
                                f"api failed request, detail -> url : {full_url}, params : {params}"
                            )

                            raise BadResponseFormat(f"api failed , status_code : {r.status}")

        elif request_method == "post":
            if proxy:
                async with aiohttp.ClientSession() as session:
                    proxies = {"http": proxy, "https": proxy}
                    async with session.post(
                        full_url, headers=headers, json=params, proxy=proxies, timeout=3
                    ) as response:
                        r = response

                        if r.status == 200:
                            result = await r.text()
                            result = json.loads(result)

                        else:
                            logging.warning(
                                f"api failed request, detail -> url : {full_url}, params : {params}"
                            )

                            raise BadResponseFormat(f"api failed , status_code : {r.status}")
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(full_url, headers=headers, json=params) as response:
                        r = response

                        if r.status == 200:
                            result = await r.text()
                            result = json.loads(result)

                        else:
                            logging.warning(
                                f"api failed request, detail -> url : {full_url}, params : {params}"
                            )

                            raise BadResponseFormat(f"api failed , status_code : {r.status}")

        return result

    async def create_transfer(self, amount, tokenSymbol, fromChain, toAddr):
        await self.load_exchange(fromChain)

        token = self.tokens[tokenSymbol]
        self.tokenSymbol = tokenSymbol

        self.fromChain = fromChain
        self.toChain = fromChain
        self.amount = amount

        amount_transfer = self.from_value(value=amount, exp=int(token["decimals"]))

        accountAddress = self.set_checksum(self.account)
        tokenAaddress = self.set_checksum(token["contract"])
        self.toAddrress = self.set_checksum(toAddr)

        tokenContract = await self.get_contract(tokenAaddress, self.chains["chainAbi"])

        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        if (fromChain == "KLAYTN") and (tokenSymbol == "KLAY"):
            tx = {
                "to": self.toAddrress,
                "value": amount_transfer,
                "gas": 400000,
                "gasPrice": Web3.to_wei("50", "gwei"),
                "nonce": self.nonce,
            }

        elif (fromChain == "MOOI") and (tokenSymbol == "MOOI"):
            tx = {
                "to": self.toAddrress,
                "value": amount_transfer,
                "gas": 400000,
                "gasPrice": Web3.to_hex(25000000000),
                "nonce": self.nonce,
            }

        else:
            tx = tokenContract.functions.transfer(
                self.toAddrress, amount_transfer
            ).build_transaction(
                {
                    "from": self.account,
                    "nonce": self.nonce,
                    "gas": 4000000,
                    "value": 0,
                }
            )

        tx_receipt = self.fetch_transaction(tx, round="TRANSFER")

        tx_receipt["amount_in"] = self.amount
        tx_receipt["amount_out"] = self.amount

        return tx_receipt

    async def subscribe(self, params, ws_url=None):
        """
        Info
        ----------
        Subscribes to new pending transactions for a given account.

        Parameters
        ----------
        ws_url: str, optional
            The web socket URL to use. If not provided, the mainnet web socket URL from `self.chains` will be used.

        Returns
        -------
        None
            This function does not return anything. It simply prints out the subscription response and listens for new pending transactions indefinitely. If a transaction is received that is intended for the account specified in `self.account`, the function will return.
        """

        if ws_url == None:
            ws_url = self.chains["mainnet"]["webscoket"]

        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())

        queryRaw = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            # "params": ["newPendingTransactions"],
            "params": [params],
        }

        query = json.dumps(queryRaw)

        async with connect(ws_url, ssl=ssl_context) as ws:
            await ws.send(query)
            subscription_response = await ws.recv()
            logging.info(
                subscription_response
            )  # {"jsonrpc":"2.0","id":1,"result":"0xd67da23f62a01f58042bc73d3f1c8936"}

            while True:
                message = await asyncio.wait_for(ws.recv(), timeout=1800)
                response = json.loads(message)
                logging.info(
                    response
                )  # {'jsonrpc': '2.0', 'method': 'eth_subscription', 'params': {'subscription': '0x878ab62df576e724c785b020f3abf971', 'result': '0xdf52eb6b791e697582b0c4758172fb0b52c54c2ffbfed186b801a66bd9a8780d'}}
                tx_hash = response["params"]["result"]

                # tx = self.w3.eth.get_transaction(tx_hash)

                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=1800)

                logging.info(tx_receipt)

                # if tx.to == self.account:

                #     return

    def get_proxy_list(self):
        pass

    #     proxy_url = "https://www.socks-proxy.net/"

    #     resp = requests.get(proxy_url)
    #     sel = Selector(resp)
    #     tr_list = sel.xpath('//*[@id="list"]/div/div[2]/div/table/tbody/tr')
    #     proxy_server_list = []

    #     for tr in tr_list:
    #         ip = tr.xpath("td[1]/text()").extract_first()
    #         port = tr.xpath("td[2]/text()").extract_first()
    #         https = tr.xpath("td[7]/text()").extract_first()

    #         if https == "Yes":
    #             server = f"{ip}:{port}"
    #             proxy_server_list.append(server)

    #     return proxy_server_list

    # def updateTxParameters(self):
    #     """
    #     Info
    #     ----
    #     Updates the transaction parameters by making an HTTP request to a gas station API.

    #     Parameters
    #     ----------
    #     None

    #     Returns
    #     -------
    #     maxPriorityFee: int
    #         The maximum priority fee.
    #     maxFee: int
    #         The maximum fee.
    #     """
    #     r = requests.get("https://gasstation-mainnet.matic.network/v2")
    #     gas = r.json()

    #     maxPriorityFee = gas["fast"]["maxPriorityFee"]
    #     maxFee = gas["fast"]["maxFee"]

    #     return maxPriorityFee, maxFee

    async def get_gasPrice(self):
        if self.chains == None:
            fast_gas = 25000000000

            return int(fast_gas)

        if self.chains["mainnet"]["chain_id"] not in (8217, 1201):
            if self.proxy:
                fast_gas = await self.create_request(
                    "https://ethapi.openocean.finance/",
                    {},
                    "v2",
                    f"{self.chains['mainnet']['chain_id']}",
                    "gas-price",
                    proxy=self.proxy,
                )

                fast_gas = fast_gas["fast"]

            else:
                fast_gas = await self.create_request(
                    "https://ethapi.openocean.finance/",
                    {},
                    "v2",
                    f"{self.chains['mainnet']['chain_id']}",
                    "gas-price",
                )

                fast_gas = fast_gas["fast"]

        else:
            fast_gas = await self.get_maxPriorityFeePerGas()

            if fast_gas == 0:
                fast_gas == await self.estimate_gas()

        return int(fast_gas)

    def get_fee_history(self):
        block_count = 0xA
        newest_block = "latest"
        reward_percentiles = [25, 75]

        method = "eth_feeHistory"
        params = [hex(block_count), newest_block] + [reward_percentiles]
        return self.w3.manager.request_blocking(method, params)

    async def get_maxPriorityFeePerGas(self):
        method = "eth_maxPriorityFeePerGas"
        params = []

        return await self.w3.manager.request_blocking(method, params)

    async def get_base_fee(self):
        method = "eth_baseFee"
        params = []

        try:
            hex_string = await self.w3.manager.request_blocking(method, params)
            integer_value = int(hex_string, 16)

        except:
            integer_value = 25000000000
            pass

        return integer_value

    def block_number(self) -> str:
        """
        Returns
        -------
        result: Block number
        """
        return self.w3.eth.block_number

    async def get_contract(self, address: str, abi: dict):
        """
        Parameters
        ----------
        address : Contract address
        abi : Contract abi

        Returns
        -------
        result: a contract object.
        """

        # if is_score_address(address) :

        return self.w3.eth.contract(address, abi=abi)

        # else:load_exchange
        #     raise AddressError("Address is wrong.")

    async def decimals(self, tokenSymbol):
        """
        Parameters
        ----------
        tokenSymbol : token symbol

        Returns
        -------
        result: decimals of token
        """

        token = self.tokens[tokenSymbol]
        tokenAddress = self.set_checksum(token["contract"])

        if self.tokens[tokenSymbol]["decimals"]:
            return int(self.tokens[tokenSymbol]["decimals"])

        try:
            tokenContract = await self.get_contract(tokenAddress, self.chains["chainAbi"])

            if "decimals" not in self.tokens[tokenSymbol]:
                decimals = await tokenContract.functions.decimals().call()
                self.tokens[tokenSymbol]["decimals"] = decimals

                # self.save_token(self.tokens)

            else:
                decimals = self.tokens[tokenSymbol]["decimals"]

            return int(decimals)
        except ABIFunctionNotFound:
            return 18

    def __exist(self, tokenAsymbol, tokenBsymbol):
        pair_address = self.getPair(tokenAsymbol, tokenBsymbol)
        return int(pair_address, 16) != 0

    async def get_pool(self, tokenAsymbol, tokenBsymbol):
        """
        Info
        ----
        Gets the pool address for a pair of tokens.

        Parameters
        ----------
        tokenAsymbol: str
            The symbol of the first token in the pair.
        tokenBsymbol: str
            The symbol of the second token in the pair.

        Returns
        -------
        pair: str
            The address of the pool for the given pair of tokens.
        """

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])

        routerAddress = self.set_checksum(self.markets["routerAddress"])

        try:
            factoryContract = await self.get_contract(routerAddress, self.markets["factoryAbi"])

            token_sort = sorted([tokenAsymbol, tokenBsymbol])

            pool_name = token_sort[0] + "-" + token_sort[1]

            if pool_name not in self.pools:
                pair = factoryContract.functions.tokenToPool(tokenAaddress, tokenBaddress).call()

                self.pools = self.deep_extend(
                    self.pools,
                    {
                        pool_name: {
                            "name": pool_name,
                            "baseChain": {self.chainName: {self.exchangeName: pair}},
                        }
                    },
                )
                # Pool().save_pool(self.pools)
            else:

                pair = dict(self.pools[pool_name])["poolAddress"]

            return pair
        except ABIFunctionNotFound:
            return logging.warning("No ABI found")

    async def get_pair(self, tokenAsymbol, tokenBsymbol):
        """
        Info
        ----
        Gets the pool address for a pair of tokens.

        Parameters
        ----------
        tokenAsymbol: str
            The symbol of the first token in the pair.
        tokenBsymbol: str
            The symbol of the second token in the pair.

        Returns
        -------
        pool: str
            The address of the pool for the given pair of tokens.
        """

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])

        routerAddress = self.set_checksum(self.markets["factoryAddress"])

        try:
            factoryContract = await self.get_contract(routerAddress, self.markets["factoryAbi"])

            token_sort = sorted([tokenAsymbol, tokenBsymbol])

            pool_name = token_sort[0] + "-" + token_sort[1]

            if pool_name not in self.pools:
                pair = await factoryContract.functions.getPair(tokenAaddress, tokenBaddress).call()

                self.pools = self.deep_extend(
                    self.pools,
                    {
                        pool_name: {
                            "name": pool_name,
                            "baseChain": {self.chainName: {self.exchangeName: pair}},
                        }
                    },
                )
                # Pool().save_pool(self.pools)
            else:
                pair = dict(self.pools[pool_name])["poolAddress"]
            return pair
        except ABIFunctionNotFound:
            return logging.warning("No ABI found")

    async def reversed(self, tokenAaddress, tokenBaddress):
        try:
            factoryContract = await self.get_contract(tokenAaddress, self.markets["factoryAbi"])

            pair = factoryContract.functions.tokenA(tokenAaddress).call()
            self.__pairs[tokenAaddress + tokenBaddress] = pair
            return pair
        except ABIFunctionNotFound:
            return logging.warning("No ABI found")

    def reserve_ratio(self, input=None, output=None, intermediate=None, refresh=False):
        reserves = self.reserves(input, output, intermediate, refresh)
        if self.reversed(input, output):
            return reserves[0] / reserves[1]
        else:
            return reserves[1] / reserves[0]

    def getAmountsOut(self, amount, path):
        return self.router_contract.functions.getAmountsOut(int(amount), path).call()[-1]

    async def sync(self, pool):
        contract = await self.get_contract(pool, self.chains["chainAbi"])
        return await contract.functions.sync().call()

    def require(self, execute_result: bool, msg):
        if execute_result:
            raise msg

    async def get_gas_fixingRate(self):
        # r = requests.get("https://token-rates-aggregator.1inch.io/v1.0/native-token-rate?vs=US")

        try:
            if self.chains["baseCurrency"] == "MOOI":
                params = {"ids": self.chains["coingecko_id"], "vs_currencies": "usd"}

                fixingRate = await self.create_request(
                    "https://api.coingecko.com/", params, "api", "v3", "simple", "price"
                )

                fixingRate = fixingRate[self.chains["coingecko_id"]]["usd"]

            else:
                params = {"symbol": self.chains["baseCurrency"] + "USDT"}

                fixingRate = await self.create_request(
                    "https://api.binance.com/", params, "api", "v3", "ticker", "price"
                )

                fixingRate = fixingRate["price"]

        except:
            fixingRate = 0

        return float(fixingRate)

    async def decode(self, tx_hash):
        routerAddress = self.set_checksum(self.markets["routerAddress"])

        if "version" in self.markets:
            routerContract = await self.get_contract(
                routerAddress, self.markets["routerAbi"][int(self.markets["version"])]
            )

        else:
            routerContract = await self.get_contract(routerAddress, self.markets["routerAbi"])

        # tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=1800)

        transaction = self.w3.eth.get_transaction(tx_hash)

        result = routerContract.decode_function_input(transaction.input)

        return result

    def allowance(self, tokenSymbol):
        token = self.tokens[tokenSymbol]
        tokenAddress = self.set_checksum(token["contract"])
        account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAbi"])

        contract = self.w3.eth.contract(tokenAddress, self.chains["chainAbi"])
        return contract.functions.allowance(account, routerAddress).call()

    async def fees(self, input=None, output=None, intermediate=None, amount=1):
        ratio = self.reserve_ratio(input, output, intermediate)
        amount = amount * await self.decimals(input)
        price = self.price(amount, input, output, intermediate)
        price = price / await self.decimals(output)
        return 1 - price / ratio

    async def estimate_gas(self):
        try:
            result = await self.w3.eth.gasPrice / 1000000000

        except:
            result = await self.get_base_fee()

        return result

    async def get_TransactionCount(self, address: str):
        nonce = await self.w3.eth.get_transaction_count(address)

        return nonce

    def fetch_tokens(self):
        return self.tokens

    @retry
    async def fetch_balance(self, tokens=None, *args, **kwargs):
        balances = {}

        if tokens is not None:
            if is_list(tokens):
                symbols = tokens

            else:
                symbols = list(tokens)
        else:
            symbols = list(self.tokens.keys())

        for symbol in symbols:
            balance = self.partial_balance(symbol)
            balances[balance["symbol"]] = balance["balance"]

        if "pool" in kwargs:
            pool_balances = self.pool_balance(kwargs["pool"])

            for pool_balance in pool_balances:
                if pool_balance in balances:
                    balances[pool_balance] += pool_balances[pool_balance]

                else:
                    balances[pool_balance] = pool_balances[pool_balance]

        return balances

    async def check_sync(self):
        return await self.w3.eth.syncing

    async def check_approve(
        self, amount: int, token: str, account: str, router: str, build: dict, *args, **kwargs
    ):
        """
        Info
        ----
        Check if the given token has been approved for use by the given account and router address, and if not, transact the approval.

        Parameters
        ----------
        amountA: int
            The amount of the token to approve.
        token: str
            The address of the token.
        account: str
            The address of the account.
        router: str
            The address of the router.

        Returns
        -------
        tx_receipt: dict
            The transaction receipt if the approval was made. Otherwise, returns None.
        """

        if token == self.chains["baseContract"]:
            return

        contract = await self.get_contract(token, self.chains["chainAbi"])

        approvedTokens = await contract.functions.allowance(account, router).call()

        if "approve_amount" in kwargs:
            approve_amount = kwargs["approve_amount"]

        else:
            approve_amount = self.unlimit

        if approvedTokens < amount:
            tx = await self.get_approve(token, router, account, approve_amount, build)

            tx_receipt = await self.fetch_transaction(tx, round="CHECK")
            return tx_receipt

        else:
            return

    async def get_approve(self, token: str, router: str, account: str, approvedTokens: int, build):
        contract = await self.get_contract(token, self.chains["chainAbi"])

        tx = await contract.functions.approve(router, approvedTokens).build_transaction(build)

        return tx

    def set_logger(self, filePath):
        # if filePath == None :

        #     #default_log
        #     basePath = Path(__file__).resolve().parent.parent
        #     logfile_name = 'logfile.log'
        #     filePath = str(os.path.join(basePath, logfile_name))

        logging.basicConfig(
            level=logging.INFO,
            filename=filePath,
            filemode="w",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # logging.Formatter.converter = lambda *args: datetime.datetime.now(
        #     tz=timezone("Asia/Seoul")
        # ).timetuple()

        self.logger = logging.getLogger(__name__)

    def create_session(self):
        session = requests.Session()
        session.mount("https://", SSLAdapter())
        return session

    async def updateTxParameters(self):
        gas = await self.create_request(
            f"https://gas-price-api.1inch.io/v1.3/{self.chains['mainnet']['chain_id']}"
        )

        try:
            maxPriorityFeePerGas = int(gas["high"]["maxPriorityFeePerGas"])
            maxFeePerGas = int(gas["high"]["maxFeePerGas"])

        except:
            maxPriorityFeePerGas = 50000000000
            maxFeePerGas = 75000000000

        base_fee = await self.get_base_fee()

        if maxFeePerGas < base_fee:
            maxFeePerGas = base_fee

        return maxPriorityFeePerGas, maxFeePerGas

    def base_txDict(self):
        txDict = {
            "from_network": self.chains["name"],
            "to_network": self.chains["name"],
            "tx_hash": "",
            "status": 2,  # pending
            "block": "",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": "",
            "from_address": "",
            "amount_in": 0,
            "token_in": self.tokenSymbol,
            "to_address": "",
            "amount_out": 0,
            "token_out": self.tokenBsymbol,
            "gas_fee": 0,
            "tx_scope": "",
        }

        return txDict

    async def get_node(self, host, chainName):
        """
        Info
        ----
        Gets the node information for the given host and chain name.

        Parameters
        ----------
        host: str
            The hostname of the node.
        chainName: str
            The name of the chain.

        Returns
        -------
        node: dict
            The dictionary containing the node information.
        """

        basePath = Path(__file__).resolve().parent.parent.parent

        nodeDictPath = os.path.join(basePath, "key", "pv_node.json")

        if Path(nodeDictPath).exists():
            with open(nodeDictPath, "rt", encoding="utf-8") as f:
                nodeDict = json.load(f)

            self.total_node = len(nodeDict[chainName])

            if host >= len(nodeDict[chainName]):

                host = 0

            node = nodeDict[chainName][host]

        else:
            raise ValueError(f"can not find path : {nodeDictPath}")

        return node

    async def load_exchange(self, chainName, exchangeName=None):
        self.load_chains(chainName)
        self.baseCurrency = self.chains["baseCurrency"]
        self.load_markets(chainName, exchangeName)

        self.load_pools(chainName, exchangeName, self.markets["pool_pass"])
        self.load_tokens(chainName, exchangeName, self.baseCurrency, self.markets["token_pass"])

        # self.w3 = self.set_async_network(self.chains['mainnet']['public_node'])

        if self.host == None:
            self.exchange_node = self.chains["mainnet"]["public_node"]

            # self.w3 = self.set_network(self.exchange_node)
            self.w3 = self.set_async_network(self.exchange_node)

        else:

            self.exchange_node = await self.get_node(self.host, chainName)

            # self.w3 = self.set_network(self.exchange_node)
            self.w3 = self.set_async_network(self.exchange_node)

        # if self.chains["POS"]:
        #     await self.set_pos()

    def load_chains(self, chainName):
        self.chains = self.set_chains(chainName)

        # self.chains = {}

        if not self.chains:
            self.chains = self.safe_chain()

    def load_markets(self, chainName, exchangeName):
        self.markets = self.set_markets(chainName, exchangeName)

        # self.markets = {}

        if not self.markets:
            self.markets = self.safe_market()

    async def load_bridge(self, bridgeName):
        markets = self.set_all_markets(bridgeName)

        self.bridge = {}

        if markets:
            self.bridge = self.deep_extend(self.set_all_markets(bridgeName), markets)

    def load_pools(self, chainName, exchangeName, passing=False):
        self.pools = self.set_pools(chainName, exchangeName, passing)

        # self.pools = {}

        if not self.pools:
            self.pools = self.safe_pool()

    def load_tokens(self, chainName, exchangeName, baseCurrency, passing=False):
        self.tokens = self.set_tokens(chainName, exchangeName, baseCurrency, passing)

        if not self.tokens:
            self.tokens = self.safe_token()

    def load_all(self):
        # self.all_chains = self.set_all_chains()
        self.all_markets = self.set_all_markets()
        self.all_pools = self.set_all_pools()
        self.all_tokens = self.set_all_tokens()

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if is_dict(arg):
                if not is_dict(result):
                    result = {}
                for key in arg:
                    result[key] = Exchange.deep_extend(
                        result[key] if key in result else None, arg[key]
                    )
            else:
                result = arg
        return result

    @staticmethod
    def safe_chain():
        return Chain().__dict__

    @staticmethod
    def safe_market():
        return Market().__dict__

    @staticmethod
    def safe_pool():
        return Pool().__dict__

    @staticmethod
    def safe_token():
        return Token().__dict__

    @staticmethod
    def set_chains(chainName):
        return Chain().set_chain(chainName)

    @staticmethod
    def set_markets(chainName, exchangeName):
        return Market().set_market(chainName, exchangeName)

    @staticmethod
    def set_pools(chainName, exchangeName, passing):
        return Pool().set_pool(chainName, exchangeName, passing)

    @staticmethod
    def set_tokens(chainName, exchangeName, baseCurrency, passing):
        return Token().set_token(chainName, exchangeName, baseCurrency, passing)

    @staticmethod
    def set_all_chains():
        return Chain().set_all_chains()

    @staticmethod
    def set_all_markets(exchangeName):
        return Market().set_all_markets(exchangeName)

    @staticmethod
    def set_all_pools():
        return Chain().set_all_chains()

    @staticmethod
    def set_all_tokens():
        return Chain().set_all_chains()

    @staticmethod
    def set_network(network_path):
        return Web3(Web3.HTTPProvider(network_path, request_kwargs={"timeout": 1800}))

        # head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'}

        # PARAMS = {'headers':head}

        # return Web3(load_provider_from_uri(network_path))

    @staticmethod
    def set_async_network(network_path):

        return Web3(
            Web3.AsyncHTTPProvider(network_path, request_kwargs={"timeout": 1800}),
            modules={"eth": (AsyncEth,)},
            middlewares=[],
        )

    @staticmethod
    def set_checksum(value):
        return Web3.to_checksum_address(value)

    # async def set_pos(self):
    #     await self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    @staticmethod
    def from_value(value: float or int, exp: int = 18) -> int:
        return int(SafeMath.truncate(SafeMath.mul(value, 10**exp)))

    @staticmethod
    def to_value(value: float or int, exp: int = 18) -> Decimal:

        return SafeMath.truncate(SafeMath.div(float(Decimal(value)), 10**exp), 8)

    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
