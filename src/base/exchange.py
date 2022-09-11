from errors import ExchangeError
from errors import NetworkError
from errors import NotSupported
from errors import AuthenticationError
from errors import DDoSProtection
from errors import RequestTimeout
from errors import ExchangeNotAvailable
from errors import InvalidAddress
from errors import InvalidOrder
from errors import ArgumentsRequired
from errors import BadSymbol
from errors import NullResponse
from errors import RateLimitExceeded
from requests.utils import default_user_agent
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3

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

    def safe_market(self):
        result = {
            'id': None,
            'name' : None,
            'symbol': None,
            "baseCurrency" : None,
            "fee" : None,
            "factoryAbi" : None,
            "factoryAddress" : None,
            "routerAbi" : None,
            "routerAddress" : None,
            'info': None,
            "symbols" : None,
            "pools" : None,
            "chains" : None,

        }
        return result

    def safe_token(self):
        result = {
            "id" : None,
            "name" : None,
            "symbol" : None,
            "contract" : None,
            "decimal" : None,
            "info" : None
        }
        return result

    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    
    def load_markets(self, reload=False, params={}):
        
        if not reload:
            if self.markets:
                return self.set_markets(self.markets)

    def set_markets(self, markets, currencies=None):

        symbols = self.markets['symbols']
        self.tokens = {}

        if markets :
           self.markets = self.deep_extend(self.safe_market(),self.markets)

        if len(symbols) > 0 :
           self.symbols = self.deep_extend(self.symbols, symbols)

        for token in self.tokenList :

            if token in self.symbols :

              self.tokens[token] = self.deep_extend(self.safe_token(), self.tokenList[token])
        
        return self.markets