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
import collections
import requests
import base64
from web3 import Web3
import datetime

class klayswap(Exchange):
    
    def __init__(self, config : dict) :
        
        #TODO private
        self.address = config["private"]["wallet"]["address"]
        self.privateKey = config["private"]["wallet"]["privateKey"]
        self.network_path = config["public"]["chainInfo"]["private_node"]

        self.markets = config["public"]["marketList"]
        self.tokens = config["public"]["tokenList"]
        self.pools = config["public"]["poolList"]
        
        self.chainAbi = config["public"]["chainAbi"]
        self.factoryAbi = config["public"]["factoryAbi"]
        self.routerAbi = config["public"]["routerAbi"]
        
        self.symbols = list(self.tokens.keys())
        
        self.get_provider()

    def get_provider(self) :
        
        self.w3 = Web3(Web3.HTTPProvider('https://public-node-api.klaytnapi.com/v1/cypress'))
        
    def fetch_tokens(self,tokens):
        
        #TODO
        # fetchCurrenciesEnabled = self.safe_value(self.options, 'fetchCurrencies')
        # if not fetchCurrenciesEnabled:
        #     return None
        
        result = tokens
        return result
    
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
    
    def set_contract(self,address : str ,abi : dict) :
        
        contract = self.w3.eth.contract(address, abi = abi)
        
        return contract
        
    def set_checksum(self,value) :
        
        result = Web3.toChecksumAddress(value)
        
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
        
    
    def functiontransaction(self,tx):
        
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
        
        last_block_number = self.w3.eth.block_number
        print(f'last block number in eth = {last_block_number}')
        
        signed_tx =self.w3.eth.account.signTransaction(tx, self.privateKey)
        
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        return self.w3.eth.waitForTransactionReceipt(tx_hash)
    
    # def set_balnace(self) :
    
            
    




    

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
        
    config = {

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

balance = klaytn.fetch_balance()

swap = klaytn.create_swap(1, 'MOOI' , 0.3, 'oUSDT', 'KlaySwap')

print(swap)
