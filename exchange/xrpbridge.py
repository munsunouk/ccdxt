import os
from pathlib import Path

from mars.base.exchange import Exchange
from mars.base.utils.errors import (
    InsufficientBalance,
)
from mars.base.utils.retry import retry
# from mars.base.utils.validation import *
from web3.exceptions import BadResponseFormat
from eth_typing.evm import ChecksumAddress
import requests
import random
import datetime
from typing import Optional
class Xrpbridge(Exchange):

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
        # self.chainName = "ORBIT"
        self.exchangeName = "xrpbridge"
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
        from_tokenSymbol: symbol of token input
        to_tokenSymbol : symbol of token output
        fromChain : name of chain token transfering
        toChain : name of chain token transfered
        toAddr : address of account of toChain`s chain

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

        token = self.tokens[from_tokenSymbol]
        
        
        self.require(fromChain == toChain, ValueError("Same Chain"))

        amount = self.from_value(value=amount, exp=int(token["decimals"]))

        tokenAddress = self.set_checksum(token["contract"])
        self.account = self.set_checksum(self.account)
        self.toAddrress = self.set_checksum(toAddr)
        bridgeAddress = self.bridge["type"]["XRP_bridge"]["bridgeAddress"]
        bridgeAddress = self.set_checksum(bridgeAddress)

        self.tokenContract = self.get_contract(tokenAddress, self.bridge["type"]["XRP_bridge"]["bridgeAbi"])
        self.routerContract = self.get_contract(bridgeAddress, self.bridge["type"]["XRP_bridge"]["bridgeAbi"])
        self.gasPrice = self.w3.toHex(25000000000)
        self.check_approve(
            amount=amount, token=tokenAddress, account=self.account, router=bridgeAddress
        )

        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

        xrp_deposit_address = kwargs['xrp_deposit_address']
        destinationTag = kwargs['destinationTag']
        six_random_number = random.randint(100000, 999999)
        
        tx = self._withdraw(xrp_deposit_address, destinationTag, amount, six_random_number)

        tx_receipt = self.fetch_transaction(tx, round="BRIDGE")
        
        self.load_exchange(toChain,  self.exchangeName)
        time_spend, amount = self.check_bridge_completed(to_tokenSymbol, self.toAddrress)

        return tx_receipt
    
    @retry
    async def create_desTag(self, fromChain, *args, **kwargs) :
                
        self.load_exchange(fromChain,  self.exchangeName)

        self.account = self.set_checksum(self.account)
        
        bridgeAddress = self.bridge["type"]["XRP_bridge"]["bridgeAddress"]
        bridgeAddress = self.set_checksum(bridgeAddress)
        self.routerContract = self.get_contract(bridgeAddress, self.bridge["type"]["XRP_bridge"]["bridgeAbi"])
        
        result = self.routerContract.functions.getAddressTagInfoByAddress(self.account).call()

        return int(result[1])

    def _withdraw(self, toAddrress, destinationTag, amount, nonce):

        tx = self.routerContract.functions.withdrawXrp_m(toAddrress, destinationTag, amount, nonce).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
                "gasPrice" : self.gasPrice,
            }
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
            
            if ((current_balance['balance'] - start_balance['balance']) > (self.amount // 2)) \
                or (current_balance['balance'] >= self.amount) \
                or (current_time - start_time).seconds > 1800 :
                
                break
                    
        end_bridge = datetime.datetime.now()
        
        bridge_time = (end_bridge - start_bridge).seconds
        
        time_spend = {
            'bridge_time' : bridge_time
        }
        
        self.account = current_account
        balance = self.from_value(current_balance['balance'], self.decimals(tokenSymbol))
        
        return time_spend, balance

    def decode(self, tokenSymbol, fromChain, tx_hash):

        self.load_bridge(self.exchangeName)
        self.load_exchange(fromChain,  self.exchangeName)
        
        bridgeAddress = self.bridge["type"]["XRP_bridge"]["bridgeAddress"]

        bridgeAddress = self.set_checksum(bridgeAddress)

        routerContract = self.get_contract(
            bridgeAddress, self.bridge["type"]["XRP_bridge"]["bridgeAbi"]
        )

        transaction = self.w3.eth.get_transaction(tx_hash)

        result = routerContract.decode_function_input(transaction.input)
        # result = result[1]

        # deposit = routerContract.events.SwapRequest()
        # deposit = routerContract.events.SwapNFT()

        # result = deposit.processReceipt(tx_hash,errors=DISCARD)

        return result

