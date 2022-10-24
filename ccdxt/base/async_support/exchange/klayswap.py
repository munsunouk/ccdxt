import ccdxt

from ccdxt.base.async_support.base.exchange import Exchange
from ccdxt.base.utils.errors import InsufficientBalance
import datetime

class Klayswap(Exchange):
    
    has = {
        
        'createSwap': True,
        'fetchTicker': True,
        'fetchBalance': True,
        
    }

    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "KLAYTN"
        self.exchangeName = "klayswap"
        
        self.load_exchange(self.chainName, self.exchangeName)
        
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol) :
        
        amountin = self.from_value(value = amountAin, exp = self.decimals(tokenAsymbol))
        
        pool = await self.get_pool(tokenAsymbol, tokenBsymbol)
        
        pool = self.set_checksum(pool)    
        
        reserve = await self.get_reserves(pool, tokenAsymbol, tokenBsymbol)
        
        amountBout = await self.get_amount_out(pool,tokenAsymbol,amountin)
        
        price_amount = amountBout / amountin
        
        price_value = amountBout / self.to_value(value = amountin, exp = self.decimals(tokenAsymbol))
        
        price_amount = self.to_value(value = price_value, exp = self.decimals(tokenBsymbol))
        
        price_impact = float((reserve - price_amount) / reserve)

        amountBlose = amountBout * price_impact
        
        amountB = amountBout - amountBlose
        
        amountout = self.to_value(value = amountB, exp = self.decimals(tokenBsymbol))
        
        result = {
            
            "amountAin" : amountAin,
            "tokenAsymbol" : tokenAsymbol,
            "amountBout" : amountout,
            "tokenBsymbol" : tokenBsymbol,
            
        }
        
        return result 
    
    async def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol) :
        '''
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
        '''
        
        tokenAbalance = await self.partial_balance(tokenAsymbol)
        
        self.tokenAsymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.require(amountA > tokenAbalance['balance'], InsufficientBalance(tokenAbalance, amountA))
        self.require(tokenAsymbol == tokenBsymbol, ValueError)

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value = amountA, exp = int(tokenA["decimals"]))
        amountBMin = self.from_value(value = amountBMin, exp = int(tokenB["decimals"]))
        
        tokenAaddress = self.set_checksum(tokenA['contract'])
        tokenBaddress = self.set_checksum(tokenB['contract'])
        accountAddress = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        
        self.check_approve(amountA = amountA, token = tokenAaddress, \
                           account = accountAddress, router = routerAddress)
        
        self.routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])

        if tokenAsymbol == self.baseCurrncy:
            tx = self.eth_to_token(tokenBaddress, amountBMin)
        elif tokenBsymbol == self.baseCurrncy:
            tx = self.token_to_eth(tokenAaddress, amountA)
        else:
            tx = self.token_to_token(tokenAaddress, amountA, tokenBaddress, amountBMin)

        tx_receipt = self.fetch_transaction(tx, 'SWAP')
           
        return tx_receipt
    
    def token_to_token(self, tokenAaddress, amountA, tokenBaddress, amountBMin)  :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        tx = self.routerContract.functions.exchangeKctPos(tokenAaddress, amountA, \
                                               tokenBaddress, amountBMin, []).buildTransaction(
            {
                "from" : self.account,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        
        return tx
    
    def eth_to_token(self, tokenBaddress, amountBMin)  :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        tx = self.routerContract.functions.exchangeKctPos(
                                               tokenBaddress, amountBMin, []).buildTransaction(
            {
                "from" : self.account,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        
        return tx
    
    def token_to_eth(self, tokenAaddress, amountA) :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        tx = self.routerContract.functions.exchangeKlayNeg(
                                                tokenAaddress, amountA, []).buildTransaction(
            {
                "from" : self.account,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        
        return tx
    
    async def get_amount_out(self,pool,tokenAsymbol,amountIn) :
        
        tokenA = self.tokens[tokenAsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        
        poolAddress = self.set_checksum(pool)
        
        self.factoryContract = await self.get_contract(poolAddress, self.markets['factoryAbi'])
        
        amountOut = await self.factoryContract.functions.estimatePos(tokenAaddress,amountIn).call()
        
        return amountOut
    
    async def get_reserves(self, poolAddress, tokenAsymbol, tokenBsymbol):
        
        tokenA = self.tokens[tokenAsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        
        factoryContract = await self.get_contract(poolAddress, self.markets['factoryAbi'])
        
        tokenA = await factoryContract.functions.tokenA().call()
        
        routerContract = await self.get_contract(poolAddress, self.markets['routerAbi'])
        reserves = await routerContract.functions.getCurrentPool().call()
        
        if tokenA != tokenAaddress :
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenBsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenAsymbol))
            
            reserve = reserves[0] / reserves[1]
            
        else:
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenAsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenBsymbol))
            
            reserve = reserves[1] / reserves[0]
        
        return reserve