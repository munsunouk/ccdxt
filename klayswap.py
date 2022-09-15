from src.base.exchange import Exchange
import json
from src.base.errors import ExchangeError
from src.base.errors import AuthenticationError
from src.base.errors import PermissionDenied
from src.base.errors import AccountSuspended
from src.base.errors import ArgumentsRequired
from src.base.errors import BadRequest
from src.base.errors import BadSymbol
from src.base.errors import MarginModeAlreadySet
from src.base.errors import BadResponse
from src.base.errors import InsufficientFunds
from src.base.errors import InvalidOrder
from src.base.errors import OrderNotFound
from src.base.errors import OrderImmediatelyFillable
from src.base.errors import OrderNotFillable
from src.base.errors import NotSupported
from src.base.errors import DDoSProtection
from src.base.errors import RateLimitExceeded
from src.base.errors import ExchangeNotAvailable
from src.base.errors import OnMaintenance
from src.base.errors import InvalidNonce
from src.base.errors import RequestTimeout

class klayswap(Exchange):

    def __init__(self):

        super().__init__()

        self.id = 1
        self.chainName = "klaytn"
        self.exchangeName = "klayswap"
        
        self.load_exchange(self.chainName, self.exchangeName)

        self.symbols = list(self.tokenList.keys())

        self.chainAbi = None
        self.network_path = None

        #market info
        self.id = None
        self.name = None
        self.enableRateLimit = True
        self.rateLimit = 2000  # milliseconds = seconds * 1000

        # #TODO private
        # self.address = config["private"]["wallet"]["address"]
        # self.privateKey = config["private"]["wallet"]["privateKey"]
        # self.network_path = config["public"]["chainInfo"]["private_node"]

        # self.markets = config['public']['marketList']['KlaySwap']
        # self.tokenList = config["public"]["tokenList"]
        # self.pools = config["public"]["poolList"]

        # self.symbols = list(self.tokenList.keys())  

        # self.tokens = None
        # self.pools = None
        # self.symbols = None
        
        # self.factoryAbi = None
        # self.routerAbi = None
        
        # #private info
        # self.privateKey = ''  # a "0x"-prefixed hexstring private key for a wallet
        # self.walletAddress = ''  # the wallet address "0x"-prefixed hexstring


if __name__ == "__main__" :
    
    klayswap = klayswap()