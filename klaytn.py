# from src.base.chain import Chain
import json
from src.base.exchange import Exchange
from web3 import Web3
import datetime

class klayswap(Exchange):

    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "klaytn"
        self.exchangeName = "klayswap"
        
        self.load_exchange(self.chainName, self.exchangeName)

        # self.symbols = list(self.tokenList.keys())
        

        self.symbols = list(self.tokens.keys())
        
        print(self.symbols)
        
    def fetch_tokens(self):

        return self.tokens
    
    def fetch_balance(self) :
        
        result = []
        
        for symbol in self.symbols :
            
            balance = self.set_balance(self.tokens[symbol])
            result.append(balance)
            
        return  result
    
    def create_swap(self, amountA, tokenA, amountBMin, tokenB, market) :
        
        amountA = BigNumber(value = amountA, exp = self.tokens[tokenA]["decimal"]).from_value()
        
        tokenA_address = self.tokens[tokenA]["contract"]
        
        tokenA_checksum = self.set_checksum(tokenA_address)
        
        amountBMin = BigNumber(value = amountBMin, exp = self.tokens[tokenB]["decimal"]).from_value()
        
        tokenB_address = self.tokens[tokenB]["contract"]
        
        tokenB_checksum = self.set_checksum(tokenB_address)
        
        address_checksum = self.set_checksum(self.address)
        
        router_checksum = self.set_checksum(self.markets[market]["routerAddress"])
        
        self.check_approve(amountA = amountA, token = tokenA_checksum, \
                           address = address_checksum, router = router_checksum)
        
        deadline = int(datetime.datetime.now().timestamp() + 1800)
        
        contract = self.set_contract(router_checksum, self.routerAbi)
        
        nonce = self.w3.eth.getTransactionCount(self.address)
        
        tx = contract.functions.exchangeKctPos(tokenA_checksum, amountA, \
                                               tokenB_checksum, amountBMin, []).buildTransaction(
            {
                "from" : self.address,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        tx_receipt = self.functiontransaction(tx)
        
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

    
    def set_balance(self,token : str) :
        
        token_checksum = self.set_checksum(token["contract"])
        
        address_checksum = self.set_checksum(self.address)
        
        decimal = token["decimal"]
        
        contract = self.set_contract(token_checksum, self.chainAbi)
        
        balance = contract.functions.balanceOf(address_checksum).call()
        
        balance = BigNumber(value = balance, exp = decimal).to_value()
        
        result = {
            
            "symbol" : token["symbol"],
            "address" : address_checksum,
            "balance" : balance
            
        }
        
        return result
    
    def check_approve(self, amountA : int, token : str, address : str, router : str)  :
        
        '''
        Check token approved and transact approve if is not
        
        Parameters
        ----------
        token : token address
        routerAddress: LP pool owner who allow
        '''
        
        if (token == ('0x0000000000000000000000000000000000000000')) :
            return
        
        contract = self.set_contract(token, self.chainAbi)
        
        approvedTokens = contract.functions.allowance(address,router).call()
        
        if approvedTokens < amountA :
           
           tx = self.get_approve(token, router)

           return tx
           
        else : return
        
    def get_approve(self,token : str, router : str) :
        
        contract = self.set_contract(token, self.chainAbi)
        
        tx = contract.functions.approve(router, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact()
        
        return tx

if __name__ == "__main__" :
    
    klaytn = klayswap()

# balance = klaytn.fetch_balance()

# swap = klaytn.create_swap(1, 'MOOI' , 0.3, 'oUSDT', 'KlaySwap')

# print(swap)
