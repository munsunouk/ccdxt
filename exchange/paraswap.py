from ..base.exchange import Exchange
from ..base.utils.errors import (
    InsufficientBalance,
)

from ..base.utils.retry import retry
from typing import Optional
from web3.exceptions import BadResponseFormat

import requests
from requests.exceptions import HTTPError, ReadTimeout, ProxyError, SSLError, ConnectTimeout
from random import choice

# from proxy_requests.proxy_requests import ProxyRequests
import logging
import time
import os
from pathlib import Path
import asyncio
import datetime
from enum import Enum


class Paraswap(Exchange):
    has = {
        "createSwap": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "chainName": "MATIC",
            "exchangeName": "paraswap",
            "retries": 3,
            "retriesTime": 10,
            "host": None,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
            "api_url": "https://apiv5.paraswap.io/",
            "sleep": 10,
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

        self.load_exchange(self.chainName, self.exchangeName)
        self.set_logger(self.log)

    @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol, **kwargs):
        await asyncio.sleep(self.sleep)

        amountIn = amountAin

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = tokenA["contract"]
        tokenBaddress = tokenB["contract"]

        amountA = self.from_value(value=amountAin, exp=int(tokenA["decimals"]))

        if tokenA["contract"] == self.chains["baseContract"]:
            tokenAaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        elif tokenB["contract"] == self.chains["baseContract"]:
            tokenBaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        # params1 = {
        #     "srcToken": tokenAaddress,
        # }

        # params2 = {
        #     "destToken":tokenBaddress,
        #     "amount": amountA,
        #     "srcDecimals": int(tokenA["decimals"]),
        #     "destDecimals" : int(tokenB["decimals"]),
        #     "partner" : "llamaswap",
        #     "side" : "SELL",
        #     "network" : self.chains['mainnet']['chain_id'],
        #     "excludeDEXS" : "ParaSwapPool,ParaSwapLimitOrders"

        # }

        # site_config = [("?", params1), ("&", params2)]

        # full_site = self.create_reuqest_detail(self.api_url + 'prices/', site_config)

        # quote_result = self.create_request(full_site)["priceRoute"]

        params = {
            "srcToken": tokenAaddress,
            "destToken": tokenBaddress,
            "amount": amountA,
            "srcDecimals": int(tokenA["decimals"]),
            "destDecimals": int(tokenB["decimals"]),
            "partner": "llamaswap",
            "side": "SELL",
            "network": self.chains["mainnet"]["chain_id"],
            "excludeDEXS": "ParaSwapPool,ParaSwapLimitOrders",
        }

        if self.proxy:
            quote_result = self.create_request(self.api_url, params, "prices", proxy=self.proxy)

        else:
            quote_result = self.create_request(self.api_url, params, "prices")

        amountout = self.to_value(
            value=quote_result["priceRoute"]["destAmount"], exp=self.decimals(tokenBsymbol)
        )

        result = {
            "amountAin": amountAin,
            "amountBout": amountout,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
            "estimateGas": int(quote_result["priceRoute"]["gasCost"]),
            "quote_result": quote_result,
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

        await asyncio.sleep(self.retriesTime)

        if (path != None) and (len(path) > 2):
            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path[1:-1]]

        else:
            self.path = []

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA

        tokenBalance = self.partial_balance(self.tokenSymbol)
        baseCurrency = self.partial_balance(self.chains["baseCurrency"])

        self.require(
            self.amount > tokenBalance["balance"],
            InsufficientBalance(tokenBalance, f"need :{self.amount}"),
        )
        self.require(1 > baseCurrency["balance"], InsufficientBalance(baseCurrency, f"need : 1"))
        # self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        amountBMin = self.from_value(value=amountBMin, exp=int(tokenB["decimals"]))

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])

        if tokenA["contract"] == self.chains["baseContract"]:
            tokenAaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            tokenAaddress = self.set_checksum(tokenAaddress)

        elif tokenB["contract"] == self.chains["baseContract"]:
            tokenBaddress = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            tokenBaddress = self.set_checksum(tokenBaddress)

        tokenApprove = self.set_checksum(tokenA["contract"])
        accountAddress = self.set_checksum(self.account)

        routerAddress = self.set_checksum(self.markets["routerAddress"])
        tokenTransferAddress = self.set_checksum(self.markets["tokenTransferAddress"])

        self.check_approve(
            amount=amountA, token=tokenApprove, account=accountAddress, router=tokenTransferAddress
        )

        self.routerContract = self.get_contract(
            routerAddress, self.markets["routerAbi"][int(self.markets["version"])]
        )

        if kwargs:
            if "priceRoute" in kwargs:
                priceRoute = kwargs["priceRoute"]

            else:
                raise ValueError("need priceRoute")

            if "slippage" in kwargs:
                slippage = kwargs["slippage"]

            else:
                slippage = 50

        else:
            raise ValueError("need priceRoute")

        tx = self.token_to_token(
            amountA,
            tokenA,
            tokenAaddress,
            tokenB,
            tokenBaddress,
            accountAddress,
            routerAddress,
            slippage,
            priceRoute,
        )

        tx_receipt = self.fetch_transaction(tx, "SWAP")

        return tx_receipt

    def get_proxy_list(self):
        pass

    def create_tx(self, accountAddress, routerAddress, quote_tx):
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        if self.chainName == "MATIC":
            maxPriorityFeePerGas, maxFeePerGas = self.updateTxParameters()

            tx = {
                "from": accountAddress,
                "to": routerAddress,
                "value": int(quote_tx["value"]),
                "maxPriorityFeePerGas": int(maxPriorityFeePerGas),
                "maxFeePerGas": int(maxFeePerGas),
                "data": quote_tx["data"],
                "nonce": self.nonce,
                "chainId": self.chains["mainnet"]["chain_id"],
            }

            gas = self.w3.eth.estimate_gas(tx)
            tx["gas"] = gas

        else:
            gasPrice = self.get_gasPrice()

            tx = {
                "from": accountAddress,
                "to": routerAddress,
                "value": int(quote_tx["value"]),
                "gasPrice": gasPrice,
                "data": quote_tx["data"],
                "nonce": self.nonce,
                "chainId": self.chains["mainnet"]["chain_id"],
                "gas": int(quote_tx["estimatedGas"]),
            }

        return tx

    def token_to_token(
        self,
        amountA,
        tokenA,
        tokenAaddress,
        tokenB,
        tokenBaddress,
        accountAddress,
        routerAddress,
        slippage,
        priceRoute,
    ):
        params = {
            "srcToken": tokenAaddress,
            "srcAmount": amountA,
            "srcDecimals": int(tokenA["decimals"]),
            "destToken": tokenBaddress,
            "destDecimals": int(tokenB["decimals"]),
            "slippage": slippage,
            "userAddress": self.account,
            "partner": "llamaswap",
            "positiveSlippageToUser": False,
            "priceRoute": priceRoute,
        }

        if self.proxy:
            quote_tx = self.create_request(
                self.api_url,
                params,
                "transactions",
                f"{self.chains['mainnet']['chain_id']}",
                request_method="post",
                proxy=self.proxy,
            )

        else:
            quote_tx = self.create_request(
                self.api_url,
                params,
                "transactions",
                f"{self.chains['mainnet']['chain_id']}",
                request_method="post",
            )

        tx = self.create_tx(accountAddress, routerAddress, quote_tx)

        return tx

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

    def get_gasPrice(self):
        r = requests.get(
            f"https://api.paraswap.io/prices/gas/{self.chains['mainnet']['chain_id']}?eip1559=false"
        )

        if r.status_code == 200:
            gas = r.json()

        else:
            raise BadResponseFormat(f"openocean api failed : {r.text}")

        fast_gas = gas["fast"]

        return int(fast_gas)

    def get_transaction(self, tx_hash):
        r = requests.get(
            f"https://open-api.openocean.finance/v3/{self.chains['baseChain']}/getTransaction?hash={tx_hash}"
        )

        if r.status_code == 200:
            raw_receipt = r.json()

        else:
            raise BadResponseFormat(f"openocean api failed : {r.text}")

        txDict = {
            "from_network": self.chains["name"],
            "to_network": self.chains["name"],
            "tx_hash": raw_receipt["data"]["tx_hash"],
            "status": 3,  # pending
            "block": raw_receipt["data"]["block_number"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": None,
            "from_address": None,
            "amount_in": raw_receipt["data"]["in_amount_value"],
            "token_in": self.tokenSymbol,
            "to_address": None,
            "amount_out": raw_receipt["data"]["out_amount_value"],
            "token_out": self.tokenBsymbol,
            "gas_fee": raw_receipt["data"]["tx_fee"],
            "tx_scope": None,
        }

        return txDict
