from ccdxt.base.async_support.base.exchange import Exchange
from ccdxt.base.utils.errors import InsufficientBalance
from ccdxt.base.utils import safeMath
from ccdxt.base.utils.validation import *

from eth_typing import HexAddress
from eth_typing.evm import Address, ChecksumAddress

import datetime

class Orbitbridge(Exchange):
    
    has = {
        
        'create_bridge': True,
        'fetchTicker': True,
        'fetchBalance': True,
        
    }

    def __init__(self):

        super().__init__()

        #market info
        self.id = 1
        self.chainName = "ORBIT"
        self.exchangeName = "orbitbridge"

    async def create_bridge(self, amount, tokenSymbol,fromChain, toChain, toAddr) :
        '''
        Info
        ----------
        create bridge amount of token in fromChain to toChain`s toAddr after check approve
        
        Parameters
        ----------
        amount : token amount input
        tokenAsymbol: symbol of token input
        fromChain : name of chain token transfering
        toChain : name of chain token transfered
        toAddr : address of account of toChain`s chain 
        
        Returns
        -------
        {
        'transaction_hash': '0x6ea0feb76b39e4a2b03e553b4fbbacf8aefb8e5a1f7911893891fc49e5d8db79', 
        'status': 1, 
        'block': 34314503, 
        'timestamp': datetime.datetime(2022, 10, 14, 10, 18, 6, 614884), 
        'function': <Function requestSwap(address,string,bytes,uint256)>,
        'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF', 
        'amountIn': 0.622748, 
        'tokenA': 'oZEMIT', 
        'to': '0x9Abc3F6c11dBd83234D6E6b2c373Dfc1893F648D', 
        'from_chain': 'MATIC', 
        'to_chain': 'KLAYTN', 
        'transaction_fee:': 0.009408398005397502
        }
        '''
        
        self.load_bridge(fromChain, self.exchangeName)
        self.load_exchange(fromChain)
        
        self.tokenSymbol = tokenSymbol
        self.fromChain = fromChain
        self.toChain = toChain
        
        token = self.tokens[tokenSymbol]
        
        # base = self.tokens[]

        tokenBalance = self.partial_balance(tokenSymbol)
        
        # baseBalance = self.partial_balance(tokenSymbol)
        
        self.require(amount < tokenBalance['balance'], InsufficientBalance(tokenBalance, amount))

        amount = self.from_value(value = amount, exp = int(token["decimals"]))
        
        tokenAddress = self.set_checksum(token['contract'])
        accountAddress = self.set_checksum(self.account)
        toAddrress = self.set_checksum(toAddr)
        bridgeAddress = self.set_checksum(self.bridge["bridgeAddress"])
        
        if fromChain == 'KLAYTN' :
            
            self.check_approve(amountA = amount, token = tokenAddress, \
                           account = accountAddress, router = bridgeAddress)
            
            self.routerContract = self.get_contract(bridgeAddress, self.bridge['bridgeAbi'])

            tx = self._depositToken(tokenAddress, toChain, toAddrress, amount)
            
        elif fromChain == 'MATIC' :
            
            self.set_pos()
            
            self.check_approve(amountA = amount, token = tokenAddress, \
                           account = accountAddress, router = bridgeAddress)
            
            self.routerContract = self.get_contract(bridgeAddress, self.bridge['bridgeAbi'])
            
            tx = self._requestSwap(tokenAddress, toChain, toAddrress, amount)

        tx_receipt = self.fetch_transaction(tx, round = 'BRIDGE')
           
        return tx_receipt
    
    def _depositToken(self, tokenAddress: ChecksumAddress, toChain: str, toAddr: ChecksumAddress, amount: int):
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        tx = self.routerContract.functions.depositToken(tokenAddress, toChain, toAddr, amount).buildTransaction(                                          
            {
                "from" : self.account,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        
        return tx
    
    def _requestSwap(self, tokenAddress: ChecksumAddress, toChain: str, toAddr: ChecksumAddress, amount: int):
        
        nonce = self.w3.eth.getTransactionCount(self.account)
        
        tx = self.routerContract.functions.requestSwap(tokenAddress, toChain, toAddr, amount).buildTransaction(                                          
            {
                "from" : self.account,
                # 'gas' : 4000000,
                "nonce": nonce,
            }
        )
        
        return tx
    
    def decode(self,fromChain, tx_hash) :
        
        self.load_bridge(fromChain, self.exchangeName)
        self.load_exchange(fromChain)
        routerAddress = self.set_checksum(self.bridge["bridgeAddress"])
        routerContract = self.get_contract(routerAddress, self.bridge['bridgeAbi'])

        transaction = self.w3.eth.getTransaction(tx_hash)
        
        result = routerContract.decode_function_input(transaction.input)
        
        return result
    