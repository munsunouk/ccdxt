from mars.base.exchange import Exchange
from mars.base.utils.errors import (
    InsufficientBalance,
)
from mars.base.utils.retry import retry

import datetime
# from pytz import timezone
from typing import Optional
import time

class Mooiswap(Exchange):
    def __init__(self, config_change: Optional[dict] = {}):

        super().__init__()
        
        config = {
            "retries" : 3,
            "retriesTime" : 10,
            "host" : None,
            "account" : None,
            "privateKey" : None,
            "log" : None,
            "proxy" : None,
        }
        
        config.update(config_change)

        # market info
        self.id = 2
        self.chainName = "MOOI"
        self.exchangeName = "mooiswap"
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

    @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol):

        amountin = self.from_value(value=amountAin, exp=self.decimals(tokenAsymbol))

        pool = self.get_pair(tokenAsymbol, tokenBsymbol)

        pool = self.set_checksum(pool)

        amountBout = self.get_amount_out(tokenAsymbol, amountin, tokenBsymbol)

        amountout = self.to_value(value=amountBout, exp=self.decimals(tokenBsymbol))

        result = {
            "amountAin": amountAin,
            "amountBout": amountout,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
        }

        return result
    @retry
    async def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs):

        self.baseCurrency = 'wMOOI'

        self.pathName = path
        
        if 'round' in kwargs :
            
            return self.base_txDict()

        self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))
        
        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        
        if tokenAsymbol == 'wMOOI' :
            
            self.tokenSymbol = 'MOOI'
            
        elif tokenBsymbol == 'wMOOI' :
            
            self.tokenBsymbol = 'MOOI'
            
        if tokenAsymbol == 'MOOI' :
            
            tokenAsymbol = 'wMOOI'
            
        elif tokenBsymbol == 'MOOI' :
            
            tokenBsymbol = 'wMOOI'

        self.amount = amountA
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        amountA = self.from_value(value=amountA, exp=self.decimals(tokenAsymbol))
        amountBMin = self.from_value(value=amountBMin, exp=self.decimals(tokenBsymbol))

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])

        if path:

            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path]

        else:

            self.path = [tokenAaddress, tokenBaddress]

        self.check_approve(
            amount=amountA, token=tokenAaddress, account=self.account, router=routerAddress
        )

        self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"])

        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        self.deadline = int(datetime.datetime.now().timestamp() + 1800)
        self.gasPrice = self.w3.toHex(25000000000)
        
        
        print("tokenAaddress", tokenAaddress)
        print("tokenB", tokenB)
        print("tokenBaddress", tokenBaddress)
        print("routerAddress", routerAddress)

        if tokenAsymbol == self.baseCurrency:
            tx = self.eth_to_token(amountA, tokenBaddress, amountBMin)
        elif tokenBsymbol == self.baseCurrency:
            tx = self.token_to_eth(tokenAaddress, amountA, amountBMin)
        else:
            tx = self.token_to_token(tokenAaddress, amountA, tokenBaddress, amountBMin)

        tx_receipt = self.fetch_transaction(tx, "SWAP")

        return tx_receipt

    def token_to_token(self, tokenAaddress, amountA, tokenBaddress, amountBMin):

        # maxPriorityFee, maxFee = self.updateTxParameters()
        # self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

        tx = self.routerContract.functions.swapExactTokensForTokens(
            amountA, amountBMin, self.path, self.account, self.deadline
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
                "gasPrice" : self.gasPrice
            }
        )

        return tx

    def eth_to_token(self, amountA, tokenBaddress, amountBMin):

        # raise ValueError(amountA, self.account, self.gasPrice, self.path, self.account, self.deadline)

        tx = self.routerContract.functions.swapExactETHForTokens(
            amountBMin, self.path, self.account, self.deadline
        ).build_transaction(
            {
                "from": self.account,
                "gasPrice" : self.gasPrice,
                "nonce": self.nonce,
                "value": amountA,
            }
        )

        return tx

    def token_to_eth(self, tokenAaddress, amountA, amountBMin):

        tx = self.routerContract.functions.swapExactTokensForETH(
            amountA, amountBMin, self.path, self.account, self.deadline
        ).build_transaction(
            {
                "from": self.account,
                "gasPrice" : self.gasPrice,
                "nonce": self.nonce,
            }
        )

        return tx

    def get_amount_out(self, tokenAsymbol, amountIn, tokenBsymbol):

        routerAddress = self.set_checksum(self.markets["routerAddress"])

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])

        self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"])

        amountOut = self.routerContract.functions.getAmountsOut(
            amountIn, [tokenAaddress, tokenBaddress]
        ).call()[-1]

        return amountOut

    async def get_reserves(self, tokenAsymbol, tokenBsymbol):
        
        pool = self.get_pair(tokenAsymbol, tokenBsymbol)

        pool = self.set_checksum(pool)

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])

        routerContract = self.get_contract(pool, self.markets["routerAbi"])

        tokenA = routerContract.functions.token0().call()

        reserves = routerContract.functions.getReserves().call()

        if tokenA != tokenAaddress:
            reservesA = self.to_value(reserves[1], self.decimals(tokenAsymbol))
            reservesB = self.to_value(reserves[0], self.decimals(tokenBsymbol))

        else:
            reservesA = self.to_value(reserves[0], self.decimals(tokenAsymbol))
            reservesB = self.to_value(reserves[1], self.decimals(tokenBsymbol))

        reserve = reservesB / reservesA

        return {
            "pool" : f"{tokenAsymbol}-{tokenBsymbol}",
            "tokenAsymbol" : tokenAsymbol,
            "tokenBsymbol" : tokenBsymbol,
            "tokenAreserves" : reservesA,
            "tokenBreserves" : reservesB,
            "poolPrice" : reserve,
            'created_at' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
