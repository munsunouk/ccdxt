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
from src.base.errors import ContractLogicError
from src.base.exchange import Exchange
from src.base.big_number import BigNumber
from src.base.abi import ABI
import collections
import requests
import base64
from web3 import Web3
import datetime

class klayswap(Exchange):
    
    def __init__(self, config : dict) :
        
        #TODO private
        # self.address = config["private"]["wallet"]["address"]
        # self.privateKey = config["private"]["wallet"]["privateKey"]
        self.network_path = config["public"]["chainInfo"]["mainnet"]["public_node"]

        self.markets = config["public"]["marketList"]["KlaySwap"]
        
        self.tokenList = config["public"]["tokenList"]
        self.pools = config["public"]["poolList"]
        
        self.chainAbi = config["public"]["chainAbi"]
        self.factoryAbi = config["public"]["factoryAbi"]
        self.routerAbi = config["public"]["routerAbi"]
        
        self.set_network(self.network_path)
        
        self.load_markets(self.markets)
        
        self.symbols = list(self.tokenList.keys())

    def set_network(self,network_path) :
        
        self.w3 = Web3(Web3.HTTPProvider(network_path))
        
    def fetch_tokens(self):

        return self.tokens
    
    def fetch_balance(self) :
        
        result = []
        
        for symbol in self.symbols :
            
            balance = self.set_balance(self.tokens[symbol])
            result.append(balance)
            
        return  result
    
    
    def create_swap(self, amountA, tokenA, amountBMin, tokenB, market) :
        
        amountA = BigNumber(value = amountA, exp = self.tokens[tokenA]["decimal"]).from_value()
        
        tokenA_address = self.tokens[tokenA]["contract"]
        
        tokenA_checksum = self.set_checksum(tokenA_address)
        
        amountBMin = BigNumber(value = amountBMin, exp = self.tokens[tokenB]["decimal"]).from_value()
        
        tokenB_address = self.tokens[tokenB]["contract"]
        
        tokenB_checksum = self.set_checksum(tokenB_address)
        
        address_checksum = self.set_checksum(self.address)
        
        router_checksum = self.set_checksum(self.markets[market]["routerAddress"])
        
        self.check_approve(amountA = amountA, token = tokenA_checksum, \
                           address = address_checksum, router = router_checksum)
        
        deadline = int(datetime.datetime.now().timestamp() + 1800)
        
        contract = self.set_contract(router_checksum, self.routerAbi)
        
        nonce = self.w3.eth.getTransactionCount(self.address)
        
        tx = contract.functions.exchangeKctPos(tokenA_checksum, amountA, \
                                               tokenB_checksum, amountBMin, []).buildTransaction(
            {
                "from" : self.address,
                'gas' : 4000000,
                "nonce": nonce,
            }
        )
        tx_receipt = self.functiontransaction(tx)
        
        tx_arrange = {
            
            'transaction_hash' : tx_receipt['transactionHash'].hex(),
            'status' : None,
            'block' :  tx_receipt['blockNumber'],
            'timestamp' : datetime.datetime.now(),
            'from' : tx_receipt['from'],
            'to' : tx_receipt['to'],
            'transaction_fee:' : tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18 ,
            
        }
           
        return tx_arrange

    
    def set_balance(self,token : str) :
        
        token_checksum = self.set_checksum(token["contract"])
        
        address_checksum = self.set_checksum(self.address)
        
        decimal = token["decimal"]
        
        contract = self.set_contract(token_checksum, self.chainAbi)
        
        balance = contract.functions.balanceOf(address_checksum).call()
        
        balance = BigNumber(value = balance, exp = decimal).to_value()
        
        result = {
            
            "symbol" : token["symbol"],
            "address" : address_checksum,
            "balance" : balance
            
        }
        
        return result
    
    def check_approve(self, amountA : int, token : str, address : str, router : str)  :
        
        '''
        Check token approved and transact approve if is not
        
        Parameters
        ----------
        token : token address
        routerAddress: LP pool owner who allow
        '''
        
        if (token == ('0x0000000000000000000000000000000000000000')) :
            return
        
        contract = self.set_contract(token, self.chainAbi)
        
        approvedTokens = contract.functions.allowance(address,router).call()
        
        if approvedTokens < amountA :
           
           tx = self.get_approve(token, router)

           return tx
           
        else : return
        
    def get_approve(self,token : str, router : str) :
        
        contract = self.set_contract(token, self.chainAbi)
        
        tx = contract.functions.approve(router, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact()
        
        return tx

if __name__ == "__main__" :
    
    tokenListPath = "src/resources/chain/klaytn/contract/token_list.json"
    poolListPath = "src/resources/chain/klaytn/contract/pool_list.json"
    marketListPath = "src/resources/chain/klaytn/contract/market_list.json"
    chainInfoPath = "src/resources/chain/klaytn/contract/chain_info.json"
    
    privatePath = "src/resources/chain/klaytn/contract/private.json"

    with open(tokenListPath, "rb") as file_in:
        tokenListPath = json.load(file_in)
        
    with open(poolListPath, "rb") as file_in:
        poolListPath = json.load(file_in)

    with open(marketListPath, "rb") as file_in:
        marketListPath = json.load(file_in)
        
    with open(chainInfoPath, "rb") as file_in:
        chainInfoPath = json.load(file_in)

    chainAbi = chainInfoPath["chainAbi"]
    factoryAbi = chainInfoPath["factoryAbi"]
    routerAbi = chainInfoPath["routerAbi"]

    with open(chainAbi, 'r') as f:
        chainAbi = json.load(f)
    with open(factoryAbi, 'r') as f:
        factoryAbi = json.load(f)
    with open(routerAbi, 'r') as f:
        routerAbi = json.load(f)
        
    config = {

        "public" : {

            "tokenList" : tokenListPath,
            "poolList" : poolListPath,
            "marketList" : marketListPath,
            "chainInfo" : chainInfoPath,
            "chainAbi" : chainAbi,
            "factoryAbi" : factoryAbi,
            "routerAbi" : routerAbi
        
        }
    }

klaytn = klayswap(config)

# balance = klaytn.fetch_balance()

# swap = klaytn.create_swap(1, 'MOOI' , 0.3, 'oUSDT', 'KlaySwap')

abi = ABI()
abi.get_abi_by_filename(fname = 'chain')

# print(swap)
