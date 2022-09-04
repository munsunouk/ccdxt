# from src.base.chain import Chain
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
import requests
import base64
from web3 import Web3

class klaytn:
    
    def __init__(self,params : dict) :
        
        #TODO
        self.accessKeyId = params["private"]["chain"]["accessKeyId"]
        self.secretAccessKey = params["private"]["chain"]["secretAccessKey"]
        self.address = params["private"]["wallet"]["address"]
        self.accessKeyId = params["private"]["wallet"]["privateKey"]


        self.markets = params["public"]["marketListPath"]
        self.tokens = params["public"]["tokenListPath"]
        self.pools = params["public"]["poolListPath"]

    def get_provider(self) :
        
        userAndPass = base64.b64encode(bytes(f'{self.accessKeyId}:{self.secretAccessKey}', encoding="utf-8")).decode('ascii')
    
        headers = {
            'headers' : [
                {
                    'name' : 'Authorization', 
                    'value' : 'Basic %s' %  userAndPass 
                },
                {
                    'name' : 'x-chain-id', 
                    'value' : 8217
                },
                    
            ]
        }
        
        session = requests.Session()
        session.headers.update(headers)

        self.w3 = Web3(Web3.HTTPProvider(self.network_pathes[1], session=session))

    def fetch_tokens(self):
        
        #TODO
        # fetchCurrenciesEnabled = self.safe_value(self.options, 'fetchCurrencies')
        # if not fetchCurrenciesEnabled:
        #     return None
        
        response = self.tokens
        return response

    # #TODO
    # def set_balnace(self) :

    # def fetch_balance(self) :



    

if __name__ == "__main__" :
    
    tokenListPath = "src/resources/chain/klaytn/contract/token_list.json"
    poolListPath = "src/resources/chain/klaytn/contract/pool_list.json"
    marketListPath = "src/resources/chain/klaytn/contract/market_list.json"

    privatePath = "src/resources/chain/klaytn/contract/private.json"

    with open(tokenListPath, "rb") as file_in:
        tokenListPath = file_in.readline()
        
    with open(poolListPath, "rb") as file_in:
        poolListPath = file_in.readline()

    with open(marketListPath, "rb") as file_in:
        marketListPath = file_in.readline()

    with open(privatePath, "rb") as file_in:
        privatePath = file_in.readline()
        
    params = {

        "public" : {

            "tokenListPath" : tokenListPath,
            "poolListPath" : poolListPath,
            "marketListPath" : marketListPath,

        },
        "private" : privatePath

    }

klaytn = klaytn(params)

klaytn.fetch_tokens()
