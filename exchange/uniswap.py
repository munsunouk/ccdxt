from mars.base.exchange import Exchange
from mars.base.utils.errors import (
    InsufficientBalance,
)
from mars.base.utils.retry import retry
from mars.base.utils import SafeMath 
from mars.base.utils.constants import MAX_UINT_128

from typing import Optional
import datetime
# from pytz import timezone
import time


class Uniswap(Exchange):
    def __init__(self, config_change: Optional[dict] = {}):

        super().__init__()
        
        config = {
            "retries" : 3,
            "retriesTime" : 10,
            "host" : None,
            "account" : None,
            "privateKey" : None,
            "log" : None,
            "proxy" : False
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

    def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs):

        self.baseCurrency = self.chains["baseCurrency"]

        self.pathName = path

        self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        amountA = self.from_value(value=amountA, exp=self.decimals(tokenAsymbol))
        amountBMin = self.from_value(value=amountBMin, exp=self.decimals(tokenBsymbol))

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])

        if path != None:

            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path]

        else:

            self.path = [tokenAaddress, tokenBaddress]

        self.check_approve(
            amount=amountA, token=tokenAaddress, account=self.account, router=routerAddress
        )

        self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"])

        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        self.deadline = int(datetime.datetime.now().timestamp() + 1800)

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
                # "gasPrice": self.w3.toHex(gasprice),
                # 'gas': 250000,
                # "maxPriorityFeePerGas": self.w3.toWei(maxPriorityFee, "gwei"),
                # "maxFeePerGas": self.w3.toWei(maxFee, "gwei"),
                "nonce": self.nonce,
            }
        )

        return tx

    def eth_to_token(self, amountA, tokenBaddress, amountBMin):

        tx = self.routerContract.functions.swapExactETHForTokens(
            amountBMin, self.path, self.account, self.deadline
        ).build_transaction(
            {
                "from": self.account,
                # "gasPrice" : self.w3.toHex(25000000000),
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
                # "gasPrice" : self.w3.toHex(25000000000),
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

        tokenAaddress = self.set_checksum(tokenA["contract"])

        routerContract = self.get_contract(pool, self.markets["routerAbi"])

        tokenA = routerContract.functions.token0().call()

        reserves = routerContract.functions.getReserves().call()

        if tokenA != tokenAaddress:
            reserves[1] = self.to_value(reserves[0], self.decimals(tokenBsymbol))
            reserves[0] = self.to_value(reserves[1], self.decimals(tokenAsymbol))

        else:
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenAsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenBsymbol))

        reserve = reserves[0] / reserves[1]

        return {
            "pool" : f"{tokenBsymbol}-{tokenAsymbol}",
            "tokenAsymbol" : tokenBsymbol,
            "tokenBsymbol" : tokenAsymbol,
            "tokenAreserves" : reserves[1],
            "tokenBreserves" : reserves[0],
            "poolPrice" : reserve,
            'created_at' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @retry
    async def add_liquidity(
            self,
            tokenAsymbol,
            tokenBsymbol,
            amountA,
            amountB,
            amountSlippage,
            priceSlippage,
            number_bins,
            fee: int = 3_000,
            *args, **kwargs
        ):
        """
        add liquidity to pool and mint position nft
        """
        
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))
        
        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA_value
        self.input = {
            "tokenAsymbol" : tokenAsymbol,
            "tokenBsymbol" : tokenBsymbol,
            "amountA" : amountA_value,
            "amountB" : amountB_value,
            "amountSlippage" : amountSlippage,
            "priceSlippage" : priceSlippage,
            "number_bins" : number_bins,
        }
        
        self.pool_name = f"{tokenAsymbol}-{tokenBsymbol}"
        
        self.require(f"{self.pool_name}" not in self.pools, ValueError("can`t find any available pairs in mars"))
        
        pool = self.pools[f"{self.pool_name}"]

        if "isV3" in pool :
            
            isV3 = pool['isV3']
            
        else :
            
            isV3 = False
            
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA_value = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        amountB_value = self.from_value(value=amountB, exp=int(tokenB["decimals"]))
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        factoryAddress = self.set_checksum(self.markets["factoryAddress"][int(isV3)])
        self.poolAddress = self.set_checksum(pool["poolAddress"])
        routerAddress = self.set_checksum(self.markets["routerAddress"][int(isV3)])
        nonFungiblePositionManagerAddress = self.set_checksum(self.markets["nonFungiblePositionManagerAddress"][int(isV3)])
        
        self.factoryContract = self.get_contract(factoryAddress, self.markets["factoryAbi"][int(isV3)])
        self.poolContract = self.get_contract(self.poolAddress, self.markets["poolAbi"][int(isV3)])
        self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"][int(isV3)])
        self.nft_managerContract = self.get_contract(nonFungiblePositionManagerAddress, self.markets["nonFungiblePositionManager"][int(isV3)])
        
        tokenAalance = self.partial_balance(tokenAsymbol)
        tokenBalance = self.partial_balance(tokenBsymbol)
        
        self.require(amountA > tokenAalance["balance"], InsufficientBalance(tokenAalance, f"need :{amountA}"))
        self.require(amountB > tokenBalance["balance"], InsufficientBalance(tokenBalance, f"need :{amountB}"))
        
        token_0 = self.poolContract.functions.token0().call()
        token_1 = self.poolContract.functions.token1().call()
        
        fee = self.poolContract.functions.fee().call()
        tick_lower = SafeMath.nearest_tick(tick_lower, fee)
        tick_upper = SafeMath.nearest_tick(tick_upper, fee)
        
        self.require(tick_lower < tick_upper, ValueError("Invalid tick range"))
        self.require(not self.fetch_available_LBPairs(), ValueError("can`t find any available pairs"))
        
        self.check_approve(
            amount=amountA, token=tokenAaddress, account=self.account, router=nonFungiblePositionManagerAddress
        )

        self.check_approve(
            amount=amountB, token=tokenBaddress, account=self.account, router=nonFungiblePositionManagerAddress
        )

        amountAMin = int(round(amountA_value * (1 - amountSlippage / 100)))
        amountBMin = int(round(amountB_value * (1 - amountSlippage / 100)))
        
        deadline = int(datetime.datetime.now().timestamp() + 1800)

        payload = {
            "token0" : token_0,
            "token1" : token_1,
            "fee" : fee,
            "tickLower" : tick_lower,
            "tickUpper" : tick_upper,
            "amount0Desired" : amountA_value,
            "amount1Desired" : amountB_value,
            "amount0Min" : amountAMin,
            "amount1Min" : amountBMin,
            "recipient" : self.account,
            "deadline" : deadline
        }

        self.token_with_token(payload)
        
        tx = self.token_with_token(payload)
        
        tx_receipt = self.fetch_transaction(tx, "ADD", payload=payload)
        
        return tx_receipt
    
    @retry
    async def remove_liquidity(
            self,
            tokenAsymbol,
            tokenBsymbol,
            amountSlippage,
            *args, **kwargs
        ):
        """
        add liquidity to pool and mint position nft
        """
        
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))
        
        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.input = {
            "tokenAsymbol" : tokenAsymbol,
            "tokenBsymbol" : tokenBsymbol,
            "amountSlippage" : amountSlippage
        }
        
        self.pool_name = f"{tokenAsymbol}-{tokenBsymbol}"
        
        self.require(f"{self.pool_name}" not in self.pools, ValueError("can`t find any available pairs in mars"))
        
        pool = self.pools[f"{self.pool_name}"]

        if "isV3" in pool :
            
            isV3 = pool['isV3']
            
        else :
            
            isV3 = False
            
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        factoryAddress = self.set_checksum(self.markets["factoryAddress"][int(isV3)])
        self.poolAddress = self.set_checksum(pool["poolAddress"])
        routerAddress = self.set_checksum(self.markets["routerAddress"][int(isV3)])
        nonFungiblePositionManagerAddress = self.set_checksum(self.markets["nonFungiblePositionManagerAddress"][int(isV3)])
        
        self.factoryContract = self.get_contract(factoryAddress, self.markets["factoryAbi"][int(isV3)])
        self.poolContract = self.get_contract(self.poolAddress, self.markets["poolAbi"][int(isV3)])
        self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"][int(isV3)])
        self.nft_managerContract = self.get_contract(nonFungiblePositionManagerAddress, self.markets["nonFungiblePositionManager"][int(isV3)])
        
        position = self.nonFungiblePositionManager.functions.positions(pool['tokenId']).call()

        self.require(not position, ValueError("can`t find any available pairs"))
        
        amountAMin = 0
        amountBMin = 0
        
        deadline = int(datetime.datetime.now().timestamp() + 1800)
        
        tx = self.decrease_liquidity(self, pool['tokenId'], position, amountAMin, amountBMin, deadline)
        
        tx_receipt = self.fetch_transaction(tx, "REMOVE")
        
        tx = self.collect_token_id(pool['tokenId'])
        
        tx_receipt = self.fetch_transaction(tx, "REMOVE")
        
        tx = self.burn(pool['tokenId'])
        
        tx_receipt = self.fetch_transaction(tx, "REMOVE")
        
        
        return tx_receipt
    
    def fetch_available_LBPairs(self):
        
        return self.poolContract.functions.slot0().call()
    
    def token_with_token(self, payload):

        tx = self.nft_managerContract.functions.mint(
            payload
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )
    
        return tx
    
    def collect_token_id(self, tokenId) :
        
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce
        
        tx = self.nft_managerContract.functions.collect(
            (tokenId, self.account), MAX_UINT_128, MAX_UINT_128
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )
    
        return tx
    
    def decrease_liquidity(self, tokenId, position, amount0Min, amount1Min, deadline) :
        
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce
        
        tx = self.nft_managerContract.functions.decreaseLiquidity(
            (tokenId, position[7], amount0Min, amount1Min, deadline)
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )
    
        return tx
    
    def burn(self, tokenId) :
        
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce
        
        tx = self.nft_managerContract.functions.burn(
            tokenId
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )
    
        return tx