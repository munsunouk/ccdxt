import os
from pathlib import Path
import datetime
import time

from mars.base.exchange import Exchange
from mars.base.utils.errors import (
    InsufficientBalance,
    NetworkError,
)
from mars.base.utils.retry import retry
from web3.logs import DISCARD, IGNORE

from typing import Optional
import logging

class Mooibridge(Exchange):

    has = {
        "create_bridge": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):

        super().__init__()

        config = {
            "retries" : 3,
            "retriesTime" : 10,
            "host" : None,
            "account" : None,
            "privateKey" : None,
            "log" : None,
        }
        
        config.update(config_change)
        

        # market info
        self.id = 3
        # self.chainName = "MOOI"
        self.exchangeName = "mooibridge"
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.load_bridge(self.exchangeName)
        self.set_logger(self.log)
        
    @retry
    async def create_bridge(self, amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, toAddr, *args, **kwargs):
        """
        Info
        ----------
        create bridge amount of token in fromChain to toChain`s toAddr after check approve

        Parameters
        ----------
        amount : token amount input
        tokenAsymbol: symbol of token input
        fromChain : name of chain token transfering
        toChain : name of chain token transfered
        toAddr : address of account of toChain`s chain
        args : toAddr privatekey

        Returns
        -------
        {
        'transaction_hash': '0x6ea0feb76b39e4a2b03e553b4fbbacf8aefb8e5a1f7911893891fc49e5d8db79',
        'status': 1,
        'block': 34314503,
        'timestamp': datetime.datetime(2022, 10, 14, 10, 18, 6, 614884),
        'function': <Function requestSwap(address,string,bytes,uint256)>,
        'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
        'amountIn': 0.622748,
        'tokenA': 'oZEMIT',
        'to': '0x9Abc3F6c11dBd83234D6E6b2c373Dfc1893F648D',
        'from_chain': 'MATIC',
        'to_chain': 'KLAYTN',
        'transaction_fee:': 0.009408398005397502
        }
        """
        
        
        self.load_exchange(fromChain, self.exchangeName)
        
        self.tokenSymbol = from_tokenSymbol
        self.fromChain = fromChain
        self.toChain = toChain
        self.amount = amount
        
        if from_tokenSymbol == 'MOOI' :
            
            from_tokenSymbol = 'wMOOI'
            token = self.tokens[from_tokenSymbol]
            
            self.chains["baseContract"] = token["contract"]
            
        else :
            
            token = self.tokens[from_tokenSymbol]
        
        self.require(fromChain == toChain, ValueError("Same Chain"))

        amount = self.from_value(value=amount, exp=int(token["decimals"]))

        tokenAddress = self.set_checksum(token["contract"])
        self.account = self.set_checksum(self.account)
        self.toAddrress = self.set_checksum(toAddr)
        bridgeAddress = self.bridge["type"]["MOOI_bridge"]["bridgeAddress"][fromChain]
        bridgeAddress = self.set_checksum(bridgeAddress)
        
        unwrapAddress = self.bridge["type"]["MOOI_bridge"]["bridgeAddress"][toChain]
        unwrapAddress = self.set_checksum(unwrapAddress)

        self.tokenContract = self.get_contract(tokenAddress, self.bridge["type"]["MOOI_bridge"]["bridgeAbi"])
        
        self.routerContract = self.get_contract(bridgeAddress, self.bridge["type"]["MOOI_bridge"]["bridgeAbi"])
        self.gasPrice = self.w3.toHex(25000000000)
        self.check_approve(
            amount=amount, token=tokenAddress, account=self.account, router=bridgeAddress
        )

        if fromChain == "MOOI":
            
            await self._create_wrap(amount)
            self.tokenSymbol = from_tokenSymbol
            tx_receipt = await self._create_transfer(amount)
            
            self.load_exchange(toChain, self.exchangeName)
            time_spend, amount = self.check_bridge_completed(to_tokenSymbol, toAddr)

        elif fromChain == "KLAYTN":

            tx_receipt = await self._create_transfer(amount)

            self.load_exchange(toChain, self.exchangeName)
            self.tokenSymbol = to_tokenSymbol
            
            token = self.tokens[from_tokenSymbol]
            
            if to_tokenSymbol == 'MOOI' :
                
                to_tokenSymbol = 'wMOOI'
            
            self.account = self.set_checksum(toAddr)
            self.privateKey = args[0]
            
            self.tokenContract = self.get_contract(tokenAddress, self.bridge["type"]["MOOI_bridge"]["bridgeAbi"])
            self.unwrapContract = self.get_contract(unwrapAddress, self.bridge["type"]["MOOI_bridge"]["bridgeAbi"])
            
            time_spend, amount = self.check_bridge_completed(to_tokenSymbol, toAddr)
            
            self.tokenSymbol = 'wMOOI'
            await self._create_unwrap(amount)

        return tx_receipt
    
    @retry
    async def _create_wrap(self, amount):
        
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        tx = self._deposit(amount)
        
        tx_receipt = self.fetch_transaction(tx, round="DEPOSIT")
        
        time.sleep(3)
        
        return tx_receipt
    
    @retry
    async def _create_unwrap(self, amount):
        
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce
        
        tx = self._withdraw(amount)
        
        tx_receipt = self.fetch_transaction(tx, round="WITHDRAW")
        
        return tx_receipt
    
    @retry
    async def _create_transfer(self, amount):

        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce
        
        tx = self._transfer(amount)
            
        tx_receipt = self.fetch_transaction(tx, round="BRIDGE")
        
        time.sleep(3)
        
        return tx_receipt

    def _deposit(self, amount):

        tx = self.tokenContract.functions.deposit().build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
                "gasPrice" : self.gasPrice,
                "value": amount,
            }
        )

        return tx
    
    def _withdraw(self, amount):

        tx = self.unwrapContract.functions.withdraw(amount).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
                "gasPrice" : self.gasPrice,
            }
        )

        return tx
    
    def _transfer(self, amount):
        
        data = []
        data = self.w3.toHex(bytes(data))
        
        params = {
            "from": self.account,
            "nonce": self.nonce,
        }
        
        if self.fromChain == 'MOOI' :
            
            params['gasPrice'] = self.gasPrice
            
        else :
            pass

        tx = self.tokenContract.functions.requestValueTransfer(amount, self.toAddrress, 0, data).build_transaction(
            params
        )

        return tx
        
    def check_bridge_completed(self, tokenSymbol, toAddr) :
        
        start_bridge = datetime.datetime.now()
        
        start_time = datetime.datetime.now()
        
        current_account = self.account
        
        self.account = toAddr
        
        start_balance = self.partial_balance(tokenSymbol)
        
        while True :
            
            current_time = datetime.datetime.now()
            
            current_balance = self.partial_balance(tokenSymbol)
            
            if ((current_balance['balance'] - start_balance['balance']) >= (self.amount)) \
                or (current_balance['balance'] >= self.amount)\
                or (current_time - start_time).seconds > self.timeOut :
                    
                if current_balance['balance'] - start_balance['balance'] > 0 :
                    
                    amount = current_balance['balance'] - start_balance['balance']
                    
                else :
                    
                    amount = self.amount

                break
                    
        end_bridge = datetime.datetime.now()
        
        bridge_time = (end_bridge - start_bridge).seconds
        
        time_spend = {
            'bridge_time' : bridge_time
        }
        
        self.account = current_account
        
        balance = self.from_value(amount, self.decimals(tokenSymbol))
        
        return time_spend, balance
    
    def decode(self, tokenSymbol, fromChain, tx_hash):

        self.load_bridge(self.exchangeName)
        self.load_exchange(fromChain, self.exchangeName)
        
        token = self.tokens[tokenSymbol]
        
        bridgeAddress = self.bridge["type"]["MOOI_bridge"]["bridgeAddress"][fromChain]
        bridgeAddress = self.set_checksum(bridgeAddress)

        bridgeContract = self.get_contract(bridgeAddress, self.bridge["type"]["MOOI_bridge"]["bridgeAbi"])

        transaction = self.w3.eth.get_transaction(tx_hash)

        result = bridgeContract.decode_function_input(transaction.input)
        
        # result = bridgeContract.decode_function_input("0x2e1a7d4d00000000000000000000000000000000000000000000004a873213a57ff80000")
        
        # result = result[1]

        # result = deposit.processReceipt(tx_hash,errors=DISCARD)

        return result

