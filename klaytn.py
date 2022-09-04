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
from src.base.big_number import BigNumber
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
        
        self.chainAbi = params["public"]["chainAbi"]
        self.factoryAbi = params["public"]["factoryAbi"]
        self.routerAbi = params["public"]["routerAbi"]

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
    

    #TODO
    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    
    def set_balance(self,token : str, address : str) :
        
        token = self.set_checksum(token["contract"])
        
        decimal = token["decimal"]
        
        contract = self.set_contract(address, self.chainAbi)
        
        balance = contract(token).functions.balanceOf(address).call()
        
        balance = BigNumber.to_number(value = balance, exp = decimal)
        
        return balance
    
    def set_contract(self,address : str ,abi : dict) :
        
        contract = self.w3.eth.contract(address, abi = abi)
        
        return contract
        
    def set_checksum(self,value) :
        
        result = Web3.toChecksumAddress(value)
        
        return result
    
    
    # def set_balnace(self) :
    
            
    

    # def fetch_balance(self) :



    

if __name__ == "__main__" :
    
    tokenListPath = "src/resources/chain/klaytn/contract/token_list.json"
    poolListPath = "src/resources/chain/klaytn/contract/pool_list.json"
    marketListPath = "src/resources/chain/klaytn/contract/market_list.json"
    chainInfoPath = "src/resources/chain/klaytn/contract/chain_list.json"
    
    privatePath = "src/resources/chain/klaytn/contract/private.json"

    with open(tokenListPath, "rb") as file_in:
        tokenListPath = json.load(file_in)
        
    with open(poolListPath, "rb") as file_in:
        poolListPath = json.load(file_in)

    with open(marketListPath, "rb") as file_in:
        marketListPath = json.load(file_in)
        
    with open(chainInfoPath, "rb") as file_in:
        chainInfoPath = json.load(file_in)

    with open(privatePath, "rb") as file_in:
        privatePath = json.load(file_in)
        
    chainAbi = chainInfoPath["chainAbi"]
    factoryAbi = chainInfoPath["factoryAbi"]
    routerAbi = chainInfoPath["routerAbi"]

    with open(chainAbi, 'r') as f:
        chainAbi = json.load(f)
    with open(factoryAbi, 'r') as f:
        factoryAbi = json.load(f)
    with open(routerAbi, 'r') as f:
        routerAbi = json.load(f)
        
    params = {

        "public" : {

            "tokenList" : tokenListPath,
            "poolList" : poolListPath,
            "marketList" : marketListPath,
            "chainInfo" : chainInfoPath,
            "chainAbi" : chainAbi,
            "factoryAbi" : factoryAbi,
            "routerAbi" : routerAbi
        
        },
        "private" : privatePath

    }

klaytn = klaytn(params)

tokens = klaytn.fetch_tokens()

print(tokens)
