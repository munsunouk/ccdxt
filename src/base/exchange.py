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
from src.base import Token, Market, Pool 
from src.base import BigNumber, Abi
from requests.utils import default_user_agent
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from typing import Optional, Type, Union
import json
from eth_typing import HexAddress
from web3.contract import Contract

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
        
        # self.userAgent = default_user_agent()
        
        # settings = self.deep_extend(self.describe(), config)
            
        # for key in settings:
        #     if hasattr(self, key) and isinstance(getattr(self, key), dict):
        #         setattr(self, key, self.deep_extend(getattr(self, key), settings[key]))
        #     else:
        #         setattr(self, key, settings[key])

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
    def safe_token():
        return json.dumps(Token().__dict__)
    
    @staticmethod
    def safe_market():
        return json.dumps(Market().__dict__)
    
    @staticmethod
    def safe_pool():
        return json.dumps(Pool().__dict__)

    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    
    def load_exchange(self):
        
        self.set_tokens(self.tokens)
        self.set_pools(self.pools)
        self.set_markets(self.markets)
        
    def set_tokens(self, tokens):
        
        print(f"tokens : {tokens}")

        self.tokens = {}

        for token in tokens :

            self.tokens[token] = self.deep_extend(self.safe_token(), tokens[token])
        
        return self.tokens
    
    def set_pools(self, pools):
        
        print(f"pools : {pools}")

        self.pools = {}

        for pool in pools :

            self.pools[pool] = self.deep_extend(self.safe_pool(), pools[pool])
        
        return self.pools

    def set_markets(self, markets):
        
        print(f"markets : {markets}")

        symbols = markets['symbols']
        self.tokens = {}

        if markets :
           self.markets = self.deep_extend(self.safe_market(),self.markets)

        if len(symbols) > 0 :
           self.symbols = self.deep_extend(self.symbols, symbols)

    
    
    
# `   def get_contract(self, web3: Web3, fname: str, bytecode: Optional[str] = None) -> Type[Contract]:
#         """Create a Contract proxy class from our bundled contracts.
#         `See Web3.py documentation on Contract instances <https://web3py.readthedocs.io/en/stable/contracts.html#contract-deployment-example>`_.
#         :param web3: Web3 instance
#         :param bytecode: Override bytecode payload for the contract
#         :param fname: `JSON filename from supported contract lists <https://github.com/tradingstrategy-ai/web3-ethereum-defi/tree/master/eth_defi/abi>`_.
#         :return: Python class
#         """
#         contract_interface = self.get_abi_by_filename(fname)
#         abi = contract_interface["abi"]
#         bytecode = bytecode if bytecode is not None else contract_interface["bytecode"]
#         Contract = web3.eth.contract(abi=abi, bytecode=bytecode)
#         return Contract

#     def get_deployed_contract(self, web3: Web3,fname: str,address: Union[HexAddress, str],) -> Contract:
#         """Get a Contract proxy objec for a contract deployed at a specific address.
#         `See Web3.py documentation on Contract instances <https://web3py.readthedocs.io/en/stable/contracts.html#contract-deployment-example>`_.
#         :param web3: Web3 instance
#         :param fname: `JSON filename from supported contract lists <https://github.com/tradingstrategy-ai/web3-ethereum-defi/tree/master/eth_defi/abi>`_.
#         :param address: Ethereum address of the deployed contract
#         :return: `web3.contract.Contract` subclass
#         """
#         assert address
#         Contract = self.get_contract(web3, fname)
#         return Contract(address)`