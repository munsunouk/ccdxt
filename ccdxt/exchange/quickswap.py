from ccdxt.base.exchange import Exchange
from ccdxt.base.errors import InsufficientBalance, InvalidToken
import datetime

class Quickswap(Exchange):
    
    has = {
        
        'createSwap': True,
        'fetchTicker': True,
        'fetchBalance': True,
        
    }
    
    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "polygon"
        self.exchangeName = "quickswap"
        
        self.load_exchange(self.chainName, self.exchangeName)
        
    def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol) :
        
        amountin = self.from_value(value = amountAin, exp = self.decimals(tokenAsymbol))
        
        pool = self.get_pair(tokenAsymbol, tokenBsymbol)
        
        reserve = self.get_reserves(pool, tokenAsymbol, tokenBsymbol)
        
        amountBout = self.get_amount_out(tokenAsymbol,amountin,tokenBsymbol)
        
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
    
    def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol) :
        
        tokenAbalance = self.partial_balance(tokenAsymbol)
        if amountA > tokenAbalance:
            raise InsufficientBalance(tokenAbalance, amountA)
        
        if tokenAsymbol == tokenBsymbol:
            raise ValueError
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value = amountA, exp = tokenA["decimal"])
        amountBMin = self.from_value(value = amountBMin, exp = tokenB["decimal"])
        
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
    
    def token_to_token(self, tokenAaddress, amountA, tokenBaddress, amountBMin)  :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        deadline = int(datetime.datetime.now().timestamp() + 1800)\
                                               
        tx = self.routerContract.functions.swapExactTokensForTokens(amountA,amountBMin,[tokenAaddress,tokenBaddress],self.account,deadline).transact(
                {
                    "from" : self.account,
                    'gas' : 3000000,
                    "nonce": nonce,
                }
            )                                      
        
        return tx
    
    def eth_to_token(self, tokenAaddress, tokenBaddress, amountBMin)  :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        deadline = int(datetime.datetime.now().timestamp() + 1800)\
                                               
        tx = self.routerContract.functions.swapETHForExactTokens(amountBMin, tokenBaddress, [tokenAaddress,tokenBaddress],self.account,deadline).transact(
                {
                    "from" : self.account,
                    "gasPrice" : self.w3.toHex(25000000000),
                    "nonce": nonce,
                }
            )                                      
        
        return tx

    def token_to_eth(self, tokenAaddress, amountA, tokenBaddress, amountBMin) :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        deadline = int(datetime.datetime.now().timestamp() + 1800)\
                                               
        tx = self.routerContract.functions.swapTokensForExactETH(amountA,amountBMin,[tokenAaddress,tokenBaddress],self.account,deadline).transact(
                {
                    "from" : self.account,
                    "gasPrice" : self.w3.toHex(25000000000),
                    "nonce": nonce,
                }
            )                                      
        
        return tx
    
    def get_amount_out(self,tokenAsymbol,amountIn,tokenBsymbol) :
        
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB['contract'])
        
        self.factoryContract = self.get_contract(routerAddress, self.markets['routerAbi'])
        
        amountOut = self.factoryContract.functions.getAmountsOut(amountIn, [tokenAaddress, tokenBaddress]).call()[-1]
        
        return amountOut
    
    def get_reserves(self, poolAddress, tokenAsymbol, tokenBsymbol):
        
        tokenA = self.tokens[tokenAsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        
        factoryContract = self.get_contract(poolAddress, self.markets['factoryAbi'])
        
        tokenA = factoryContract.functions.tokenA().call()
        
        routerContract = self.get_contract(poolAddress, self.markets['routerAbi'])
        reserves = routerContract.functions.getCurrentPool().call()
        
        if tokenA != tokenAaddress :
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenBsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenAsymbol))
        else:
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenAsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenBsymbol))
            
        reserve = reserves[1] / reserves[0]
        
        return reserve