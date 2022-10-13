from ccdxt.base.exchange import Exchange
import datetime
from ccdxt.base.utils.errors import InsufficientBalance
class Meshswap(Exchange):

    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "MATIC"
        self.exchangeName = "meshswap"
        
        self.load_exchange(self.chainName, self.exchangeName)
    
    def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol) :
        
        amountin = self.from_value(value = amountAin, exp = self.decimals(tokenAsymbol))
        
        pool = self.get_pair(tokenAsymbol, tokenBsymbol)
        
        pool = self.set_checksum(pool)
        
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
        
        self.require(amountA > tokenAbalance['balance'], InsufficientBalance(tokenAbalance, amountA))
        self.require(tokenAsymbol == tokenBsymbol, ValueError)
        
        self.tokenAsymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        amountA = self.from_value(value = amountA, exp = self.decimals(tokenAsymbol))
        amountBMin = self.from_value(value = amountBMin, exp = self.decimals(tokenBsymbol))
        
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
        deadline = int(datetime.datetime.now().timestamp() + 1800)

        tx = self.routerContract.functions.swapExactTokensForTokens(amountA,amountBMin,[tokenAaddress,tokenBaddress],self.account,deadline).buildTransaction(
                {
                    "from" : self.account,
                    # "gasPrice" : self.w3.toHex(25000000000),
                    # 'gas': 250000,
                    # 'maxPriorityFeePerGas': self.w3.toWei(20,'gwei'),
                    # 'maxFeePerGas': self.w3.toWei(30,'gwei'),
                    "nonce": nonce,
                }
            )                                      
        
        return tx
    
    def eth_to_token(self, tokenAaddress, tokenBaddress, amountBMin)  :
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        deadline = int(datetime.datetime.now().timestamp() + 1800)\
                                               
        tx = self.routerContract.functions.swapETHForExactTokens(amountBMin, tokenBaddress, [tokenAaddress,tokenBaddress],self.account,deadline).buildTransaction(
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
                                               
        tx = self.routerContract.functions.swapTokensForExactETH(amountA,amountBMin,[tokenAaddress,tokenBaddress],self.account,deadline).buildTransaction(
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
        
        self.routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])
        
        amountOut = self.routerContract.functions.getAmountsOut(amountIn, [tokenAaddress, tokenBaddress]).call()[-1]
        
        return amountOut
    
    def get_reserves(self, poolAddress, tokenAsymbol, tokenBsymbol):
        
        tokenA = self.tokens[tokenAsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        
        routerContract = self.get_contract(poolAddress, self.markets['routerAbi'])
        
        tokenA = routerContract.functions.token0().call()

        reserves = routerContract.functions.getReserves().call()
        
        if tokenA != tokenAaddress :
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenBsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenAsymbol))
            
            reserve = reserves[0] / reserves[1]
            
        else:
            reserves[0] = self.to_value(reserves[0], self.decimals(tokenAsymbol))
            reserves[1] = self.to_value(reserves[1], self.decimals(tokenBsymbol))
            
            reserve = reserves[1] / reserves[0]
        
        return reserve