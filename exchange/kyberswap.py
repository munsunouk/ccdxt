from mars.base.exchange import Exchange
from mars.base.utils.errors import (
    InsufficientBalance,
)

from mars.base.utils.retry import retry
from typing import Optional
from web3.exceptions import BadResponseFormat

import requests
from requests.exceptions import HTTPError, ReadTimeout, ProxyError, SSLError, ConnectTimeout
from random import choice
# from proxy_requests.proxy_requests import ProxyRequests
import logging
import time
import os
from pathlib import Path
import asyncio
import datetime
from enum import Enum
from mars.base.utils import SafeMath 


class Kyberswap(Exchange):

    has = {
        "createSwap": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):

        super().__init__()

        config = {
            "chainName": "MATIC",
            "exchangeName": "kyberswap",
            "retries": 3,
            "retriesTime": 10,
            "host": None,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy" : False,
            "api_url" : "https://aggregator-api.kyberswap.com/",
            "sleep" : 10
        }

        config.update(config_change)

        # market info
        self.id = 1
        self.chainName = config["chainName"]
        self.exchangeName = config["exchangeName"]
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.proxy = config["proxy"]
        self.api_url = config["api_url"]
        self.sleep = config["sleep"]

        self.load_exchange(self.chainName, self.exchangeName)
        self.set_logger(self.log)
        
    @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol, **kwargs):
        
        await asyncio.sleep(self.sleep)
        
        amountIn = amountAin

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        
        tokenAaddress = tokenA["contract"]
        tokenBaddress = tokenB["contract"]
        
        amountA = self.from_value(value=amountAin, exp=int(tokenA["decimals"]))
        
        if tokenA["contract"] == self.chains['baseContract'] :
            tokenAaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            
        elif tokenB["contract"] == self.chains['baseContract'] :
            tokenBaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
 
        params = {
            "tokenIn": tokenAaddress,
            "tokenOut":tokenBaddress,
            "amountIn": amountA,
            "to": self.markets['routerAddress'],
            "saveGas" : 0,
            "gasInclude" : 1,
            "slippageTolerance" : 50,
            "clientData" : {"source":"DefiLlama"}
            
        }
        
        if self.proxy :
            
            quote_result = self.create_request(self.api_url, params, self.chains['baseChain'], 'route', 'encode', proxy=self.proxy)
            
        else :
        
            quote_result = self.create_request(self.api_url, params, self.chains['baseChain'], 'route', 'encode')
        
        amountout = self.to_value(
            value=quote_result["outputAmount"], exp=self.decimals(tokenBsymbol)
        )

        result = {
            "amountAin": amountAin,
            "amountBout": amountout,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
            "estimateGas": int(quote_result["totalGas"]),
            "quote_result" : quote_result,
        }

        return result

    @retry
    async def create_swap(self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs):
        """
        Parameters
        ----------
        amountA : tokenA amount input
        tokenAsymbol: symbol of token input
        amountBMin : tokenB amount output which is expactation as minimun
        tokenBsymbol : symbol of tokenB output
        Return
        {
        'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4',
        'status': 1,
        'block': 34314499,
        'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156),
        'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>,
        'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
        'amountIn': 0.1,
        'tokenA': 'USDC',
        'to': '0x10f4A785F458Bc144e3706575924889954946639',
        'amountOut': 0.623371,
        'tokenB': 'oZEMIT',
        'transaction_fee:': 0.023495964646856035
        }
        """
        
        await asyncio.sleep(self.retriesTime)

        if (path != None) and (len(path) > 2):

            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path[1:-1]]

        else:

            self.path = []

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA

        tokenBalance = self.partial_balance(self.tokenSymbol)
        baseCurrency = self.partial_balance(self.chains['baseCurrency'])
        
        self.require(self.amount > tokenBalance["balance"], InsufficientBalance(tokenBalance, f"need :{self.amount}"))
        self.require(
            1 > baseCurrency["balance"], InsufficientBalance(baseCurrency, f"need : 1")
        )
        # self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        amountBMin = self.from_value(value=amountBMin, exp=int(tokenB["decimals"]))
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        
        if tokenA["contract"] == self.chains['baseContract'] :
            tokenAaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            tokenAaddress = self.set_checksum(tokenAaddress)
            
        elif tokenB["contract"] == self.chains['baseContract'] :
            tokenBaddress = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            tokenBaddress = self.set_checksum(tokenBaddress)
            
        
        tokenApprove = self.set_checksum(tokenA["contract"])    
        accountAddress = self.set_checksum(self.account)

        routerAddress = self.set_checksum(self.markets["routerAddress"])
        tokenTransferAddress = self.set_checksum(self.markets["tokenTransferAddress"])

        self.check_approve(
            amount=amountA, token=tokenApprove, account=accountAddress, router=tokenTransferAddress
        )

        self.routerContract = self.get_contract(
            routerAddress, self.markets["routerAbi"][int(self.markets["version"])]
        )
        slippage = 50
        
        if kwargs :
                
            if "slippage" in kwargs :
                
                slippage = kwargs['slippage']

        tx = self.token_to_token(
            amountA, tokenA, tokenAaddress, tokenB, tokenBaddress, accountAddress, routerAddress, slippage
        )

        tx_receipt = self.fetch_transaction(tx, "SWAP")

        return tx_receipt                                          

    def get_proxy_list(self):
        
        pass
    
    def create_tx(self, accountAddress, routerAddress, quote_tx):
        
        self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce
        
        if self.chainName == "MATIC" :

            maxPriorityFeePerGas, maxFeePerGas = self.updateTxParameters()

            tx = {
                "from": accountAddress,
                "to": routerAddress,
                # "value": int(quote_tx["value"]),
                "maxPriorityFeePerGas": int(maxPriorityFeePerGas),
                "maxFeePerGas": int(maxFeePerGas),
                "data": quote_tx["encodedSwapData"],
                "nonce": self.nonce,
                "chainId": self.chains["mainnet"]["chain_id"],
            }
        
            gas = self.w3.eth.estimate_gas(tx)
            tx["gas"] = gas
            
        else :
            
            gasPrice = self.get_gasPrice()

            tx = {
                "from": accountAddress,
                "to": routerAddress,
                # "value": int(quote_tx["value"]),
                "gasPrice" : gasPrice,
                "data": quote_tx["encodedSwapData"],
                "nonce": self.nonce,
                "chainId": self.chains["mainnet"]["chain_id"],
                "gas" : int(quote_tx["estimatedGas"])
            }
        
        return tx
    
    def token_to_token(self, amountA, tokenA, tokenAaddress, tokenB, tokenBaddress, accountAddress, routerAddress, slippage):
        
        params = {
            "tokenIn": tokenAaddress,
            "tokenOut":tokenBaddress,
            "amountIn": amountA,
            "to": self.markets['routerAddress'],
            "saveGas" : 0,
            "gasInclude" : 1,
            "slippageTolerance" : slippage,
            "clientData" : {"source":"DefiLlama"}
            
        }
        
        if self.proxy :
            
            quote_tx = self.create_request(self.api_url, params, self.chains['baseChain'], 'route', 'encode', proxy=self.proxy)
            
        else :

            quote_tx = self.create_request(self.api_url, params, self.chains['baseChain'], 'route', 'encode')
        
        tx = self.create_tx(accountAddress, routerAddress, quote_tx)

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
            
            if ((current_balance['balance'] - start_balance['balance']) > (self.amount)) \
                or (current_balance['balance'] >= self.amount)\
                or (current_time - start_time).seconds > 1800 :
                    
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
    
    def get_gasPrice(self):
        
        r = requests.get(
            f"https://api.paraswap.io/prices/gas/{self.chains['mainnet']['chain_id']}?eip1559=false"
        )
        
        if r.status_code == 200:

            gas = r.json()

        else:
            raise BadResponseFormat(f"openocean api failed : {r.text}")
        
        fast_gas = gas["fast"]

        return int(fast_gas)
    
    def get_transaction(self, tx_hash) :
        
        r = requests.get(
            f"https://open-api.openocean.finance/v3/{self.chains['baseChain']}/getTransaction?hash={tx_hash}"
        )
        
        if r.status_code == 200:

            raw_receipt = r.json()

        else:
            raise BadResponseFormat(f"openocean api failed : {r.text}")
        
        txDict = {
            "from_network" : self.chains['name'],
            "to_network" : self.chains['name'],
            "tx_hash": raw_receipt['data']['tx_hash'],
            "status": 3, #pending
            "block": raw_receipt['data']['block_number'],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": None,
            "from_address": None,
            "amount_in": raw_receipt['data']['in_amount_value'],
            "token_in": self.tokenSymbol,
            "to_address": None,
            "amount_out": raw_receipt['data']['out_amount_value'],
            "token_out": self.tokenBsymbol,
            "gas_fee": raw_receipt['data']['tx_fee'],
            'tx_scope': None
        }

        return txDict
    
    @retry
    async def add_liquidity(
            self,
            tokenAsymbol,
            tokenBsymbol,
            amountA,
            amountB,
            amountSlippage,
            priceSlippage,
            number_bins,
            fee: int = 3_000,
            *args, **kwargs
        ):
        """
        add liquidity to pool and mint position nft
        """
        
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))
        
        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA_value
        self.input = {
            "tokenAsymbol" : tokenAsymbol,
            "tokenBsymbol" : tokenBsymbol,
            "amountA" : amountA_value,
            "amountB" : amountB_value,
            "amountSlippage" : amountSlippage,
            "priceSlippage" : priceSlippage,
            "number_bins" : number_bins,
        }
        
        self.pool_name = f"{tokenAsymbol}-{tokenBsymbol}"
        
        self.require(f"{self.pool_name}" not in self.pools, ValueError("can`t find any available pairs in mars"))
        
        pool = self.pools[f"{self.pool_name}"]

        if "isV3" in pool :
            
            isV3 = pool['isV3']
            
        else :
            
            isV3 = False
            
        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA_value = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        amountB_value = self.from_value(value=amountB, exp=int(tokenB["decimals"]))
        
        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        factoryAddress = self.set_checksum(self.markets["factoryAddress"][int(isV3)])
        self.poolAddress = self.set_checksum(pool["poolAddress"])
        routerAddress = self.set_checksum(self.markets["routerAddress"][int(isV3)])
        nonFungiblePositionManagerAddress = self.set_checksum(self.markets["nonFungiblePositionManagerAddress"][int(isV3)])
        
        self.factoryContract = self.get_contract(factoryAddress, self.markets["factoryAbi"][int(isV3)])
        self.poolContract = self.get_contract(self.poolAddress, self.markets["poolAbi"][int(isV3)])
        self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"][int(isV3)])
        self.nft_managerContract = self.get_contract(nonFungiblePositionManagerAddress, self.markets["nonFungiblePositionManager"][int(isV3)])
        
        tokenAalance = self.partial_balance(tokenAsymbol)
        tokenBalance = self.partial_balance(tokenBsymbol)
        
        self.require(amountA > tokenAalance["balance"], InsufficientBalance(tokenAalance, f"need :{amountA}"))
        self.require(amountB > tokenBalance["balance"], InsufficientBalance(tokenBalance, f"need :{amountB}"))
        
        token_0 = self.poolContract.functions.token0().call()
        token_1 = self.poolContract.functions.token1().call()
        
        fee = self.poolContract.functions.fee().call()
        tick_lower = SafeMath.nearest_tick(tick_lower, fee)
        tick_upper = SafeMath.nearest_tick(tick_upper, fee)
        
        self.require(tick_lower < tick_upper, ValueError("Invalid tick range"))
        self.require(not self.fetch_available_LBPairs(), ValueError("can`t find any available pairs"))
        
        self.check_approve(
            amount=amountA, token=tokenAaddress, account=self.account, router=nonFungiblePositionManagerAddress
        )

        self.check_approve(
            amount=amountB, token=tokenBaddress, account=self.account, router=nonFungiblePositionManagerAddress
        )

        amountAMin = int(round(amountA_value * (1 - amountSlippage / 100)))
        amountBMin = int(round(amountB_value * (1 - amountSlippage / 100)))
        
        deadline = int(datetime.datetime.now().timestamp() + 1800)

        payload = {
            "token0" : token_0,
            "token1" : token_1,
            "fee" : fee,
            "tickLower" : tick_lower,
            "tickUpper" : tick_upper,
            "amount0Desired" : amountA_value,
            "amount1Desired" : amountB_value,
            "amount0Min" : amountAMin,
            "amount1Min" : amountBMin,
            "recipient" : self.account,
            "deadline" : deadline
        }

        self.token_with_token(payload)
        
        tx = self.token_with_token(payload)
        
        tx_receipt = self.fetch_transaction(tx, "ADD", payload=payload)
        
        return tx_receipt
    
    def fetch_available_LBPairs(self):
        
        return self.poolContract.functions.slot0().call()
    
    def token_with_token(self, payload):

        tx = self.nft_managerContract.functions.mint(
            payload
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )
    
        return tx
    
    def add_call_parameters(position, ticks, options):
        # ... previous logic ...

        for index,p in enumerate(positions):
            # ... previous logic ...

            if is_mint(options):
                recipient = validate_and_parse_address(options['recipient'])
                calldatas.append(
                    encode_function_data('mint', [
                        {
                            'token0': p["pool"]["token0"]["address"],
                            'token1': p["pool"]["token1"]["address"],
                            'fee': p["pool"]["fee"],
                            'tickLower': p["tickLower"],
                            'tickUpper': p["tickUpper"],
                            'ticksPrevious': ticks_previous[index],
                            'amount0Desired': Web3.toHex(amount0_desired),
                            'amount1Desired': Web3.toHex(amount1_desired),
                            'amount0Min': amount0_min,
                            'amount1Min': amount1_min,
                            'recipient' : recipient,
                            deadline: deadline
                        }
                    ])
                )
            else:
                calldatas.append(
                    encode_function_data('addLiquidity', [
                        {
                        "tokenId": Web3.toHex(options.tokenId),
                        "ticksPrevious": ticks_previous[index],
                        "amount0Desired": Web3.toHex(amount0_desired),
                        "amount1Desired": Web3.toHex(amount1_desired),
                        "amount0Min" : amount0_min,
                        "amount1Min" : amount1_min,
                        deadline: deadline
                        }
                    ])
                )

            # ... rest of the logic here ...

        return {
        'calldata' : multicall.encode_multicall(calldatas),
        value:Web3.toHex(value)
        }