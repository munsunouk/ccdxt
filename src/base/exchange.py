from src.base import Chain, Market, Token 
from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, TransactionNotFound, BadFunctionCallOutput
from typing import Optional, Type, Union
import json
from eth_typing import HexAddress
from web3.contract import Contract
from decimal import Decimal
from src.base.errors import NotSupported
from web3.datastructures import AttributeDict
from eth_tester.exceptions import TransactionFailed
import logging
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
        self.symbols = None
        
        self.factoryAbi = None
        self.routerAbi = None
        
        self.unlimit = 115792089237316195423570985008687907853269984665640564039457584007913129639935
        self.baseCurrncy  = '0x0000000000000000000000000000000000000000'
        
        #private info
        self.privateKey = ''  # a "0x"-prefixed hexstring private key for a wallet
        self.account = ''  # the wallet address "0x"-prefixed hexstring

        logging.basicConfig(level=logging.INFO,
                            filename=params['log'],
                            filemode="w",
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def block_number(self):
        return self.w3.eth.block_number
    
    def get_contract(self, address : str ,abi : dict) :
        '''
        Returns a contract object.
        '''
        return self.w3.eth.contract(address, abi = abi)
    
    def decimals(self, tokenSymbol):
        
        token = self.tokens[tokenSymbol]
        tokenAddress = self.set_checksum(token["contract"])
        
        if tokenAddress in self.__decimals:
            return self.__decimals[tokenAddress]

        try:
            tokenContract = self.get_contract(tokenAddress, self.chains['chainAbi'])
            decimals = tokenContract.functions.decimals().call()
            self.__decimals[tokenAddress] = decimals
            return decimals
        except ABIFunctionNotFound:
            return 18
        
    def __exist(self, tokenAsymbol, tokenBsymbol):

        pair_address = self.getPair(tokenAsymbol, tokenBsymbol)
        return int(pair_address, 16) != 0
    
    def getPair(self, tokenAsymbol, tokenBsymbol):

        if (tokenAsymbol + tokenBsymbol) in self.__pairs:
            return self.__pairs[tokenAsymbol + tokenBsymbol]
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        
        try:
            factoryContract = self.get_contract(tokenAaddress, self.markets['factoryAbi'])

            pair = factoryContract.functions.getPair(tokenAaddress, tokenBaddress).call()
            self.__pairs[tokenAaddress + tokenBaddress] = pair
        except ABIFunctionNotFound:
            return pair
    
    def __reserves(self, tokenAsymbol, tokenBsymbol):
        
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])

        pair_address = self.getPair(tokenBaddress, tokenAaddress)
        if pair_address in self.__pairs_reserves:
            return self.__pairs_reserves[pair_address]
        
        try:
        
            liqudityContract = self.get_contract(tokenAaddress, self.chains['chainAbi'])
            reserves = liqudityContract.functions.getReserves().call()
            if self.reversed(tokenAaddress, tokenBaddress):
                reserves[0] = reserves[0] / self.decimals(tokenBsymbol)
                reserves[1] = reserves[1] / self.decimals(tokenAsymbol)
            else:
                reserves[0] = reserves[0] / self.decimals(tokenAsymbol)
                reserves[1] = reserves[1] / self.decimals(tokenBsymbol)
            self.__pairs_reserves[pair_address] = reserves
            
            return reserves
        
        except ABIFunctionNotFound:
            raise NotSupported('fetch_tokens() is not supported yet')
        
    def reserves(self, input = None, output = None, intermediate = None, refresh = False):
        if intermediate is None:
            return self.__reserves(input, output, refresh)
        begin = self.__reserves(intermediate, input, refresh)
        end = self.__reserves(intermediate, output, refresh)
        if self.reversed(intermediate, input):
            begin = [ begin[1], begin[0] ]
        if self.reversed(intermediate, output):
            end = [ end[1], end[0] ]
        res = [ end[0] * begin[1], end[1] * begin[0]]
        if self.reversed(input, output):
            res = [ res[1], res[0] ]
        return res
    
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
    
    def decode(self,tx_hash) :
        
        routerAddress = self.set_checksum(self.markets["routerAddress"])
        routerContract = self.get_contract(routerAddress, self.markets['routerAbi'])
        
        transaction = self.w3.eth.getTransaction(tx_hash)
        
        result = routerContract.decode_function_input(transaction.input)
        
        return result
    
    def allowance(self, tokenSymbol):
        
        token = self.tokens[tokenSymbol]
        tokenAddress = self.set_checksum(token["contract"])
        account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets['routerAbi'])
        
        contract = self.client.eth.contract(tokenAddress, self.chains['chainAbi'])
        return contract.functions.allowance(account, routerAddress).call()
        
    def fees(self, input = None, output = None, intermediate = None, amount = 1):
        ratio = self.reserve_ratio(input, output, intermediate)
        amount = amount * self.decimals(input)
        price = self.price(amount, input, output, intermediate)
        price = price / self.decimals(output)
        return 1 - price / ratio
    
    def estimate_gas(self):
           return self.w3.eth.gasPrice / 1000000000
        
    def partial_balance(self, tokenSymbol : str) :
        
        token = self.tokens[tokenSymbol]
        
        tokenAaddress = self.set_checksum(token["contract"])
        accountAddress = self.set_checksum(self.account)
        
        tokenContract = self.get_contract(tokenAaddress, self.chains['chainAbi'])
        
        balance = tokenContract.functions.balanceOf(accountAddress).call()
        
        balance = self.to_value(balance, token["decimal"])
        
        result = {
            
            "symbol" : token["symbol"],
            "balance" : balance
            
        }
        
        return result
        
    def get_TransactionCount(self,address : str) :
        
        nonce = self.w3.eth.getTransactionCount(address)
        
        return nonce

    def fetch_tokens(self):

        return self.tokens

    def fetch_balance(self) :
        
        result = []
        
        symbols = list(self.tokens.keys())
        
        for symbol in symbols :
            
            balance = self.partial_balance(symbol)
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
        routerAddress: LP pool owner who allow
        '''
        
        if (token == self.baseCurrncy) :
            return
        
        contract = self.get_contract(token, self.chains['chainAbi'])
        
        approvedTokens = contract.functions.allowance(account,router).call()
        
        if approvedTokens < amountA :
           
           tx = self.get_approve(token, router)
           
           tx_receipt = self.fetch_transaction(tx)

           return tx_receipt
           
        else : return
        
    def get_approve(self,token : str, router : str) :
        
        contract = self.get_contract(token, self.chains['chainAbi'])
        
        nonce = self.get_TransactionCount(self.account)
        
        tx = contract.functions.approve(router, self.unlimit).buildTransaction(
            {
                "from" : self.account,
                "nonce": nonce,
            }
        )
        
        return tx
    
    def fetch_transaction(self, tx, routerContract):
        
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
        signed_tx =self.w3.eth.account.signTransaction(tx, self.privateKey)
        
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

        if tx_receipt["status"] != 1:

            return self.fetch_trade_fail(tx_hash)

        function, input_args = routerContract.decode_function_input(self.get_transaction_data_field(tx))
        path = input_args["path"]
        assert len(path), f"Seeing a bad path routing {path}"

        amount_in = input_args["amountIn"]
        amount_out_min = input_args["amountOutMin"]

        txDict = {
            
            'transaction_hash' : tx_receipt['transactionHash'].hex(),
            'status' : tx_receipt["status"],
            'block' :  tx_receipt['blockNumber'],
            'timestamp' : datetime.datetime.now(),
            'from' : tx_receipt['from'],
            'to' : tx_receipt['to'],
            'transaction_fee:' : tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18 ,
            
        }
        
        return tx_receipt
    
    def load_exchange(self,chainName,exchangeName):
        
        self.load_chains(chainName)
        self.load_markets(chainName, exchangeName)
        self.load_tokens(chainName, exchangeName)
        self.w3 = self.set_network(self.chains['mainnet']['public_node'])
    
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
            
    def load_tokens(self, chainName, exchangeName):
        
        tokens = self.set_tokens(chainName,exchangeName)

        self.tokens = {}

        for token in tokens :

            self.tokens[token] = self.deep_extend(self.safe_token(), tokens[token])

    def fetch_trade_fail(self,tx_hash) :

        tx = self.w3.eth.get_transaction(tx_hash)
    
        replay_tx = {
            "to": tx["to"],
            "from": tx["from"],
            "value": tx["value"],
            "data": self.get_transaction_data_field(tx),
        }

        # Replay the transaction locally
        try:
            result = self.w3.eth.call(replay_tx)
        except ValueError as e:
            self.logger.debug("Revert exception result is: %s", e)
            assert len(e.args) == 1, f"Something fishy going on with {e}"

            data = e.args[0]
            if type(data) == str:
                # BNB Smart chain + geth
                return data
            else:
                # Ganache
                # {'message': 'VM Exception while processing transaction: revert BEP20: transfer amount exceeds balance', 'stack': 'CallError: VM Exception while processing transaction: revert BEP20: transfer amount exceeds balance\n    at Blockchain.simulateTransaction (/usr/local/lib/node_modules/ganache/dist/node/1.js:2:49094)\n    at processTicksAndRejections (node:internal/process/task_queues:96:5)', 'code': -32000, 'name': 'CallError', 'data': '0x08c379a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002642455032303a207472616e7366657220616d6f756e7420657863656564732062616c616e63650000000000000000000000000000000000000000000000000000'}
                return data["message"]
        except TransactionFailed as e:
            # Ethereum Tester
            return e.args[0]

        # TODO:
        # Not sure why this happens.
        # When checking on bscchain:
        # This transaction has been included and will be reflected in a short while.

        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        if receipt.status != 0:
            self.logger.error("Queried revert reason for a transaction, but receipt tells it did not fail. tx_hash:%s, receipt: %s", tx_hash.hex(), receipt)

        current_block_number = self.w3.eth.block_number
        # TODO: Convert to logger record
        self.logger.error(f"Transaction succeeded, when we tried to fetch its revert reason. Hash: {tx_hash.hex()}, tx block num: {tx.blockNumber}, current block number: {current_block_number}, transaction result {result.hex()}. Maybe the chain tip is unstable?")
        return "<could not extract the revert reason>"

    def get_transaction_data_field(self,tx: AttributeDict) -> str:

        """Get the "Data" payload of a transaction.
        Ethereum Tester has this in tx.data while Ganache has this in tx.input.
        Yes, it is madness.
        Example:
        .. code-block::
            tx = web3.eth.get_transaction(tx_hash)
            function, input_args = router.decode_function_input(get_transaction_data_field(tx))
            print("Transaction {tx_hash} called function {function}")
        """
        if "data" in tx:
            return tx["data"]
        else:
            return tx["input"]


    
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
    def safe_chain():
        return json.dumps(Chain().__dict__)

    @staticmethod
    def safe_market():
        return json.dumps(Market().__dict__)
    
    @staticmethod
    def safe_token():
        return json.dumps(Token().__dict__)
    
    @staticmethod
    def set_chains(chainName):
        return Chain().set_chain(chainName)
    
    @staticmethod
    def set_markets(chainName,exchangeName):
        return Market().set_market(chainName,exchangeName)
    
    @staticmethod
    def set_tokens(chainName,exchangeName):
        return Token().set_token(chainName,exchangeName)
    
    @staticmethod
    def set_network(network_path) :
        return Web3(Web3.HTTPProvider(network_path))
    
    @staticmethod
    def set_checksum(value) :
        return Web3.toChecksumAddress(value)
    
    @staticmethod
    def from_value(value : float or int, exp : int=18) -> int :
        return int(round(value * 10 ** exp))

    @staticmethod
    def to_value(value : float or int, exp : int=18)-> Decimal :
        return round(float(Decimal(value) / Decimal(10 ** exp)),6)
    
    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value
    
