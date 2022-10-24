import re
import itertools

from ccdxt.base import Chain, Market, Pool, Token, Transaction
from ccdxt.base.utils.errors import ABIFunctionNotFound, RevertError, AddressError, NotSupported
from ccdxt.base.utils.validation import *
from ccdxt.base.utils import SafeMath
from eth_account import Account
from decimal import Decimal

from typing import Optional, Union, Tuple, Callable, Any
from eth_typing.evm import Address
from eth_typing import ChecksumAddress
from eth_abi.exceptions import DecodingError
# from decimal import Decimal

from web3 import Web3
from web3.eth import AsyncEth
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS
from web3._utils.abi import get_abi_output_types, map_abi_data
from web3.middleware import async_geth_poa_middleware,geth_poa_middleware, construct_sign_and_send_raw_middleware
from web3.types import TxParams, FunctionIdentifier, BlockIdentifier, ABI, ABIFunction, CallOverrideParams
from web3._utils.contracts import prepare_transaction, find_matching_fn_abi
from web3.contract import Contract, ContractFunction, ACCEPTABLE_EMPTY_STRINGS
from web3.exceptions import BadFunctionCallOutput

import asyncio
import logging

class Exchange(Transaction):
    """Base exchange class"""

    def __init__(self):

        #chain info
        self.chains : Optional[dict] = None
        self.network_path : Optional[str] = None
        self.baseDecimal = 18

        #market info
        self.id = None
        self.chainName : Optional[str] = None
        self.exchangeName : Optional[str] = None
        self.rateLimit : Optional[int] = 2000  # milliseconds = seconds * 1000
        self.markets : Optional[dict] = None
        self.tokens : Optional[dict] = None
        
        #etc
        self.unlimit = 115792089237316195423570985008687907853269984665640564039457584007913129639935
        
        #private info
        self.privateKey : Optional[str] = None  # a "0x"-prefixed hexstring private key for a wallet
        self.account : Union[Address, str, None] = None  # the wallet address "0x"-prefixed hexstring
        
        #log
        self.log = './logfile.log'

        logging.basicConfig(level=logging.INFO,
                            filename=self.log,
                            filemode="w",
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    async def call_contract_function(
            self,
            web3: Web3,
            address: ChecksumAddress,
            normalizers: Tuple[Callable[..., Any], ...],
            function_identifier: FunctionIdentifier,
            transaction: TxParams,
            block_id: Optional[BlockIdentifier] = None,
            contract_abi: Optional[ABI] = None,
            fn_abi: Optional[ABIFunction] = None,
            state_override: Optional[CallOverrideParams] = None,
            fn_args: Any = [],
            fn_kwargs: Any = {}) -> Any:
        """
        Helper function for interacting with a contract function using the
        `eth_call` API.
        """
        print(fn_abi)
        call_transaction = prepare_transaction(
            address,
            web3,
            fn_identifier=function_identifier,
            contract_abi=contract_abi,
            fn_abi=fn_abi,
            transaction=transaction,
            fn_args=fn_args,
            fn_kwargs=fn_kwargs,
        )

        return_data = await web3.eth.call(
            call_transaction,
            block_identifier=block_id,
            state_override=state_override,
        )

        if fn_abi is None:
            fn_abi = find_matching_fn_abi(contract_abi, web3.codec, function_identifier, fn_args, fn_kwargs)

        output_types = get_abi_output_types(fn_abi)

        try:
            output_data = web3.codec.decode_abi(output_types, return_data)
        except DecodingError as e:
            # Provide a more helpful error message than the one provided by
            # eth-abi-utils
            is_missing_code_error = (
                return_data in ACCEPTABLE_EMPTY_STRINGS
                and web3.eth.get_code(address) in ACCEPTABLE_EMPTY_STRINGS)
            if is_missing_code_error:
                msg = (
                    "Could not transact with/call contract function, is contract "
                    "deployed correctly and chain synced?"
                )
            else:
                msg = (
                    f"Could not decode contract function call to {function_identifier} with "
                    f"return data: {str(return_data)}, output_types: {output_types}"
                )
            raise BadFunctionCallOutput(msg) from e

        _normalizers = itertools.chain(
            BASE_RETURN_NORMALIZERS,
            normalizers,
        )
        normalized_data = map_abi_data(_normalizers, output_types, output_data)

        if len(normalized_data) == 1:
            return normalized_data[0]
        else:
            return normalized_data
        
    async def call_function(self, function: ContractFunction, tx_kwargs=None, block_id=None):
        tx: TxParams = {}
        if not tx_kwargs:
            tx_kwargs = {}
        tx.update(tx_kwargs)
        # tx["data"] = function._encode_transaction_data()
        tx["to"] = self.account
        return await self.call_contract_function(
            web3=self.w3,
            address=self.account,
            transaction=tx,
            normalizers=tuple(),
            function_identifier=function.function_identifier,
            contract_abi=None,
            fn_abi=function.abi,
            fn_args=function.args,
            fn_kwargs=function.kwargs,
            block_id=block_id,
            # **kwargs,
        )
        
    async def block_number(self) -> str:
        """
        Returns
        -------
        result: Block number
        """
        return self.w3.eth.block_number
    
    async def get_contract(self, address : str ,abi : dict) :
        '''
        Parameters
        ----------
        address : Contract address
        abi : Contract abi
        
        Returns
        -------
        result: a contract object.
        '''
        
        # if is_score_address(address) :
        
        return self.w3.eth.contract(address, abi = abi)
        
        # else:load_exchange
        #     raise AddressError("Address is wrong.")
    
    def decimals(self, tokenSymbol):
        '''
        Parameters
        ----------
        tokenSymbol : token symbol
        
        Returns
        -------
        result: decimals of token
        '''
        
        token = self.tokens[tokenSymbol]
        tokenAddress = self.set_checksum(token["contract"])
        
        if self.tokens[tokenSymbol]['decimals'] :
            return int(self.tokens[tokenSymbol]['decimals'])

        try:
            tokenContract = self.get_contract(tokenAddress, self.chains['chainAbi'])
            
            if "decimals" not in self.tokens[tokenSymbol] :
            
                decimals = tokenContract.functions.decimals().call()
                self.tokens[tokenSymbol]["decimals"] = decimals
                
                # self.save_token(self.tokens)
            
            else :
                decimals = self.tokens[tokenSymbol]["decimals"]
                
            return int(decimals)
        except ABIFunctionNotFound:
            return 18
        
    def __exist(self, tokenAsymbol, tokenBsymbol):

        pair_address = self.getPair(tokenAsymbol, tokenBsymbol)
        return int(pair_address, 16) != 0
        
    async def get_pool(self, tokenAsymbol, tokenBsymbol):

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        
        try:
            factoryContract = await self.get_contract(routerAddress, self.markets['factoryAbi'])
            
            token_sort = sorted([tokenAsymbol, tokenBsymbol])
            
            pool_name = token_sort[0] + '-' + token_sort[1]
        
            if pool_name not in self.pools :

                pair = await factoryContract.functions.tokenToPool(tokenAaddress, tokenBaddress).call()
                
                self.pools = self.deep_extend(self.pools, 
                            {
                                pool_name : {
                                    "name" : pool_name,
                                    "baseChain" : {
                                        self.chainName : {
                                            self.exchangeName : pair
                                        }
                                    }
                                }
                                
                            })
                # Pool().save_pool(self.pools)
            else :
                pair = dict(self.pools[pool_name])['poolAddress']
            return pair
        except ABIFunctionNotFound:
            return print("No ABI found")
        
    async def get_pair(self, tokenAsymbol, tokenBsymbol):

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        
        try:
            factoryContract = await self.get_contract(routerAddress, self.markets['factoryAbi'])
            
            token_sort = sorted([tokenAsymbol, tokenBsymbol])
            
            pool_name = token_sort[0] + '-' + token_sort[1]

            if pool_name not in self.pools :

                pair = await self.call_function(factoryContract.functions.getPair(tokenAaddress, tokenBaddress))
                
                self.pools = self.deep_extend(self.pools, 
                            {
                                pool_name : {
                                    "name" : pool_name,
                                    "baseChain" : {
                                        self.chainName : {
                                            self.exchangeName : pair
                                        }
                                    }
                                }
                                
                            })
                # Pool().save_pool(self.pools)
            else :
                pair = dict(self.pools[pool_name])['poolAddress']
            return pair
        except ABIFunctionNotFound:
            return print("No ABI found")
    
    def reversed(self,tokenAaddress,tokenBaddress) :
        
        try:
            factoryContract = self.get_contract(tokenAaddress, self.markets['factoryAbi'])

            pair = factoryContract.functions.tokenA(tokenAaddress).call()
            self.__pairs[tokenAaddress + tokenBaddress] = pair
            return pair
        except ABIFunctionNotFound:
            return print("No ABI found")
    
    def reserve_ratio(self, input = None, output = None, intermediate = None, refresh = False):
        reserves = self.reserves(input, output, intermediate, refresh)
        if self.reversed(input, output):
            return reserves[0] / reserves[1]
        else:
            return reserves[1] / reserves[0]
        
    def getAmountsOut(self, amount, path):
        return self.router_contract.functions.getAmountsOut(int(amount), path).call()[-1]
    
    def sync(self, tokenAsymbol, tokenBsymbol):
        pair = self.getPair(tokenAsymbol, tokenBsymbol)
        contract = self.w3.eth.contract(self.set_checksum(pair), self.chains['chainAbi'])
        return contract.functions.sync().call()
    
    def require(self, execute_result: bool, msg: str):
        if not execute_result:
            RevertError(msg)
    
    def decode(self,tx_hash) :
        
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])
        
        transaction = self.w3.eth.getTransaction(tx_hash)
        
        result = routerContract.decode_function_input(transaction.input)
        
        return result
    
    async def allowance(self, tokenSymbol):
        
        token = self.tokens[tokenSymbol]
        tokenAddress = self.set_checksum(token["contract"])
        account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets['routerAbi'])
        
        contract = self.w3.eth.contract(tokenAddress, self.chains['chainAbi'])
        return await self.call_function(contract.functions.allowance(account, routerAddress))
        
    def fees(self, input = None, output = None, intermediate = None, amount = 1):
        ratio = self.reserve_ratio(input, output, intermediate)
        amount = amount * self.decimals(input)
        price = self.price(amount, input, output, intermediate)
        price = price / self.decimals(output)
        return 1 - price / ratio
    
    def estimate_gas(self):
           return self.w3.eth.gasPrice / 1000000000
        
    async def partial_balance(self, tokenSymbol : str) -> dict :
        
        token = self.tokens[tokenSymbol]
        
        accountAddress = self.set_checksum(self.account)
        
        if token == self.chains['baseCurrency']:
            balance = await self.w3.eth.getBalance(accountAddress)
            
            balance = self.to_value(balance, self.baseDecimal)
        
        else :
            
            tokenAaddress = self.set_checksum(token["contract"])
            
            tokenContract = await self.get_contract(tokenAaddress, self.chains['chainAbi'])
            
            balance = await tokenContract.functions.balanceOf(accountAddress).call()
            
            balance = self.to_value(balance, int(token["decimals"]))
        
        result = {
            
            "symbol" : token["symbol"],
            "balance" : balance
            
        }
        
        return result
    
        # return balance
        
    def get_TransactionCount(self,address : str) :
        
        nonce = self.w3.eth.getTransactionCount(address)
        
        return nonce

    def fetch_tokens(self):

        return self.tokens

    async def fetch_balance(self, tokens = None) :
        
        result = []
        
        if tokens is not None:
            
            if is_list(tokens) :
            
                symbols = tokens
                
            else :
                symbols = list(tokens)
        else :
        
            symbols = list(self.tokens.keys())
            
        # balance_list = [self.partial_balance(symbol) for symbol in symbols]
            
        # result.append[await asyncio.gather(*balance_list)]
        
        for symbol in symbols :
            
            balance = await self.partial_balance(symbol)
            result.append(balance)
            
        return  result
    
    def create_swap(self,amountA, tokenA, amountBMin, tokenB) :
        raise NotSupported('create_swap() is not supported yet')
    
    def check_approve(self, amountA : int, token : str, account : str, router : str)  :
        
        '''
        Check token approved and transact approve if is not
        
        Parameters
        ----------
        token : token address
        account : account address
        routerAddress: LP pool owner who allow
        '''
        
        if (token == self.baseCurrncy) :
            return
        
        contract = self.get_contract(token, self.chains['chainAbi'])
        
        approvedTokens = contract.functions.allowance(account,router).call()
        
        if approvedTokens < amountA :
           
           tx = self.get_approve(token, router)
           
           tx_receipt = self.fetch_transaction(tx, round = "CHECK")

           return tx_receipt
           
        else : return
        
    def get_approve(self,token : str, router : str) :
        
        contract = self.get_contract(token, self.chains['chainAbi'])
        
        nonce = self.get_TransactionCount(self.account)
        
        tx = contract.functions.approve(router, self.unlimit).buildTransaction(
            {
                "from" : self.account,
                "nonce": nonce,
                # "gasPrice" : self.w3.toWei(10,'gwei')
                # 'maxFeePerGas': self.w3.toWei(20,'gwei'),
                # 'maxPriorityFeePerGas': self.w3.toWei(20,'gwei'),
            }
        )
        
        return tx
        
    def load_exchange(self,chainName,exchangeName=None):
        
        self.load_chains(chainName)
        self.load_markets(chainName, exchangeName)
        self.load_pools(chainName, exchangeName)
        self.load_tokens(chainName, exchangeName)
        
        # self.w3 = self.set_async_network(self.chains['mainnet']['public_node'])
        
        self.w3 = self.set_network(self.chains['mainnet']['public_node'])
        
        self.baseCurrncy = self.chains['baseContract']
        
    def load_multicall(self,chainName):
        
        self.load_chains(chainName)
        self.load_all()
        
        self.w3 = self.set_async_network(self.chains['mainnet']['public_node'])
        self.baseCurrncy = self.chains['baseContract']
    
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
           
    def load_bridge(self, chainName, bridgeName):
        
        markets = self.set_markets(chainName,bridgeName)

        self.bridge = {}

        if markets :
           self.bridge = self.deep_extend(self.safe_market(),markets)
           
    def load_pools(self, chainName, exchangeName):
        
        pools = self.set_pools(chainName,exchangeName)

        self.pools = {}

        if pools :
           self.pools = self.deep_extend(self.safe_market(),pools)
            
    def load_tokens(self, chainName, exchangeName):
        
        tokens = self.set_tokens(chainName,exchangeName)

        self.tokens = {}

        for token in tokens :

            self.tokens[token] = self.deep_extend(self.safe_token(), tokens[token])
            
    def load_all(self) :
        
        # self.all_chains = self.set_all_chains()
        self.all_markets = self.set_all_markets()
        self.all_pools = self.set_all_pools()
        self.all_tokens = self.set_all_tokens()

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if is_dict(arg):
                if not is_dict(result):
                    result = {}
                for key in arg:
                    result[key] = Exchange.deep_extend(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result
    
    @staticmethod
    def safe_chain():
        return Chain().__dict__

    @staticmethod
    def safe_market():
        return Market().__dict__
    
    @staticmethod
    def safe_pool():
        return Pool().__dict__
    
    @staticmethod
    def safe_token():
        return Token().__dict__
    
    @staticmethod
    def set_chains(chainName):
        return Chain().set_chain(chainName)
    
    @staticmethod
    def set_markets(chainName,exchangeName):
        return Market().set_market(chainName,exchangeName)
    
    @staticmethod
    def set_pools(chainName,exchangeName):
        return Pool().set_pool(chainName,exchangeName)
    
    @staticmethod
    def set_tokens(chainName,exchangeName):
        return Token().set_token(chainName,exchangeName)

    @staticmethod
    def set_all_chains():
        return Chain().set_all_chains()
    
    @staticmethod
    def set_all_markets():
        return Chain().set_all_chains()
    
    @staticmethod
    def set_all_pools():
        return Chain().set_all_chains()
    
    @staticmethod
    def set_all_tokens():
        return Chain().set_all_chains()
    
    # @staticmethod
    # def set_multicall():
    #     return Multicall().set_multicall()
    
    # @staticmethod
    # def save_token(tokens):
    #     return Token().save_token(tokens)
    
    @staticmethod
    def set_network(network_path) :
        return Web3(Web3.HTTPProvider(network_path, request_kwargs={"timeout": 60}))
    
    @staticmethod
    def set_async_network(network_path) :
        return Web3(Web3.AsyncHTTPProvider(network_path, request_kwargs={"timeout": 60}), \
               modules={'eth': (AsyncEth,)}, middlewares=[])
    
    @staticmethod
    def set_checksum(value) :
        return Web3.toChecksumAddress(value)
    
    def set_pos(self) :
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        # account = Account.from_key(self.privateKey)
        # self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    
    @staticmethod
    def from_value(value : float or int, exp : int=18) -> int :
        return int(round(SafeMath.mul(value, 10 ** exp)))

    @staticmethod
    def to_value(value : float or int, exp : int=18)-> Decimal :  
        return round(SafeMath.div(float(Decimal(value)), 10 ** exp),6)
    
    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    

