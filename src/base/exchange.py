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
    #chain info
    chain = None
    chainAbi = None
    network_path = None
    
    #market info
    id = None
    name = None
    enableRateLimit = True
    rateLimit = 2000  # milliseconds = seconds * 1000

    markets = None
    tokens = None
    pools = None
    symbols = None
    
    factoryAbi = None
    routerAbi = None
    
    #private info
    privateKey = ''  # a "0x"-prefixed hexstring private key for a wallet
    walletAddress = ''  # the wallet address "0x"-prefixed hexstring
    
    #system info
    asyncio_loop = None
    session = None  # Session () by default
    logger = None  # logging.getLogger(__name__) by default
    
    
    httpExceptions = {
        '422': ExchangeError,
        '418': DDoSProtection,
        '429': RateLimitExceeded,
        '404': ExchangeNotAvailable,
        '409': ExchangeNotAvailable,
        '410': ExchangeNotAvailable,
        '500': ExchangeNotAvailable,
        '501': ExchangeNotAvailable,
        '502': ExchangeNotAvailable,
        '520': ExchangeNotAvailable,
        '521': ExchangeNotAvailable,
        '522': ExchangeNotAvailable,
        '525': ExchangeNotAvailable,
        '526': ExchangeNotAvailable,
        '400': ExchangeNotAvailable,
        '403': ExchangeNotAvailable,
        '405': ExchangeNotAvailable,
        '503': ExchangeNotAvailable,
        '530': ExchangeNotAvailable,
        '408': RequestTimeout,
        '504': RequestTimeout,
        '401': AuthenticationError,
        '511': AuthenticationError,
    }
    has = {
        
        'createSwap': True,
        'fetchTokens': None,
        'fetchBalance': True,
        
    }
    
    def __init__(self, config={}):
        
        if self.chains:
            self.set_chains(self.chains)
        self.chainAbi = None
        self.network_path = None

        #market info
        self.id = None
        self.name = None
        self.enableRateLimit = True
        self.rateLimit = 2000  # milliseconds = seconds * 1000

        self.markets = None
        self.tokens = None
        self.pools = None
        self.symbols = None
        
        self.factoryAbi = None
        self.routerAbi = None
        
        #private info
        self.privateKey = ''  # a "0x"-prefixed hexstring private key for a wallet
        self.walletAddress = ''  # the wallet address "0x"-prefixed hexstring
        
        self.userAgent = default_user_agent()
        
        settings = self.deep_extend(self.describe(), config)
            
        for key in settings:
            if hasattr(self, key) and isinstance(getattr(self, key), dict):
                setattr(self, key, self.deep_extend(getattr(self, key), settings[key]))
            else:
                setattr(self, key, settings[key])
                
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
    
    def log(self, *args):
        print(*args)
    
    @staticmethod
    def safe_value(dictionary, key, default_value=None):
        return dictionary[key] if Exchange.key_exists(dictionary, key) else default_value
    
    @staticmethod
    def safe_integer(dictionary, key, default_value=None):
        if not Exchange.key_exists(dictionary, key):
            return default_value
        value = dictionary[key]
        try:
            # needed to avoid breaking on "100.0"
            # https://stackoverflow.com/questions/1094717/convert-a-string-to-integer-with-decimal-in-python#1094721
            return int(float(value))
        except ValueError:
            return default_value
        except TypeError:
            return default_value
    
    
    @staticmethod
    def set_account(*args) :
        
        if isinstance(args, str):
            
            account: LocalAccount = Account.from_key(args)
            result = self.safe_value(account, 'privateKey')
        
        else :
            
            result = self.w3.eth.accounts.create()
            
        return result
    
    def describe(self):
        return {}
    
    @staticmethod
    def key_exists(dictionary, key):
        if dictionary is None or key is None:
            return False
        if isinstance(dictionary, list):
            if isinstance(key, int) and 0 <= key and key < len(dictionary):
                return dictionary[key] is not None
            else:
                return False
        if key in dictionary:
            return dictionary[key] is not None and dictionary[key] != ''
        return False
        
    def load_chains(self, reload=False, params={}):
        
        if not reload:
            if self.chains:
                return self.set_chains(self.chains)

        
    def set_chains(self, chains, currencies=None):
        values = []
        chainValues = self.to_array(chains)
        for i in range(0, len(chainValues)):
            chain = self.deep_extend(self.safe_chain(),chainValues[i])
            values.append(chain)
        self.chains = self.index_by(values, 'symbol')
        chainsSortedBySymbol = self.keysort(self.chains)
        self.symbols = list(chainsSortedBySymbol.keys())
        if currencies is not None:
            self.currencies = self.deep_extend(self.currencies, currencies)
        else:
            baseCurrencies = []
            quoteCurrencies = []
            for i in range(0, len(values)):
                chain = values[i]
                if 'base' in chain:
                    currency = {
                        'id': self.safe_string_2(chain, 'baseId', 'base'),
                        'numericId': self.safe_string(chain, 'baseNumericId'),
                        'code': self.safe_string(chain, 'base'),
                    }
                    baseCurrencies.append(currency)
                if 'quote' in chain:
                    currency = {
                        'id': self.safe_string_2(chain, 'quoteId', 'quote'),
                        'numericId': self.safe_string(chain, 'quoteNumericId'),
                        'code': self.safe_string(chain, 'quote'),
                    }
                    quoteCurrencies.append(currency)
            baseCurrencies = self.sort_by(baseCurrencies, 'code')
            quoteCurrencies = self.sort_by(quoteCurrencies, 'code')
            self.baseCurrencies = self.index_by(baseCurrencies, 'code')
            self.quoteCurrencies = self.index_by(quoteCurrencies, 'code')
            allCurrencies = self.array_concat(baseCurrencies, quoteCurrencies)
            groupedCurrencies = self.group_by(allCurrencies, 'code')
            sortedCurrencies = self.sort_by(groupedCurrencies, 'code')
            self.currencies = self.deep_extend(self.currencies, self.index_by(sortedCurrencies, 'code'))
        self.currencies_by_id = self.index_by(self.currencies, 'id')
        currenciesSortedByCode = self.keysort(self.currencies)
        self.codes = list(currenciesSortedByCode.keys())
        return self.chains
    
    def safe_chain(self, chainId=None, chain=None, delimiter=None):
        result = {
            'id': chainId,
            'symbol': chainId,
            'base': None,
            'swap': False,
            'contract': False,
            'info': None,
        }
        return result
        
    def chain(self, symbol):
        if self.chain is None:
            raise ExchangeError(self.id + ' chain not loaded')
        if self.chain_by_id is None:
            raise ExchangeError(self.id + ' chain not loaded')
        if isinstance(symbol, str):
            if symbol in self.chain:
                return self.chain[symbol]
        raise BadSymbol(self.id + ' does not have chain symbol ' + symbol)
    
    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    
    def currency(self, code):
        if self.currencies is None:
            raise ExchangeError(self.id + ' currencies not loaded')
        if isinstance(code, str):
            if code in self.currencies:
                return self.currencies[code]
        raise ExchangeError(self.id + ' does not have currency code ' + code)