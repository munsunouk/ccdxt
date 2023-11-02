from ..base.exchange import Exchange
from ..base.utils.errors import (
    InsufficientBalance,
)

from ..base.utils.retry import retry
from typing import Optional
from web3.exceptions import BadResponseFormat
import subprocess
import requests

# from Naked.toolshed.shell import execute
from requests.exceptions import HTTPError, ReadTimeout, ProxyError, SSLError, ConnectTimeout
from random import choice

# from proxy_requests.proxy_requests import ProxyRequests
import logging
import time
import os
from pathlib import Path
import asyncio
import datetime
import json


class Rubicfinance(Exchange):
    has = {
        "createSwap": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "chainName": "FTM",
            "exchangeName": "rubicfinance",
            "retries": 3,
            "retriesTime": 10,
            "host": None,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
        }

        config.update(config_change)

        # market info
        self.id = 1
        self.chainName = config["chainName"]
        self.exchangeName = config["exchangeName"]
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.proxy = config["proxy"]

        self.load_exchange(self.chainName, self.exchangeName)
        self.set_logger(self.log)

    # @retry
    # async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol, fusion=False):

    #     await asyncio.sleep(1)

    #     amountIn = self.from_value(value=amountAin, exp=self.decimals(tokenAsymbol))

    #     tokenA = self.tokens[tokenAsymbol]
    #     tokenB = self.tokens[tokenBsymbol]

    #     tokenAaddress = tokenA["contract"]
    #     tokenBaddress = tokenB["contract"]

    #     if tokenAaddress == self.chains['baseContract'] :
    #         tokenAaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

    #     elif tokenBaddress == self.chains['baseContract'] :
    #         tokenBaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

    #     if not fusion :

    #         params = {
    #             "fromTokenAddress": tokenAaddress,
    #             "toTokenAddress":tokenBaddress,
    #             "amount": amountIn,
    #         }

    #         url = f"https://api.1inch.io/v5.0/{self.chains['mainnet']['chain_id']}/quote"

    #         r = requests.get(url, params=params)

    #         if r.status_code == 200:

    #             result = r.json()

    #             amountout = self.to_value(
    #                 value=result["toTokenAmount"], exp=self.decimals(tokenBsymbol)
    #             )

    #         elif r.status_code == 500:

    #             raise InsufficientBalance(f"amountAin : {amountAin}")

    #         else:
    #             raise BadResponseFormat("1inch api failed")

    #     else :

    #         #amountBout = auction end amount + 10% 테스트
    #         quote = await self.get_fusion_quote(amountIn, tokenAaddress, tokenBaddress)

    #         amountout = int(quote['presets']['fast']['auctionEndAmount']) * 1.1

    #         amountout = self.to_value(
    #                 amountout, exp=self.decimals(tokenBsymbol)
    #             )

    #     result = {
    #         "amountAin": amountAin,
    #         "amountBout": amountout,
    #         "tokenAsymbol": tokenAsymbol,
    #         "tokenBsymbol": tokenBsymbol
    #     }

    #     return result

    @retry
    async def create_bridge(
        self, amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, toAddr, *args, **kwargs
    ):
        """
        Parameters
        ----------
        amountA : tokenA amount input
        tokenAsymbol: symbol of token input
        amountBMin : tokenB amount output which is expactation as minimun
        tokenBsymbol : symbol of tokenB output
        Return
        {
        'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4',
        'status': 1,
        'block': 34314499,
        'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156),
        'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>,
        'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
        'amountIn': 0.1,
        'tokenA': 'USDC',
        'to': '0x10f4A785F458Bc144e3706575924889954946639',
        'amountOut': 0.623371,
        'tokenB': 'oZEMIT',
        'transaction_fee:': 0.023495964646856035
        }
        """

        self.load_exchange(fromChain, self.exchangeName)
        self.tokenSymbol = from_tokenSymbol
        self.fromChain = fromChain
        self.toChain = toChain
        self.amount = amount
        self.privateKey = args[0]

        self.require(fromChain == toChain, ValueError("Same Chain"))
        self.require(from_tokenSymbol == to_tokenSymbol, ValueError("Same Symbol"))

        tokenA = self.tokens[from_tokenSymbol]
        tokenB = self.tokens[to_tokenSymbol]
        amount = self.from_value(value=amount, exp=int(tokenA["decimals"]))

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        accountAddress = self.set_checksum(self.account)

        routerAddress = self.set_checksum(self.markets["routerAddress"])

        self.check_approve(
            amount=amount, token=tokenAaddress, account=accountAddress, router=routerAddress
        )

        self.routerContract = self.get_contract(
            routerAddress, self.markets["routerAbi"][int(self.markets["version"])]
        )

        tx = await self._create_bridge(amount, tokenAaddress, tokenBaddress, fromChain, toChain)

        time_spend, amount = self.check_bridge_completed(to_tokenSymbol, self.account)

        # tx_receipt = self.fetch_transaction(tx, "FUSION_SWAP")

        # tx_receipt["amount_out"] = amount

        # params = {
        #     "fromChainId" : self.chains["mainnet"]["chain_id"],
        #     "fromSymbol": tokenA['symbol'],
        #     "toSymbol": tokenB['symbol'],
        #     "toChainId" : Network[self.toChain].value,
        #     "amount": amount,
        #     "sort" : "cheapestRoute",

        # }

        # quote_total_tx = self.create_request(params, 'cross_chain', 'v1', 'cross', 'quoteByOO')

        # logging.info(quote_total_tx)

        # raise

        # data = quote_total_tx['routes']['middlewareRoute'][self.chains['baseChain']]['data']
        # value = quote_total_tx['routes']['middlewareRoute'][self.chains['baseChain']]['value']

        # # gasPrice = self.get_gasPrice(self.chains["mainnet"]["chain_id"])

        # quote_input_tx = {
        #     "data" : data,
        #     "value" : value,
        # }

        # tx = self.create_tx(accountAddress, routerAddress, quote_input_tx)

        # return tx

        # input_tx_receipt = self.fetch_transaction(input_tx, "BRIDGE")

        # time_spend, amount = self.check_bridge_completed(to_tokenSymbol, toAddr)

        # output_tx = self._create_output_swap(
        #     tokenAaddress, amount, tokenBaddress, accountAddress, routerAddress, slippage, gasPrice
        # )

        # output_tx_receipt = self.fetch_transaction(output_tx, "SWAP")

        # return output_tx_receipt

    async def _create_bridge(self, amount, tokenAaddress, tokenBaddress, fromChain, toChain):
        if self.privateKey.startswith("0x"):
            self.privateKey = self.privateKey[2:]

        else:
            pass

        basePath = Path(__file__).resolve().parent
        oneinchPath = os.path.join(basePath, "rubicfinance.js")

        js_code = f"""
        const {{ bridge_js }} = require('{oneinchPath}');
        bridge_js({amount}, '{tokenAaddress}', '{tokenBaddress}', '{fromChain}', '{toChain}', '{self.account}', '{self.privateKey}', '{self.exchange_node}');
        """

        loop = asyncio.get_event_loop()
        quote_data = await loop.run_in_executor(
            None, subprocess.check_output, ["node", "-e", js_code]
        )

        result = quote_data.decode("utf-8")

        if result.startswith("Error:"):
            raise BadResponseFormat("rubic SDK failed")

        return result

    # @retry
    # async def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, fusion=False):
    #     """
    #     Parameters
    #     ----------
    #     amountA : tokenA amount input
    #     tokenAsymbol: symbol of token input
    #     amountBMin : tokenB amount output which is expactation as minimun
    #     tokenBsymbol : symbol of tokenB output
    #     Return
    #     {
    #     'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4',
    #     'status': 1,
    #     'block': 34314499,
    #     'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156),
    #     'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>,
    #     'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
    #     'amountIn': 0.1,
    #     'tokenA': 'USDC',
    #     'to': '0x10f4A785F458Bc144e3706575924889954946639',
    #     'amountOut': 0.623371,
    #     'tokenB': 'oZEMIT',
    #     'transaction_fee:': 0.023495964646856035
    #     }
    #     """

    #     await asyncio.sleep(1)

    #     if (path != None) and (len(path) > 2):

    #         self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path[1:-1]]

    #     else:

    #         self.path = []

    #     self.tokenSymbol = tokenAsymbol
    #     self.tokenBsymbol = tokenBsymbol
    #     self.amount = amountA

    #     self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
    #     self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

    #     tokenA = self.tokens[tokenAsymbol]
    #     tokenB = self.tokens[tokenBsymbol]
    #     amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
    #     amountBMin = self.from_value(value=amountBMin, exp=int(tokenB["decimals"]))

    #     tokenAaddress = self.set_checksum(tokenA["contract"])
    #     tokenBaddress = self.set_checksum(tokenB["contract"])

    #     if tokenAaddress == self.chains['baseContract'] :
    #         tokenAaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

    #     elif tokenBaddress == self.chains['baseContract'] :
    #         tokenBaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

    #     self.account = self.set_checksum(self.account)

    #     routerAddress = self.set_checksum(self.markets["routerAddress"])

    #     self.check_approve(
    #         amountA=amountA, token=tokenAaddress, account=self.account, router=routerAddress
    #     )

    #     self.routerContract = self.get_contract(
    #         routerAddress, self.markets["routerAbi"][int(self.markets["version"])]
    #     )

    #     if not fusion :

    #         tx = self.token_to_token(
    #             tokenAaddress, amountA, tokenBaddress, self.account, routerAddress
    #         )

    #         tx_receipt = self.fetch_transaction(tx, "SWAP")

    #     else :

    #         tx = await self.create_fusion_swap(amountA, tokenAaddress, tokenBaddress)

    #         logging.info(tx)

    #         time_spend, amount = self.check_bridge_completed(tokenBsymbol, self.account)

    #         tx_receipt = self.fetch_transaction(tx, "FUSION_SWAP")

    #         tx_receipt["amount_out"] = amount

    #     return tx_receipt

    def get_rate(self, tokenAaddress, tokenBaddress):
        tx = self.routerContract.functions.getRate(tokenAaddress, tokenBaddress).call()

        return tx

    async def get_fusion_quote(self, amount, tokenA, tokenB):
        basePath = Path(__file__).resolve().parent
        oneinchPath = os.path.join(basePath, "oneinchswap.js")

        js_code = f"""
        const {{ quote_js }} = require('{oneinchPath}');
        quote_js({amount}, '{tokenA}', '{tokenB}', '{self.account}', '{self.chains['mainnet']['chain_id']}');
        """

        loop = asyncio.get_event_loop()
        quote_data = await loop.run_in_executor(
            None, subprocess.check_output, ["node", "-e", js_code]
        )

        result = quote_data.decode("utf-8")

        # .strip('\n')

        if result.startswith("Error:"):
            raise BadResponseFormat("1inch SDK failed")

        else:
            result = json.loads(result)

        return result

    def get_proxy_list(self):
        pass

    def token_to_token(self, tokenAaddress, amountA, tokenBaddress, accountAddress, routerAddress):
        if (tokenAaddress == self.chains["baseContract"]) and (self.chainName == "KLAYTN"):
            tokenAaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        elif (tokenBaddress == self.chains["baseContract"]) and (self.chainName == "KLAYTN"):
            tokenBaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        params = {
            "fromTokenAddress": tokenAaddress,
            "toTokenAddress": tokenBaddress,
            "amount": amountA,
            "fromAddress": self.account,
            "slippage": 50,
            "disableEstimate": "true",
        }

        if self.proxy:
            self.proxy_list = self.get_proxy_list()

            while True:
                retries = self.retries

                if retries != 0:
                    if len(self.proxy_list) == 0:
                        retries -= 1
                        time.sleep(self.retriesTime)
                        self.proxy_list = self.get_proxy_list()

                    else:
                        retries = self.retries

                        proxy_server = choice(self.proxy_list)
                        proxies = {"http": proxy_server, "https": proxy_server}

                        try:
                            r_swap = requests.get(
                                f"https://api.1inch.io/v{self.markets['version']}/{self.chains['mainnet']['chain_id']}/swap",
                                params=params,
                                proxies=proxies,
                                timeout=3,
                            )

                            if r_swap.status_code == 200:
                                result = r_swap.json()
                                break

                            else:
                                self.proxy_list.remove(proxy_server)
                                continue

                        except (ProxyError, SSLError, ConnectTimeout) as e:
                            self.proxy_list.remove(proxy_server)
                            continue

                else:
                    raise BadResponseFormat("1inch api failed")

        else:
            r_swap = requests.get(
                f"https://api.1inch.io/v{self.markets['version']}/{self.chains['mainnet']['chain_id']}/swap",
                params=params,
            )

            if r_swap.status_code == 200:
                result = r_swap.json()

            else:
                raise BadResponseFormat("1inch api failed")

            result = r_swap.json()

        result = r_swap.json()

        result_tx = result["tx"]

        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        maxPriorityFeePerGas, maxFeePerGas = self.updateTxParameters()

        tx = {
            "from": accountAddress,
            "to": routerAddress,
            "value": int(result_tx["value"]),
            "maxPriorityFeePerGas": int(maxPriorityFeePerGas),
            "maxFeePerGas": int(maxFeePerGas),
            "data": result_tx["data"],
            "nonce": self.nonce,
            "chainId": self.chains["mainnet"]["chain_id"],
        }

        gas = self.w3.eth.estimate_gas(tx)

        tx["gas"] = gas

        return tx

        # arg_in = f"{amountA} {tokenA} {amountBMin} {tokenB} {self.privatekey}"
        # response = muterun_js('klayswap_swap.js', arg_in)
        # tx = response.stdout.decode("utf-8")

        # return tx

    def check_bridge_completed(self, tokenSymbol, toAddr):
        start_bridge = datetime.datetime.now()

        start_time = datetime.datetime.now()

        current_account = self.account

        self.account = toAddr

        start_balance = self.partial_balance(tokenSymbol)

        while True:
            current_time = datetime.datetime.now()

            current_balance = self.partial_balance(tokenSymbol)

            if (
                ((current_balance["balance"] - start_balance["balance"]) > (self.amount))
                or (current_balance["balance"] >= self.amount)
                or (current_time - start_time).seconds > 1800
            ):
                if current_balance["balance"] - start_balance["balance"] > 0:
                    amount = current_balance["balance"] - start_balance["balance"]

                else:
                    amount = self.amount

                break

        end_bridge = datetime.datetime.now()

        bridge_time = (end_bridge - start_bridge).seconds

        time_spend = {"bridge_time": bridge_time}

        self.account = current_account

        balance = self.from_value(amount, self.decimals(tokenSymbol))

        return time_spend, balance
