from src.base.exchange import Exchange
import datetime

class Neuronswap(Exchange):

    def __init__(self):

        super().__init__()

        #market info
        self.id = 5
        self.chainName = "klaytn"
        self.exchangeName = "neuronswap"
        
        self.load_exchange(self.chainName, self.exchangeName)
    
    def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol) :
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value = amountA, exp = tokenA["decimal"])
        amountBMin = self.from_value(value = amountBMin, exp = tokenB["decimal"])
        nonce = self.w3.eth.getTransactionCount(self.account)
        deadline = int(datetime.datetime.now().timestamp() + 1800)
        
        tokenAaddress = self.set_checksum(tokenA['contract'])
        tokenBaddress = self.set_checksum(tokenB['contract'])
        accountAddress = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        
        self.check_approve(amountA = amountA, token = tokenAaddress, \
                           account = accountAddress, router = routerAddress)
        
        routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])

        tx = routerContract.functions.swapExactTokensForTokens(amountA,amountBMin,
                                                               [tokenAaddress,tokenBaddress],self.account,deadline).buildTransaction(
            {
                "from" : self.account,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        tx_receipt = self.fetch_transaction(tx)
        
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
    