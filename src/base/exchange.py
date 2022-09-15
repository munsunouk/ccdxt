from src.base.errors import ExchangeError
from src.base.errors import NetworkError
from src.base.errors import NotSupported
from src.base.errors import AuthenticationError
from src.base.errors import DDoSProtection
from src.base.errors import RequestTimeout
from src.base.errors import ExchangeNotAvailable
from src.base.errors import InvalidAddress
from src.base.errors import InvalidOrder
from src.base.errors import ArgumentsRequired
from src.base.errors import BadSymbol
from src.base.errors import NullResponse
from src.base.errors import RateLimitExceeded
from src.base import Chain, Market, Pool, Token 
from src.base import Abi
from requests.utils import default_user_agent
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from typing import Optional, Type, Union
import json
from eth_typing import HexAddress
from web3.contract import Contract
from decimal import Decimal

class Exchange(object):
    """Base exchange class"""
    has = {
        
        'createSwap': True,
        'fetchTokens': None,
        'fetchBalance': True,
        
    }

    def __init__(self, config={}):

        self.chains = None
        # if self.chains:
        #     self.set_chains(self.chains)
        self.chainAbi = None
        self.network_path = None

        #market info
        self.id = None
        self.name = None
        self.enableRateLimit = True
        self.rateLimit = 2000  # milliseconds = seconds * 1000

        self.markets = None
        self.tokenList = None
        self.tokens = None
        self.pools = None
        self.symbols = None
        
        self.factoryAbi = None
        self.routerAbi = None
        
        #private info
        self.privateKey = ''  # a "0x"-prefixed hexstring private key for a wallet
        self.walletAddress = ''  # the wallet address "0x"-prefixed hexstring

    def fetch_tokens(self) :
        raise NotSupported('fetch_tokens() is not supported yet')

    def fetch_balance(self) :
        raise NotSupported('fetch_balance() is not supported yet')
    
    def create_swap(self,amountA, tokenA, amountBMin, tokenB) :
        raise NotSupported('create_swap() is not supported yet')
    
    def functiontransaction(self, w3, privateKey, tx):
        
        '''
        Takes built transcations and transmits it to ethereum
        
        Parameters
        ----------
        w3 : web3 object
        privateKey : users private key
        tx : Transaction to be transmitted
        
        Returns
        -------
        Transaction reciept = 
        
            AttributeDict(
                {
                    'blockHash': HexBytes('0x01af4f5a6e68726ab17426e1b1f43f8b2e2602676626d936c4e5dfe045d91957'), 
                    'blockNumber': 99072001, 
                    'contractAddress': None, 
                    'cumulativeGasUsed': 88596, 
                    'effectiveGasPrice': 250000000000, 
                    'from': '0xdaf07D203C01467644e7305BE9caA6E9Fe12ac9a', 
                    'gasUsed': 31259, 
                    'logs': [AttributeDict(
                        {
                            'address': '0xceE8FAF64bB97a73bb51E115Aa89C17FfA8dD167', 
                            'blockHash': HexBytes('0x01af4f5a6e68726ab17426e1b1f43f8b2e2602676626d936c4e5dfe045d91957'), 
                            'blockNumber': 99072001, 
                            'data': '0x000000000000000000000000000000000000000000000000000000003b9aca00', 
                            'logIndex': 1, 
                            'removed': False, 
                            'topics': [HexBytes('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'), 
                            HexBytes('0x000000000000000000000000daf07d203c01467644e7305be9caa6e9fe12ac9a'), 
                            HexBytes('0x000000000000000000000000c6a2ad8cc6e4a7e08fc37cc5954be07d499e7654')], 
                            'transactionHash': HexBytes('0x02bf327810bc2113eecf5d91f110ad2b91310272576b5ee5353a69e33e98c030'), 
                            'transactionIndex': 1
                        }
                    )],
                    'logsBloom': HexBytes('0x00000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000001000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000010000040000000000000000000006000000000000000000000000000000000'), 
                    'status': 1, 
                    'to': '0xceE8FAF64bB97a73bb51E115Aa89C17FfA8dD167', 
                    'transactionHash': HexBytes('0x02bf327810bc2113eecf5d91f110ad2b91310272576b5ee5353a69e33e98c030'), 
                    'transactionIndex': 1, 
                    'type': '0x2'
                }
            )
        '''
        signed_tx =w3.eth.account.signTransaction(tx, privateKey)
        
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        return w3.eth.waitForTransactionReceipt(tx_hash)

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = Exchange.deep_extend(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result
    
    @staticmethod
    def safe_chain():
        return json.dumps(Chain().__dict__)

    @staticmethod
    def safe_market():
        return json.dumps(Market().__dict__)
    
    @staticmethod
    def safe_pool():
        return json.dumps(Pool().__dict__)
    
    @staticmethod
    def safe_token():
        return json.dumps(Token().__dict__)
    
    
    @staticmethod
    def from_value(value : float or int, exp : int=18) -> int :
        return int(round(value * 10 ** exp))

    @staticmethod
    def to_value(value : float or int, exp : int=18)-> Decimal :
        return Decimal(value) / Decimal(10 ** exp)
    
    def set_chains(self,chainName):
        return Chain().set_chain(chainName)
    
    def set_markets(self,chainName,exchangeName):
        return Market().set_market(chainName,exchangeName)
    
    def set_pools(self,chainName,exchangeName):
        return Pool().set_pool(chainName,exchangeName)
    
    def set_tokens(self,chainName,exchangeName):
        return Token().set_token(chainName,exchangeName)
    
    def load_exchange(self,chainName,exchangeName):
        
        self.load_tokens(chainName, exchangeName)
        self.load_pools(chainName, exchangeName)
        self.load_markets(chainName, exchangeName)
    
    def load_network(self,network_path) :
        
        self.w3 = Web3(Web3.HTTPProvider(network_path))

    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    
    def load_chains(self, chainName) :
        
        chains = self.set_chains(chainName)

        self.chains = {}

        if chains :
           self.chains = self.deep_extend(self.safe_chain(),chains)
    
    def load_markets(self, chainName, exchangeName):
        
        markets = self.set_markets(chainName,exchangeName)

        self.markets = {}

        if markets :
           self.markets = self.deep_extend(self.safe_market(),markets)
        
    def load_pools(self, chainName, exchangeName):
        
        pools = self.set_pools(chainName,exchangeName)

        self.pools = {}

        for pool in pools :

            self.pools[pool] = self.deep_extend(self.safe_pool(), pools[pool])
            
    def load_tokens(self, chainName, exchangeName):
        
        tokens = self.set_tokens(chainName,exchangeName)

        self.tokens = {}

        for token in tokens :

            self.tokens[token] = self.deep_extend(self.safe_token(), tokens[token])
           

           
           

    def set_contract(self, w3, address : str ,abi : dict) :
        
        contract = self.w3.eth.contract(address, abi = abi)
        
        return contract
    
    def set_checksum(self,value) :
        
        result = Web3.toChecksumAddress(value)
        
        return result     
