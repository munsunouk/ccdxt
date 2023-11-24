from ..base.exchange import Exchange
from ..base.utils.errors import (
    InsufficientBalance,
)
from ..base.utils.retry import retry

from typing import Optional
import datetime

# from pytz import timezone
import time

from web3 import Web3


class Meshswap(Exchange):
    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "retries": 3,
            "retriesTime": 10,
            "host": 0,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
        }

        config.update(config_change)

        # market info
        self.id = 2
        self.chainName = "MATIC"
        self.exchangeName = "meshswap"
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.proxy = config["proxy"]

        # self.load_exchange(self.chainName, self.exchangeName)
        self.set_logger(self.log)

    # @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol):

        result = {
            "amountAin": amountAin,
            "amountBout": 0,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
        }

        await self.load_exchange(self.chainName, self.exchangeName)

        pool = await self.get_pair(tokenAsymbol, tokenBsymbol)

        pool = self.set_checksum(pool)

        await self.sync(pool)

        amountin = self.from_value(value=amountAin, exp=await self.decimals(tokenAsymbol))

        amountBout = await self.get_amount_out(tokenAsymbol, amountin, tokenBsymbol)

        amountout = self.to_value(value=amountBout, exp=await self.decimals(tokenBsymbol))

        result["amountBout"] = amountout

        return result

    @retry
    async def create_swap(
        self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs
    ):

        await self.load_exchange(self.chainName, self.exchangeName)

        self.baseCurrency = self.chains["baseCurrency"]

        self.pathName = path

        # self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        amountA = self.from_value(value=amountA, exp=await self.decimals(tokenAsymbol))
        # amountBMin = self.from_value(value=amountBMin, exp=await self.decimals(tokenBsymbol))

        amountBMin = 1

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])

        if path != None:
            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path]

        else:
            self.path = [tokenAaddress, tokenBaddress]

        self.maxPriorityFee, self.maxFee = await self.updateTxParameters()
        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        build = {
            "from": self.account,
            "maxPriorityFeePerGas": int(self.maxPriorityFee),
            "maxFeePerGas": int(self.maxFee),
            "nonce": self.nonce,
            "value": 0,
        }

        await self.check_approve(
            amount=amountA,
            token=tokenAaddress,
            account=self.account,
            router=routerAddress,
            build=build,
        )

        self.routerContract = await self.get_contract(routerAddress, self.markets["routerAbi"])

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        build["nonce"] = self.nonce

        self.deadline = int(datetime.datetime.now().timestamp() + 1800)

        if tokenAsymbol == self.baseCurrency:
            tx = await self.eth_to_token(amountA, amountBMin, build)
        elif tokenBsymbol == self.baseCurrency:
            tx = await self.token_to_eth(amountA, amountBMin, build)
        else:
            tx = await self.token_to_token(amountA, amountBMin, build)

        tx_receipt = await self.fetch_transaction(tx, "SWAP")

        return tx_receipt

    async def token_to_token(self, amountA, amountBMin, build):

        tx = await self.routerContract.functions.swapExactTokensForTokens(
            amountA, amountBMin, self.path, self.account, self.deadline
        ).build_transaction(build)

        return tx

    async def eth_to_token(self, amountA, amountBMin, build):

        build["value"] = amountA

        tx = await self.routerContract.functions.swapExactETHForTokens(
            amountBMin, self.path, self.account, self.deadline
        ).build_transaction(build)

        return tx

    async def token_to_eth(self, amountA, amountBMin, build):
        tx = await self.routerContract.functions.swapExactTokensForETH(
            amountA, amountBMin, self.path, self.account, self.deadline
        ).build_transaction(build)

        return tx

    async def get_amount_out(self, tokenAsymbol, amountIn, tokenBsymbol):
        routerAddress = self.set_checksum(self.markets["routerAddress"])

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])

        self.routerContract = await self.get_contract(routerAddress, self.markets["routerAbi"])

        amountOut = await self.routerContract.functions.getAmountsOut(
            amountIn, [tokenAaddress, tokenBaddress]
        ).call()

        amountOut = amountOut[-1]

        return amountOut

    async def get_reserves(self, tokenAsymbol, tokenBsymbol):
        pool = self.get_pair(tokenAsymbol, tokenBsymbol)

        pool = self.set_checksum(pool)

        tokenA = self.tokens[tokenAsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])

        routerContract = await self.get_contract(pool, self.markets["routerAbi"])

        tokenA = await routerContract.functions.token0().call()

        reserves = await routerContract.functions.getReserves().call()

        if tokenA != tokenAaddress:
            reserves[1] = self.to_value(reserves[0], await self.decimals(tokenBsymbol))
            reserves[0] = self.to_value(reserves[1], await self.decimals(tokenAsymbol))

        else:
            reserves[0] = self.to_value(reserves[0], await self.decimals(tokenAsymbol))
            reserves[1] = self.to_value(reserves[1], await self.decimals(tokenBsymbol))

        reserve = reserves[0] / reserves[1]

        return {
            "pool": f"{tokenBsymbol}-{tokenAsymbol}",
            "tokenAsymbol": tokenBsymbol,
            "tokenBsymbol": tokenAsymbol,
            "tokenAreserves": reserves[1],
            "tokenBreserves": reserves[0],
            "poolPrice": reserve,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
