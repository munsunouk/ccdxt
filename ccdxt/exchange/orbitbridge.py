from ccdxt.base.exchange import Exchange
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

    def create_bridge(self, amount, tokenSymbol,fromChain, toChain, toAddr) :
        
        self.load_bridge(fromChain, self.exchangeName)
        self.load_exchange(fromChain, 'klayswap')
        
        self.tokenSymbol = tokenSymbol
        self.fromChain = fromChain
        self.toChain = toChain
        
        token = self.tokens[tokenSymbol]
        
        tokenBalance = self.partial_balance(tokenSymbol)
        
        self.require(amount > tokenBalance['balance'], InsufficientBalance(tokenBalance, amount))

        amount = self.from_value(value = amount, exp = int(token["decimals"]))
        
        tokenAddress = self.set_checksum(token['contract'])
        accountAddress = self.set_checksum(self.account)
        toAddrress = self.set_checksum(toAddr)
        bridgeAddress = self.set_checksum(self.bridge["bridgeAddress"])
        
        self.check_approve(amountA = amount, token = tokenAddress, \
                           account = accountAddress, router = bridgeAddress)
        
        self.routerContract = self.get_contract(bridgeAddress, self.bridge['bridgeAbi'])

        tx = self._depositToken(tokenAddress, toChain, toAddrress, amount)

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
    
    def decode(self,fromChain, tx_hash) :
        
        self.load_bridge(fromChain, self.exchangeName)
        self.load_exchange(fromChain, 'klayswap')
        
        routerAddress = self.set_checksum(self.bridge["bridgeAddress"])
        routerContract = self.get_contract(routerAddress, self.bridge['bridgeAbi'])
        
        # print(self.bridge['bridgeAbi'])
        
        transaction = self.w3.eth.getTransaction(tx_hash)
        
        result = routerContract.decode_function_input(transaction.input)
        
        return result
    