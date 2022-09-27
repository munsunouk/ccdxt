from ccdxt.base.exchange import Exchange
import datetime

class Pangeaswap(Exchange):

    def __init__(self):

        super().__init__()

        #market info
        self.id = 4
        self.chainName = "klaytn"
        self.exchangeName = "pangeaswap"
        
        self.load_exchange(self.chainName, self.exchangeName)
    
    def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol) :
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value = amountA, exp = tokenA["decimal"])
        amountBMin = self.from_value(value = amountBMin, exp = tokenB["decimal"])
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        for pool in self.pools :
            
            if (self.pools[pool]["tokenA"] == tokenAsymbol) or (self.pools[pool]["tokenB"] == tokenAsymbol) \
                and (self.pools[pool]["tokenA"] == tokenBsymbol) or (self.pools[pool]["tokenB"] == tokenBsymbol) :
                    
                    pool = self.pools[pool]
        
        tokenAaddress = self.set_checksum(tokenA['contract'])
        tokenBaddress = self.set_checksum(tokenB['contract'])
        accountAddress = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        poolAddress = self.set_checksum(pool["contract"])
        
        self.check_approve(amountA = amountA, token = tokenAaddress, \
                           account = accountAddress, router = routerAddress)
        
        self.routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])

        tx = self.routerContract.functions.exactInputSingle(
            (
                tokenAaddress,
                amountA,
                amountBMin,
                poolAddress,
                self.account,
                False,
            )).buildTransaction(
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