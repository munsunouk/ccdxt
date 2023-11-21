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


class Oneinchswap(Exchange):
    has = {
        "createSwap": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "chainName": "KLAYTN",
            "exchangeName": "oneinchswap",
            "retries": 3,
            "retriesTime": 10,
            "host": 0,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
            "sleep": 10,
            "api_url": "https://api-defillama.1inch.io/"
            # url = f"https://api.1inch.io/"
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
        self.api_url = config["api_url"]
        self.sleep = config["sleep"]

        # self.load_exchange(self.chainName, self.exchangeName)
        self.set_logger(self.log)

    @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol, fusion=False):
        # time.sleep(self.sleep)

        await self.load_exchange(self.chainName, self.exchangeName)

        amountIn = self.from_value(value=amountAin, exp=await self.decimals(tokenAsymbol))

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = tokenA["contract"]
        tokenBaddress = tokenB["contract"]

        if tokenAaddress == self.chains["baseContract"]:
            tokenAaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        elif tokenBaddress == self.chains["baseContract"]:
            tokenBaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        if not fusion:
            params = {
                "fromTokenAddress": tokenAaddress,
                "toTokenAddress": tokenBaddress,
                "amount": amountIn,
            }

            if self.markets["version"] == 5.0:

                version = 5.2
                params["includeGas"] = "true"

            else:

                version = self.markets["version"]

            if self.proxy:
                quote_result = await self.create_request(
                    self.api_url,
                    params,
                    f"v{version}",
                    f"{self.chains['mainnet']['chain_id']}",
                    "quote",
                    proxy=self.proxy,
                )

            else:
                quote_result = await self.create_request(
                    self.api_url,
                    params,
                    f"v{version}",
                    f"{self.chains['mainnet']['chain_id']}",
                    "quote",
                )

            if version == 5.2:

                ask = "toAmount"
                gas = "gas"

            else:

                ask = "toTokenAmount"
                gas = "estimatedGas"

            amountout = self.to_value(
                value=quote_result[ask], exp=await self.decimals(tokenBsymbol)
            )

        else:
            # amountBout = auction end amount + 10% 테스트
            quote = await self.get_fusion_quote(amountIn, tokenAaddress, tokenBaddress)

            amountout = int(quote["presets"]["fast"]["auctionEndAmount"]) * 1.1

            amountout = self.to_value(amountout, exp=await self.decimals(tokenBsymbol))

        result = {
            "amountAin": amountAin,
            "amountBout": amountout,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
            "estimateGas": int(quote_result[gas]),
            "referrer": self.account,
        }

        return result

    @retry
    async def create_swap(
        self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs
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

        await self.load_exchange(self.chainName, self.exchangeName)

        if (path != None) and (len(path) > 2):
            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path[1:-1]]

        else:
            self.path = []

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA

        # self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        amountBMin = self.from_value(value=amountBMin, exp=int(tokenB["decimals"]))
        if tokenA["contract"] == self.chains["baseContract"]:
            tokenAaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            tokenAaddress = self.set_checksum(tokenAaddress)
            tokenBaddress = self.set_checksum(tokenB["contract"])

        elif tokenB["contract"] == self.chains["baseContract"]:
            tokenAaddress = self.set_checksum(tokenA["contract"])
            tokenBaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            tokenBaddress = self.set_checksum(tokenBaddress)

        else:
            tokenAaddress = self.set_checksum(tokenA["contract"])
            tokenBaddress = self.set_checksum(tokenB["contract"])

        tokenApprove = self.set_checksum(tokenA["contract"])

        self.account = self.set_checksum(self.account)

        if (self.chainName == "MATIC") & (tokenBsymbol == self.baseCurrency):

            self.markets["routerAddress"] = self.markets["alterRouterAddress"]
            self.markets["version"] = 4.0

        routerAddress = self.set_checksum(self.markets["routerAddress"])

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        build = {
            "from": self.account,
            "nonce": self.nonce,
        }

        if self.chainName == "KLAY":

            pass

        elif self.chainName == "MATIC":

            self.maxPriorityFee, self.maxFee = await self.updateTxParameters()

            build["maxPriorityFeePerGas"] = int(self.maxPriorityFee)
            build["maxFeePerGas"] = int(self.maxFee)

        await self.check_approve(
            amount=amountA,
            token=tokenApprove,
            account=self.account,
            router=routerAddress,
            build=build,
        )

        self.routerContract = await self.get_contract(
            routerAddress, self.markets["routerAbi"][int(self.markets["version"])]
        )

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        if "fusion" not in kwargs:
            tx = await self.token_to_token(
                tokenAaddress, amountA, tokenBaddress, self.account, routerAddress
            )

            tx_receipt = await self.fetch_transaction(tx, "SWAP")

        else:
            tx = await self.create_fusion_swap(amountA, tokenAaddress, tokenBaddress)

            time_spend, amount = await self.check_bridge_completed(tokenBsymbol, self.account)

            tx_receipt = await self.fetch_transaction(tx, "FUSION_SWAP")

            tx_receipt["amount_out"] = amount

        return tx_receipt

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

        if result.startswith("Error:"):
            raise BadResponseFormat("1inch SDK failed")

        else:
            result = json.loads(result)

        return result

    async def create_fusion_swap(self, amount, tokenA, tokenB):
        if self.privateKey.startswith("0x"):
            self.privateKey = self.privateKey[2:]

        else:
            pass

        basePath = Path(__file__).resolve().parent
        oneinchPath = os.path.join(basePath, "oneinchswap.js")

        js_code = f"""
        const {{ swap_js }} = require('{oneinchPath}');
        swap_js({amount}, '{tokenA}', '{tokenB}', '{self.account}', '{self.privateKey}', '{self.exchange_node}', '{self.chains['mainnet']['chain_id']}');
        """

        loop = asyncio.get_event_loop()
        quote_data = await loop.run_in_executor(
            None, subprocess.check_output, ["node", "-e", js_code]
        )

        result = quote_data.decode("utf-8")

        if result.startswith("Error:"):
            raise BadResponseFormat("1inch SDK failed")

        return result

    def get_proxy_list(self):
        pass

    async def token_to_token(
        self, tokenAaddress, amountA, tokenBaddress, accountAddress, routerAddress
    ):

        if (tokenAaddress == self.chains["baseContract"]) and (self.chainName == "KLAYTN"):
            tokenAaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        elif (tokenBaddress == self.chains["baseContract"]) and (self.chainName == "KLAYTN"):
            tokenBaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        version = self.markets["version"]

        if version == 5:

            params = {
                "src": tokenAaddress,
                "dst": tokenBaddress,
                "amount": amountA,
                "from": self.account,
                "slippage": 0.5,
                "referrer": self.account,
                "disableEstimate": "true",
            }

        else:

            params = {
                "fromTokenAddress": tokenAaddress,
                "toTokenAddress": tokenBaddress,
                "amount": amountA,
                "fromAddress": self.account,
                "slippage": 50,
                "referrer": self.account,
                "disableEstimate": "true",
            }

        if self.proxy:
            result_tx = await self.create_request(
                self.api_url,
                params,
                f"v{self.markets['version']}",
                f"{self.chains['mainnet']['chain_id']}",
                "swap",
                proxy=self.proxy,
            )

            result_tx = result_tx["tx"]

        else:
            result_tx = await self.create_request(
                self.api_url,
                params,
                f"v{self.markets['version']}",
                f"{self.chains['mainnet']['chain_id']}",
                "swap",
            )

            result_tx = result_tx["tx"]

        maxPriorityFeePerGas, maxFeePerGas = await self.updateTxParameters()

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

        tx["gas"] = await self.w3.eth.estimate_gas(tx)

        return tx

        # arg_in = f"{amountA} {tokenA} {amountBMin} {tokenB} {self.privatekey}"
        # response = muterun_js('klayswap_swap.js', arg_in)
        # tx = response.stdout.decode("utf-8")

        # return tx

    async def check_bridge_completed(self, tokenSymbol, toAddr):
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

        balance = self.from_value(amount, await self.decimals(tokenSymbol))

        return time_spend, balance
