from ccdxt.base.exchange import Exchange
import datetime

class Klayswap(Exchange):

    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "klaytn"
        self.exchangeName = "klayswap"
        
        self.load_exchange(self.chainName, self.exchangeName)
        
    def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol) :
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        amountin = self.from_value(value = amountAin, exp = self.decimals(tokenAsymbol))
        
        pool = self.get_pool(tokenAsymbol, tokenBsymbol)
        
        reserve = self.get_reserves(pool, tokenAsymbol, tokenBsymbol)
        
        slippage = self.get_slippage(reserve, amountAin)
        
        amountBout = self.get_estimatePos(pool,tokenAsymbol,amountin)
        
        amountBout = amountBout * slippage 
        
        amountout = self.to_value(value = amountBout, exp = self.decimals(tokenBsymbol))
        
        result = {
            
            "amountAin" : amountAin,
            "tokenAsymbol" : tokenAsymbol,
            "amountBout" : amountout,
            "tokenBsymbol" : tokenBsymbol,
            "slippage" : slippage
            
        }
        
        return result
    
    def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol) :
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value = amountA, exp = tokenA["decimal"])
        amountBMin = self.from_value(value = amountBMin, exp = tokenB["decimal"])
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        tokenAaddress = self.set_checksum(tokenA['contract'])
        tokenBaddress = self.set_checksum(tokenB['contract'])
        accountAddress = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        
        self.check_approve(amountA = amountA, token = tokenAaddress, \
                           account = accountAddress, router = routerAddress)
        
        self.routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])

        tx = self.routerContract.functions.exchangeKctPos(tokenAaddress, amountA, \
                                               tokenBaddress, amountBMin, []).buildTransaction(
            {
                "from" : self.account,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        tx_receipt = self.fetch_transaction(tx, tokenAaddress, tokenBaddress)
        
        tx_arrange = {
            
            'transaction_hash' : tx_receipt['transactionHash'].hex(),
            'status' : None,
            'block' :  tx_receipt['blockNumber'],
            'timestamp' : datetime.datetime.now(),
            'from' : tx_receipt['from'],
            'to' : tx_receipt['to'],
            'transaction_fee:' : tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18 ,
            
        }
           
        return tx_arrange
    
    def get_estimatePos(self,pool,tokenAsymbol,amountIn) :
        
        tokenA = self.tokens[tokenAsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        
        poolAddress = self.set_checksum(pool)
        
        self.routerContract = self.get_contract(poolAddress, self.markets['factoryAbi'])
        
        amountOut = self.routerContract.functions.estimatePos(tokenAaddress,amountIn).call()
        
        return amountOut
    
    def get_reserves(self, poolAddress, tokenAsymbol, tokenBsymbol):
        
        tokenA = self.tokens[tokenAsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        
        factoryContract = self.get_contract(poolAddress, self.markets['factoryAbi'])
        
        tokenA = factoryContract.functions.tokenA().call()
        
        routerContract = self.get_contract(poolAddress, self.markets['routerAbi'])
        reserves = routerContract.functions.getCurrentPool().call()
        
        print(tokenA)
        print(tokenAaddress)
        
        if tokenA != tokenAaddress :
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenBsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenAsymbol))
        else:
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenAsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenBsymbol))
        
        return reserves
    
    def get_slippage(self, reserve, amount) :
        
        slippage = round(amount * 100 / reserve[0],6)
        
        return slippage