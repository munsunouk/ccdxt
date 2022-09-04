from src.base.chain import Chain
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
import collections

class klaytn:
    
    def __init__(self,params : dict) :
        
        
        self.tokens = tokenListPath
    
    def fetch_tokens(self):
        
        #TODO
        # fetchCurrenciesEnabled = self.safe_value(self.options, 'fetchCurrencies')
        # if not fetchCurrenciesEnabled:
        #     return None
        
        response = self.tokens
        
        return response
    
    

if __name__ == "__main__" :
    
    tokenListPath = "src/resources/chain/klaytn/contract/token_list.json"
    poolListPath = "src/resources/chain/klaytn/contract/pool_list.json"
        
    with open(tokenListPath, "rb") as file_in:
        tokenListPath = file_in.readline()
        
    with open(poolListPath, "rb") as file_in:
        poolListPath = file_in.readline()
        
    