import os
from pathlib import Path

from ..base.exchange import Exchange
from ..base.utils.errors import (
    InsufficientBalance,
)
from ..base.utils.retry import retry

from web3.exceptions import BadResponseFormat
from web3.logs import DISCARD
from TonTools import *
from tonsdk.utils import *
from tonsdk.boc import begin_cell

import asyncio
from typing import Optional
from eth_typing.evm import ChecksumAddress
import requests
import datetime
import json
import logging
import binascii


class Orbitbridge(Exchange):
    has = {
        "create_bridge": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "retries": 3,
            "retriesTime": 10,
            "host": 0,
            "account": None,
            "privateKey": None,
            "mnemonics": None,
            "tag" : None,
            "log": None,
            "toncenter_api_key": None,
            "tonapi_api_key": None,
            "api_url": "https://bridge.orbitchain.io/",
            "tag_file_path": "",
            "ton_vault_bridge_address" : None,
            "ton_minter_bridge_address" : None,
            "ton_eth_bridge_address" : None,
            "ton_klaytn_bridge_address" : None,
            "ton_matic_bridge_address" : None,
            "ton_bnb_bridge_address" : None,
        }

        config.update(config_change)

        # market info
        self.id = 3
        # self.chainName = "ORBIT"
        self.chainName = "MATIC"
        self.exchangeName = "orbitbridge"
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.mnemonics = config["mnemonics"]
        self.tag = config["tag"]
        self.log = config["log"]
        self.toncenter_api_key = config["toncenter_api_key"]
        self.tonapi_api_key = config["tonapi_api_key"]
        self.api_url = config["api_url"]
        self.ton_vault_bridge_address = config["ton_vault_bridge_address"]
        self.ton_minter_bridge_address = config["ton_minter_bridge_address"]
        self.ton_eth_bridge_address = config["ton_eth_bridge_address"]
        self.ton_klaytn_bridge_address = config["ton_klaytn_bridge_address"]
        self.ton_matic_bridge_address = config["ton_matic_bridge_address"]
        self.ton_bnb_bridge_address = config["ton_bnb_bridge_address"]

        # self.load_bridge(self.exchangeName)
        # self.set_logger(self.log)

    @retry
    async def create_bridge(
        self, amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, toAddr, *args, **kwargs
    ):
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

        await self.load_bridge(self.exchangeName)
        await self.load_exchange(fromChain, self.exchangeName)

        token = self.tokens[from_tokenSymbol]

        self.bridge["baseCurrency"] = self.bridge["baseChain"][fromChain]["baseCurrency"]
        self.bridge["bridgeAbi"] = self.bridge["bridgeAbi"][token["bridge"]]
        self.bridge["bridgeAddress"] = self.bridge["bridgeAddress"][
            f"{token['chain']}_{token['bridge']}"
        ]

        self.tokenSymbol = from_tokenSymbol
        self.to_tokenSymbol = to_tokenSymbol

        self.fromChain = fromChain
        self.chainName = fromChain
        self.toChain = toChain
        self.amount = amount
        base_token = self.tokens[self.chains["baseCurrency"]]

        if fromChain == "TON":

            await self.run_bridge_ton(from_tokenSymbol, amount, toChain, toAddr)

            return
        
        amount = self.from_value(value=amount, exp=int(token["decimals"]))

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        token["MinimumBridge"] = 0

        self.require(fromChain == toChain, ValueError("Same Chain"))

        if "fee" in kwargs:
            fee = kwargs["fee"]

        else:
            fee = 0

        tokenAddress = self.set_checksum(token["contract"])
        self.account = self.set_checksum(self.account)
        self.toAddrress = self.set_checksum(toAddr)

        bridgeAddress = self.set_checksum(self.bridge["bridgeAddress"])

        bridgeAddress = self.set_checksum(bridgeAddress)

        build = {
            "from": self.account,
            "nonce": self.nonce,
        }

        if (fromChain == "KLAYTN") & (toChain == "MATIC"):

            token["additionalGasFee"] = 0.5

        elif (fromChain == "MATIC") & (toChain == "KLAYTN"):

            token["additionalGasFee"] = 0.1
            self.maxPriorityFee, self.maxFee = await self.updateTxParameters()

            build["maxPriorityFeePerGas"] = int(self.maxPriorityFee)
            build["maxFeePerGas"] = int(self.maxFee)

        if "additionalGasFee" in token:

            baseCurrency = await self.partial_balance(self.chains["baseCurrency"])
            tokenBalance = await self.partial_balance(from_tokenSymbol)

            self.additionalGasFee = token["additionalGasFee"]

            self.require(
                self.additionalGasFee >= baseCurrency["balance"],
                InsufficientBalance(baseCurrency, token["additionalGasFee"]),
            )

            self.require(
                token["MinimumBridge"] >= tokenBalance["balance"],
                InsufficientBalance(tokenBalance, token["MinimumBridge"]),
            )

            self.additionalGasFee = self.from_value(
                value=self.additionalGasFee, exp=int(base_token["decimals"])
            )

        await self.check_approve(
            amount=amount,
            token=tokenAddress,
            account=self.account,
            router=bridgeAddress,
            build=build,
        )

        build["value"] = self.additionalGasFee

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        build["nonce"] = self.nonce

        self.routerContract = await self.get_contract(bridgeAddress, self.bridge["bridgeAbi"])

        if token["bridge"] == "Vault":

            if from_tokenSymbol == self.baseCurrency:

                tx = await self._ethDepositToken(toChain, self.toAddrress, amount, build=build)

            else:

                tx = await self._depositToken(
                    tokenAddress, toChain, self.toAddrress, amount, build=build
                )

        elif token["bridge"] == "Minter":

            tx = await self._requestSwap(
                tokenAddress, toChain, self.toAddrress, amount, build=build
            )

        tx_receipt = await self.fetch_transaction(tx, round="BRIDGE", api=token["bridge"])

        return tx_receipt

    @retry
    async def create_desTag(self, fromChain, *args, **kwargs):
        try:
            result = int(
                await self.create_request(
                    self.api_url,
                    {},
                    "open",
                    "v1",
                    "api",
                    "xrp",
                    "tagRequest",
                    fromChain,
                    self.account,
                )["tag"]
            )

        except:
            result = kwargs["tag"]

        return result

    async def _requestSwap(
        self,
        tokenAddress: ChecksumAddress,
        toChain: str,
        toAddr: ChecksumAddress,
        amount: int,
        build: dict,
        destinationTag: ChecksumAddress = None,
    ):

        if destinationTag:
            tx = await self.routerContract.functions.requestSwap(
                tokenAddress, toChain, toAddr, amount, destinationTag
            ).build_transaction(build)

        else:

            tx = await self.routerContract.functions.requestSwap(
                tokenAddress, toChain, toAddr, amount
            ).build_transaction(build)

        return tx

    async def _ethDepositToken(
        self,
        toChain: str,
        toAddr: ChecksumAddress,
        amount: int,
        build: dict,
    ):

        build["value"] += amount

        tx = await self.routerContract.functions["deposit"](toChain, toAddr).build_transaction(
            build
        )

        return tx

    async def _depositToken(
        self,
        tokenAddress: ChecksumAddress,
        toChain: str,
        toAddr: ChecksumAddress,
        amount: int,
        build: dict,
    ):

        tx = await self.routerContract.functions["depositToken"](
            tokenAddress, toChain, toAddr, amount
        ).build_transaction(build)

        return tx

    # @retry
    async def check_bridge_completed(self, amount, toChain, tokenSymbol, toAddr, *args, **kwargs):

        await self.load_bridge(self.exchangeName)
        await self.load_exchange(toChain, self.exchangeName)

        start_bridge = datetime.datetime.now()

        current_account = self.account

        self.account = toAddr

        start_balance = await self.partial_balance(tokenSymbol)

        if "fee" in kwargs:
            fee = amount * kwargs["fee"] * 0.01

        else:
            fee = 0

        while True:
            current_time = datetime.datetime.now()

            current_balance = await self.partial_balance(tokenSymbol)

            if (
                ((current_balance["balance"] - start_balance["balance"]) >= ((amount - fee)))
                or (current_balance["balance"] >= (amount - fee))
                # or (current_time - start_time).seconds > self.timeOut
            ):
                break

            else:

                await asyncio.sleep(30)

        end_bridge = datetime.datetime.now()

        bridge_time = (end_bridge - start_bridge).seconds

        time_spend = {"bridge_time": bridge_time}

        self.account = current_account

        balance = self.from_value(current_balance["balance"], await self.decimals(tokenSymbol))

        return time_spend, balance

    async def decode(self, tokenSymbol, fromChain, tx_hash):
        await self.load_bridge(self.exchangeName)
        await self.load_exchange(fromChain, self.exchangeName)

        token = self.tokens[tokenSymbol]

        self.bridge["bridgeAbi"] = self.bridge["bridgeAbi"][token["bridge"]]

        self.bridge["bridgeAddress"] = self.bridge["bridgeAddress"][
            f"{token['chain']}_{token['bridge']}"
        ]

        bridgeAddress = self.set_checksum(self.bridge["bridgeAddress"])

        bridgeAddress = self.set_checksum(bridgeAddress)

        routerContract = await self.get_contract(bridgeAddress, self.bridge["bridgeAbi"])

        transaction = await self.w3.eth.get_transaction(tx_hash)

        # result = routerContract.decode_function_input(transaction["input"])

        bridge = routerContract.events["Transfer"]()

        result = bridge.process_log(tx_hash)

        # result = bridge.process_receipt(transaction, errors=DISCARD)

        # result = result[1]
        # result = deposit.processReceipt(tx_hash,errors=DISCARD)

        return result

    async def run_bridge_ton(self, from_tokenSymbol, amount, toChain, toAddress):

        self.set_ton_client()
        self.set_ton_wallet(self.mnemonics)
        await self.create_bridge_ton(from_tokenSymbol, amount, toChain, toAddress)
        
    async def create_bridge_ton(
        self,
        from_tokenSymbol : str,
        amount: float,
        toChain : str,
        toAddress : str
    ):

        token = self.tokens[from_tokenSymbol]

        tokenAddress = token["contract"]
        
        current_seqno = await self.tool_wallet.get_seqno()
        self.seqno = current_seqno + self.addNounce
        
        if token["bridge"] == "Vault":
            
            if token['chain'] == 'TON' :
                bridge_address = self.ton_vault_bridge_address

            if from_tokenSymbol == self.baseCurrency:

                result = await self.tool_wallet.transfer_ton(destination_address=Address(bridge_address), amount=amount, message=self.tag)
                
                return result

            else:
                
                amount = self.from_value(value=amount, exp=int(token["decimals"]))
                
                body = self._create_deposit_body(
                    destination=Address(self.tool_wallet.address),
                    response_address=Address(self.bridge["bridgeAddress"]),
                    jetton_amount=amount,
                    query_id=0,
                    toChain=toChain,
                    toAddress=toAddress
                )

        elif token["bridge"] == "Minter":
            
            if token['chain'] == 'TON' :
                bridge_address = self.ton_minter_bridge_address
            elif token['chain'] == 'TON_ETH' :
                bridge_address = self.ton_eth_bridge_address
            elif token['chain'] == 'TON_KLAYTN' :
                bridge_address = self.ton_klaytn_bridge_address
            elif token['chain'] == 'TON_MATIC' :
                bridge_address = self.ton_matic_bridge_address
            elif token['chain'] == 'TON_BNB' :
                bridge_address = self.ton_bnb_bridge_address

            amount = self.from_value(value=amount, exp=int(token["decimals"]))
            
            body = self._create_request_body(
                destination=Address(self.tool_wallet.address),
                response_address=Address(token['contract']),
                jetton_amount=amount,
                query_id=0,
                toChain=toChain,
                toAddress=toAddress,
                tag=self.tag
            )
            
        else :
            
            ValueError("this kind of bridge isn`t supported")

        result = await self.create_transfer_message(body, Address(bridge_address), 0.14)
        
        return result
    
    def _create_deposit_body(
        self,
        destination: Address, # msg address
        response_address: Address,  # response_address (minter address)
        jetton_amount: int,
        query_id: int,
        toChain : str,
        toAddress : str
    ) -> Cell:
        
        toChain = binascii.hexlify(toChain.encode()).decode()
        
        return (
            begin_cell()
            .store_uint(260734629, 32)
            .store_uint(query_id, 64)
            .store_grams(jetton_amount)
            .store_address(destination)
            .store_address(response_address)
            # .store_grams("2600")
            .store_maybe_ref(None)
            .store_coins(2e7)
            .store_ref(
                begin_cell()
                .store_uint(0x4b4c4159544e, 256)
                .store_uint(toAddress, 160)
                .end_cell()
            )
            .end_cell()
        )

    def _create_request_body(
        self,
        destination: Address,
        response_address: Address,  # response_address (token address)
        jetton_amount: int,
        query_id: int,
        toChain : str,
        toAddress : str,
        tag
    ) -> Cell:
        
        toChain = binascii.hexlify(toChain.encode()).decode()
        toAddress = binascii.hexlify(toAddress.encode()).decode()

        return (
            begin_cell()
            .store_uint(1767081276, 32)
            .store_uint(query_id, 64)
            .store_ref(
                begin_cell()
                .store_address(response_address)
                .store_uint(0x4b4c4159544e, 256)
                .store_uint(0x8423a8d26c5C441AB1Ae072584bfA8D0a30f8549, 160)
                .store_uint(jetton_amount, 256)
                .end_cell()
            )
            .end_cell()
        )
        
        # return (
        #     begin_cell()
        #     .store_uint(0x6953853c, 32)
        #     # .store_uint(query_id, 64)
        #     .store_ref(
        #         begin_cell()
        #         .store_uint(0x595f07bc, 32)
        #         .store_uint(query_id, 64)
        #         .store_grams(jetton_amount)
        #         .store_address(response_address)
        #         # .store_uint(toChain, 256)
        #         # .store_uint(toAddress, 160)
        #         .store_string(toChain)
        #         .store_string(toAddress)
        #         .end_cell()
        #     )
        #     .end_cell()
        # )
    