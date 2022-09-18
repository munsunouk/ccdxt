from src.base.exchange import Exchange
import datetime

class Meshswap(Exchange):

    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "polygon"
        self.exchangeName = "meshswap"
        self.address = None
        
        self.load_exchange(self.chainName, self.exchangeName)
        
    def fetch_tokens(self):

        return self.tokens
    
    def fetch_balance(self) :
        
        result = []
        
        symbols = list(self.tokens.keys())
        
        for symbol in symbols :
            
            balance = self.partial_balance(symbol)
            result.append(balance)
            
        return  result
    
    def create_swap(self, amountA, tokenA, amountBMin, tokenB) :
        
        tokenA = self.tokens[tokenA]
        tokenB = self.tokens[tokenB]
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
        
        routerContract = self.set_contract(self.w3, routerAddress, self.markets['routerAbi'])

        tx = routerContract.functions.swapExactTokensForTokens(amountA,amountBMin,[tokenA,tokenB],self.account,deadline).buildTransaction(
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

    
    def partial_balance(self, token : str) :
        
        token = self.tokens[token]
        
        tokenAaddress = self.set_checksum(token["contract"])
        accountAddress = self.set_checksum(self.account)
        
        chainContract = self.set_contract(self.w3, tokenAaddress, self.chains['chainAbi'])
        
        balance = chainContract.functions.balanceOf(accountAddress).call()
        
        balance = self.to_value(balance, token["decimal"])
        
        result = {
            
            "symbol" : token["symbol"],
            "address" : accountAddress,
            "balance" : balance
            
        }
        
        return result
    
    def check_approve(self, amountA : int, token : str, account : str, router : str)  :
        
        '''
        Check token approved and transact approve if is not
        
        Parameters
        ----------
        token : token address
        routerAddress: LP pool owner who allow
        '''
        
        if (token == self.baseCurrncy) :
            return
        
        contract = self.set_contract(self.w3, token, self.chains['chainAbi'])
        
        approvedTokens = contract.functions.allowance(account,router).call()
        
        if approvedTokens < amountA :
           
           tx = self.get_approve(token, router)
           
           tx_receipt = self.fetch_transaction(tx)

           return tx_receipt
           
        else : return
        
    def get_approve(self,token : str, router : str) :
        
        contract = self.set_contract(self.w3, token, self.chains['chainAbi'])
        
        nonce = self.get_TransactionCount(self.account)
        
        tx = contract.functions.approve(router, self.unlimit).buildTransaction(
            {
                "from" : self.account,
                "nonce": nonce,
            }
        )
        
        return tx