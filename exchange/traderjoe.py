# from ..base.exchange import Exchange
# from ..base.utils.errors import (
#     InsufficientBalance,
# )

# from ..base.utils.retry import retry
# # from ..base.utils.constants import curve_4batch
# from typing import Optional
# import datetime

# # from pytz import timezone
# import time
# from ..base.utils import SafeMath
# import logging
# from enum import Enum
# import math
# from typing import List


# class LiquidityDistribution(Enum):
#     SPOT = 0
#     CURVE = 1
#     BID_ASK = 2


# class Traderjoe(Exchange):
#     has = {
#         "createSwap": True,
#         "fetchTicker": True,
#         "fetchBalance": True,
#     }

#     def __init__(self, config_change: Optional[dict] = {}):
#         super().__init__()

#         config = {
#             "chainName": "AVAX",
#             "exchangeName": "traderjoe",
#             "retries": 3,
#             "retriesTime": 10,
#             "host": None,
#             "account": None,
#             "privateKey": None,
#             "log": None,
#             "proxy": False,
#             "api_url": "https://barn.traderjoexyz.com/",
#         }

#         config.update(config_change)

#         # market info
#         self.id = 1
#         self.chainName = config["chainName"]
#         self.exchangeName = config["exchangeName"]
#         self.duration = False
#         self.addNounce = 0
#         self.retries = config["retries"]
#         self.retriesTime = config["retriesTime"]
#         self.host = config["host"]
#         self.account = config["account"]
#         self.privateKey = config["privateKey"]
#         self.log = config["log"]
#         self.api_url = config["api_url"]
#         self.proxy = config["proxy"]

#         self.load_exchange(self.chainName, self.exchangeName)
#         self.set_logger(self.log)
#         self.safe_math = SafeMath()

#     @retry
#     async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol):
#         amountIn = self.from_value(value=amountAin, exp=self.decimals(tokenAsymbol))

#         pool = self.get_pool(tokenAsymbol, tokenBsymbol)

#         pool = self.set_checksum(pool)

#         amountBout = self.get_amount_out(pool, tokenAsymbol, amountIn)
#         amountout = self.to_value(value=amountBout, exp=self.decimals(tokenBsymbol))

#         result = {
#             "amountAin": amountAin,
#             "amountBout": amountout,
#             "tokenAsymbol": tokenAsymbol,
#             "tokenBsymbol": tokenBsymbol,
#         }

#         return result

#     @retry
#     async def create_swap(
#         self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs
#     ):
#         """
#         Parameters
#         ----------
#         amountA : tokenA amount input
#         tokenAsymbol: symbol of token input
#         amountBMin : tokenB amount output which is expactation as minimun
#         tokenBsymbol : symbol of tokenB output

#         Return
#         {
#         'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4',
#         'status': 1,
#         'block': 34314499,
#         'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156),
#         'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>,
#         'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
#         'amountIn': 0.1,
#         'tokenA': 'USDC',
#         'to': '0x10f4A785F458Bc144e3706575924889954946639',
#         'amountOut': 0.623371,
#         'tokenB': 'oZEMIT',
#         'transaction_fee:': 0.023495964646856035
#         }
#         """

#         if (path != None) and (len(path) > 2):
#             self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path[1:-1]]

#         else:
#             self.path = []

#         self.tokenSymbol = tokenAsymbol
#         self.tokenBsymbol = tokenBsymbol
#         self.amount = amountA

#         self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
#         self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

#         tokenA = self.tokens[tokenAsymbol]
#         tokenB = self.tokens[tokenBsymbol]
#         amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
#         amountBMin = self.from_value(value=amountBMin, exp=int(tokenB["decimals"]))

#         tokenAaddress = self.set_checksum(tokenA["contract"])
#         tokenBaddress = self.set_checksum(tokenB["contract"])
#         self.account = self.set_checksum(self.account)
#         routerAddress = self.set_checksum(self.markets["routerAddress"])

#         self.check_approve(
#             amount=amountA, token=tokenAaddress, account=self.account, router=routerAddress
#         )

#         self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"])

#         self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

#         if tokenAsymbol == self.baseCurrency:
#             tx = self.eth_to_token(amountA, tokenBaddress, amountBMin)
#         # elif tokenBsymbol == self.baseCurrency:
#         #     tx = self.token_to_eth(tokenAaddress, amountA)
#         else:
#             tx = self.token_to_token(tokenAaddress, amountA, tokenBaddress, amountBMin)

#         tx_receipt = self.fetch_transaction(tx, "SWAP")

#         return tx_receipt

#     def token_to_token(self, tokenAaddress, amountA, tokenBaddress, amountBMin):
#         deadline = int(datetime.datetime.now().timestamp() + 1800)

#         tx = self.routerContract.functions.swapExactTokensForTokens(
#             amountA, amountBMin, self.path, self.account, deadline
#         ).build_transaction(
#             {
#                 "from": self.account,
#                 "nonce": self.nonce,
#             }
#         )

#         return tx

#     def eth_to_token(self, amountA, tokenBaddress, amountBMin):
#         deadline = int(datetime.datetime.now().timestamp() + 1800)

#         tx = self.routerContract.functions.swapExactAVAXForTokens(
#             amountBMin, self.path, self.account, deadline
#         ).build_transaction(
#             {
#                 "from": self.account,
#                 # "gasPrice" : self.w3.toHex(25000000000),
#                 "nonce": self.nonce,
#                 "value": amountA,
#             }
#         )

#         return tx

#     def token_to_eth(self, tokenAaddress, amountA, amountBMin):
#         deadline = int(datetime.datetime.now().timestamp() + 1800)

#         tx = self.routerContract.functions.swapExactTokensForAVAX(
#             amountA, amountBMin, self.path, self.account, deadline
#         ).build_transaction(
#             {
#                 "from": self.account,
#                 # "gasPrice" : self.w3.toHex(25000000000),
#                 "nonce": self.nonce,
#             }
#         )

#         return tx

#     def get_amount_out(self, tokenAsymbol, amountIn, tokenBsymbol):
#         routerAddress = self.set_checksum(self.markets["routerAddress"])

#         tokenA = self.tokens[tokenAsymbol]
#         tokenB = self.tokens[tokenBsymbol]

#         tokenAaddress = self.set_checksum(tokenA["contract"])
#         tokenBaddress = self.set_checksum(tokenB["contract"])

#         self.routerContract = self.get_contract(routerAddress, self.markets["routerAbi"])

#         amountOut = self.routerContract.functions.getAmountsOut(
#             amountIn, [tokenAaddress, tokenBaddress]
#         ).call()[-1]

#         return amountOut

#     def get_reserves(self, tokenAsymbol, tokenBsymbol):
#         pool = self.get_pool(tokenAsymbol, tokenBsymbol)

#         pool = self.set_checksum(pool)

#         tokenA = self.tokens[tokenAsymbol]

#         tokenAaddress = self.set_checksum(tokenA["contract"])

#         factoryContract = self.get_contract(pool, self.markets["factoryAbi"])

#         tokenA = factoryContract.functions.tokenA().call()

#         routerContract = self.get_contract(pool, self.markets["routerAbi"])
#         reserves = routerContract.functions.getCurrentPool().call()

#         if tokenA != tokenAaddress:
#             reservesA = self.to_value(reserves[1], self.decimals(tokenAsymbol))
#             reservesB = self.to_value(reserves[0], self.decimals(tokenBsymbol))

#         else:
#             reservesA = self.to_value(reserves[0], self.decimals(tokenAsymbol))
#             reservesB = self.to_value(reserves[1], self.decimals(tokenBsymbol))

#         reserve = reservesB / reservesA

#         return {
#             "pool": f"{tokenAsymbol}-{tokenBsymbol}",
#             "tokenAsymbol": tokenAsymbol,
#             "tokenBsymbol": tokenBsymbol,
#             "tokenAreserves": reservesA,
#             "tokenBreserves": reservesB,
#             "poolPrice": reserve,
#             "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         }

#     @retry
#     async def add_liquidity(
#         self,
#         tokenAsymbol,
#         tokenBsymbol,
#         amountA,
#         amountB,
#         amountSlippage,
#         priceSlippage,
#         number_bins,
#         *args,
#         **kwargs,
#     ):
#         """
#         Return
#         {
#         'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4',
#         'status': 1,
#         'block': 34314499,
#         'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156),
#         'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>,
#         'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
#         'amountIn': 0.1,
#         'tokenA': 'USDC',
#         'to': '0x10f4A785F458Bc144e3706575924889954946639',
#         'amountOut': 0.623371,
#         'tokenB': 'oZEMIT',
#         'transaction_fee:': 0.023495964646856035
#         }
#         """

#         self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

#         tx_receipts = []

#         self.tokenSymbol = tokenAsymbol
#         self.tokenBsymbol = tokenBsymbol
#         self.amount = amountA
#         self.input = {
#             "tokenAsymbol": tokenAsymbol,
#             "tokenBsymbol": tokenBsymbol,
#             "amountA": amountA,
#             "amountB": amountB,
#             "amountSlippage": amountSlippage,
#             "priceSlippage": priceSlippage,
#             "number_bins": number_bins,
#         }

#         self.pool_name = f"{tokenAsymbol}-{tokenBsymbol}"

#         self.require(
#             f"{self.pool_name}" not in self.pools,
#             ValueError("can`t find any available pairs in mars"),
#         )

#         pool = self.pools[f"{self.pool_name}"]

#         if "isV21" in pool:
#             isV21 = pool["isV21"]

#         else:
#             isV21 = False

#         tokenA = self.tokens[tokenAsymbol]
#         tokenB = self.tokens[tokenBsymbol]
#         amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
#         amountB = self.from_value(value=amountB, exp=int(tokenB["decimals"]))

#         tokenAaddress = self.set_checksum(tokenA["contract"])
#         tokenBaddress = self.set_checksum(tokenB["contract"])
#         self.account = self.set_checksum(self.account)
#         factoryAddress = self.set_checksum(self.markets["factoryAddress"][int(isV21)])
#         self.poolAddress = self.set_checksum(pool["poolAddress"])
#         routerAddress = self.set_checksum(self.markets["routerAddress"][int(isV21)])

#         self.factoryContract = self.get_contract(
#             factoryAddress, self.markets["factoryAbi"][int(isV21)]
#         )
#         self.poolContract = self.get_contract(self.poolAddress, self.markets["poolAbi"][int(isV21)])
#         self.routerContract = self.get_contract(
#             routerAddress, self.markets["routerAbi"][int(isV21)]
#         )

#         self.require(
#             not self.fetch_available_LBPairs(tokenAaddress, tokenBaddress, self.poolAddress),
#             ValueError("can`t find any available pairs"),
#         )

#         self.check_approve(
#             amount=amountA, token=tokenAaddress, account=self.account, router=routerAddress
#         )

#         self.check_approve(
#             amount=amountB, token=tokenBaddress, account=self.account, router=routerAddress
#         )

#         payloads = self.add_liquidity_parameters(
#             number_bins,
#             self.bins,
#             isV21,
#             tokenA,
#             tokenB,
#             tokenAaddress,
#             tokenBaddress,
#             amountA,
#             amountB,
#             amountSlippage,
#             priceSlippage,
#         )

#         for payload in payloads:
#             self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

#             try:
#                 if tokenAsymbol == self.baseCurrency:
#                     tx = self.eth_with_token(payload, amountA)
#                 elif tokenBsymbol == self.baseCurrency:
#                     tx = self.eth_with_token(payload, amountB)
#                 else:
#                     tx = self.token_with_token(payload)

#                 tx_receipt = self.fetch_transaction(tx, "ADD", payload=payload)

#             except:
#                 logging.info(payload)

#                 raise

#             tx_receipts.append(tx_receipt)

#         return tx_receipts

#     @retry
#     async def remove_liquidity(self, tokenAsymbol, tokenBsymbol, amountSlippage, *args, **kwargs):
#         """
#         Return
#         {
#         'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4',
#         'status': 1,
#         'block': 34314499,
#         'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156),
#         'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>,
#         'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF',
#         'amountIn': 0.1,
#         'tokenA': 'USDC',
#         'to': '0x10f4A785F458Bc144e3706575924889954946639',
#         'amountOut': 0.623371,
#         'tokenB': 'oZEMIT',
#         'transaction_fee:': 0.023495964646856035
#         }
#         """

#         tx_receipts = []

#         self.tokenSymbol = tokenAsymbol
#         self.tokenBsymbol = tokenBsymbol
#         # self.amount = amountA
#         self.input = {
#             "tokenAsymbol": tokenAsymbol,
#             "tokenBsymbol": tokenBsymbol,
#             "amountSlippage": amountSlippage,
#         }

#         self.require(
#             f"{tokenAsymbol}-{tokenBsymbol}" not in self.pools,
#             ValueError("can`t find any available pairs in mars"),
#         )

#         pool = self.pools[f"{tokenAsymbol}-{tokenBsymbol}"]

#         if "isV21" in pool:
#             isV21 = pool["isV21"]

#         else:
#             isV21 = False

#         tokenA = self.tokens[tokenAsymbol]
#         tokenB = self.tokens[tokenBsymbol]

#         binId_result = self.create_request(
#             self.api_url,
#             {},
#             "v1",
#             "user",
#             "bin-ids",
#             self.account,
#             "avalanche",
#             pool["poolAddress"],
#         )

#         tokenAaddress = self.set_checksum(tokenA["contract"])
#         tokenBaddress = self.set_checksum(tokenB["contract"])
#         self.account = self.set_checksum(self.account)
#         factoryAddress = self.set_checksum(self.markets["factoryAddress"][int(isV21)])
#         poolAddress = self.set_checksum(pool["poolAddress"])
#         routerAddress = self.set_checksum(self.markets["routerAddress"][int(isV21)])

#         self.factoryContract = self.get_contract(
#             factoryAddress, self.markets["factoryAbi"][int(isV21)]
#         )
#         self.poolContract = self.get_contract(poolAddress, self.markets["poolAbi"][int(isV21)])
#         self.routerContract = self.get_contract(
#             routerAddress, self.markets["routerAbi"][int(isV21)]
#         )

#         self.require(
#             not self.fetch_available_LBPairs(tokenAaddress, tokenBaddress, poolAddress),
#             ValueError("can`t find any available pairs"),
#         )

#         self.check_approve_all(router=self.markets["routerAddress"][int(isV21)])

#         payloads = self.remove_liquidity_parameters(
#             self.bins,
#             binId_result,
#             tokenAaddress,
#             tokenBaddress,
#             amountSlippage,
#         )

#         for payload in payloads:
#             self.nonce = self.w3.eth.get_transaction_count(self.account) + self.addNounce

#             try:
#                 # if tokenAsymbol == self.baseCurrency:
#                 #     tx = self.eth_with_token(payload, amountA)
#                 # elif tokenBsymbol == self.baseCurrency:
#                 #     tx = self.eth_with_token(payload, amountB)
#                 # else:
#                 tx = self.token_with_token(payload)

#                 tx_receipt = self.fetch_transaction(tx, "REMOVE", payload=payload)

#             except:
#                 logging.info(payload)

#                 raise

#             tx_receipts.append(tx_receipt)

#         return tx_receipts

#     def add_liquidity_parameters(
#         self,
#         number_bins,
#         binStep,
#         isV21,
#         tokenA,
#         tokenB,
#         tokenAaddress,
#         tokenBaddress,
#         tokenAamount,
#         tokenBamount,
#         amountSlippage,
#         priceSlippage,
#     ):
#         """
#         Return
#         ----------
#         tokenX: Token
#         tokenY: Token
#         amountX: string
#         amountY: string
#         amountXMin: string
#         amountYMin: string
#         idSlippage: number
#         deltaIds: number[]
#         distributionX: bigint[]
#         distributionY: bigint[]

#         """

#         payloads = []

#         reserveX, reserveY, activeId = self.get_LBPair_ReservesAndId(isV21)
#         idSlippage = self.get_IdSlippage_From_PriceSlippage(number_bins, binStep, priceSlippage)
#         bin_range_list = self.create_intervals(activeId, -number_bins // 2, number_bins // 2, 100)

#         deadline = int(datetime.datetime.now().timestamp() + 1800)

#         if idSlippage == 3:
#             tokenAamounts = list(
#                 map(lambda x: int(round(x * tokenAamount)), curve_4batch["batchX"])
#             )
#             tokenBamounts = list(
#                 map(lambda x: int(round(x * tokenBamount)), curve_4batch["batchY"])
#             )

#             amountAMins = list(
#                 map(lambda x: int(round(x * (1 - amountSlippage / 100))), tokenAamounts)
#             )
#             amountBMins = list(
#                 map(lambda x: int(round(x * (1 - amountSlippage / 100))), tokenBamounts)
#             )

#         for i, bin_range in enumerate(bin_range_list):
#             deltaIds, distributionX, distributionY = self.get_curve_distribution_from_bin_range(
#                 activeId, bin_range, [tokenAamounts[i], tokenBamounts[i]]
#             )
#             distributionX, distributionY = (
#                 curve_4batch["distributionX"][i],
#                 curve_4batch["distributionY"][i],
#             )
#             payload = {
#                 "tokenX": tokenAaddress,
#                 "tokenY": tokenBaddress,
#                 "binStep": binStep,
#                 "amountX": tokenAamounts[i],
#                 "amountY": tokenBamounts[i],
#                 "amountXMin": amountAMins[i],
#                 "amountYMin": amountBMins[i],
#                 "activeIdDesired": activeId,
#                 "idSlippage": idSlippage,
#                 "deltaIds": deltaIds,
#                 "distributionX": distributionX,
#                 "distributionY": distributionY,
#                 "to": self.account,
#                 "refundTo": self.account,
#                 "deadline": deadline,
#             }

#             payloads.append(payload)

#         return payloads

#     def remove_liquidity_parameters(
#         self,
#         binStep,
#         binId_result,
#         tokenAaddress,
#         tokenBaddress,
#         amountSlippage,
#     ):
#         """
#         Return
#         ----------
#         tokenX: Token
#         tokenY: Token
#         amountX: string
#         amountY: string
#         amountXMin: string
#         amountYMin: string
#         idSlippage: number
#         deltaIds: number[]
#         distributionX: bigint[]
#         distributionY: bigint[]

#         """

#         payloads = []

#         deadline = int(datetime.datetime.now().timestamp() + 1800)

#         ids_list = self.create_ids(0, binId_result[0], binId_result[1], 200)
#         amounts_list = [0] * len(ids_list)
#         amountXMin_list = [0] * len(ids_list)
#         amountYMin_list = [0] * len(ids_list)
#         totalXBalanceWithdrawn = 0
#         totalYBalanceWithdrawn = 0

#         for i, ids in enumerate(ids_list):
#             amounts = [0] * len(ids)

#             for j, id in enumerate(ids):
#                 LBTokenAmount = self.poolContract.functions.balanceOf(self.account, id).call()
#                 amounts[j] = LBTokenAmount

#                 binReserveX, binReserveY = self.poolContract.functions.getBin(id).call()

#                 totalXBalanceWithdrawn += (
#                     LBTokenAmount * binReserveX / self.poolContract.functions.totalSupply(id)
#                 )
#                 totalYBalanceWithdrawn += (
#                     LBTokenAmount * binReserveY / self.poolContract.functions.totalSupply(id)
#                 )

#             amountXMin = totalXBalanceWithdrawn * (1 - amountSlippage)  # Allow 1% slippage
#             amountYMin = totalYBalanceWithdrawn * (1 - amountSlippage)  # Allow 1% slippage

#             amounts_list[i] = amounts
#             amountXMin_list[i] = amountXMin
#             amountYMin_list[i] = amountYMin

#         for i in range(len(ids_list)):
#             payload = {
#                 "tokenX": tokenAaddress,
#                 "tokenY": tokenBaddress,
#                 "binStep": binStep,
#                 "amountXMin": amountXMin_list[i],
#                 "amountYMin": amountYMin_list[i],
#                 "ids": ids_list[i],
#                 "amounts": amounts_list[i],
#                 "to": self.account,
#                 "deadline": deadline,
#             }

#             payloads.append(payload)

#         return payloads

#     def get_uniform_distribution_from_bin_range(
#         self, tokenA, tokenB, active_id, bin_range, parsed_amounts
#     ):
#         parsed_amount_a, parsed_amount_b = parsed_amounts

#         # Init return values
#         delta_ids = []
#         _distribution_x = []
#         _distribution_y = []

#         # def get_sigma(_R):
#         #     factor = 2.0 if _R >= 20 else 1.8 if _R >= 15 else 1.7 if _R >= 10 else 1.6 if _R >= 8 else 1.5 if _R >= 6 else 1.4 if _R >= 5 else 1.0
#         #     return _R / factor

#         # Range only includes B tokens (Y tokens)
#         if bin_range[1] <= active_id and parsed_amount_a == 0:
#             neg_delta = bin_range[1] - bin_range[0] + 1

#             negative_delta_ids = [
#                 -1 * (el + 1) for el in range(active_id - bin_range[0] - 1, -1, -1)
#             ][:neg_delta]

#             delta_ids = negative_delta_ids
#             if active_id == bin_range[1]:
#                 delta_ids.append(0)

#             _distribution_x = [0 for _ in range(len(delta_ids))]
#             _distribution_y = [self.get_reserve_y(bin) for bin in range(bin_range[0], bin_range[1])]

#         # Range only includes A tokens (X tokens)
#         elif active_id <= bin_range[0] and parsed_amount_b == 0:
#             pos_delta = bin_range[1] - bin_range[0] + 1
#             positive_delta_ids = [(el + 1) for el in range(bin_range[1] - active_id)][::-1][
#                 :pos_delta
#             ][::-1]

#             delta_ids = positive_delta_ids
#             if active_id == bin_range[0]:
#                 delta_ids.insert(0, 0)

#             _distribution_x = [1 / pos_delta for _ in range(pos_delta)]
#             _distribution_y = [0 for _ in range(len(delta_ids))]

#         # Range includes both X and Y tokens
#         else:
#             neg_delta = active_id - bin_range[0]
#             pos_delta = bin_range[1] - active_id

#             negative_delta_ids = [-1 * (el + 1) for el in range(neg_delta - 1, -1, -1)]
#             positive_delta_ids = [el + 1 for el in range(pos_delta)]
#             delta_ids = negative_delta_ids + [0] + positive_delta_ids

#             pos_pct_per_bin = 1 / (0.5 + pos_delta)
#             neg_pct_per_bin = 1 / (0.5 + neg_delta)
#             _distribution_x = (
#                 [0] * neg_delta + [pos_pct_per_bin / 2] + [pos_pct_per_bin] * pos_delta
#             )
#             _distribution_y = (
#                 [neg_pct_per_bin] * neg_delta + [neg_pct_per_bin / 2] + [0] * pos_delta
#             )

#         return (
#             delta_ids,
#             [self.from_value(value=el, exp=int(tokenA["decimals"])) for el in _distribution_x],
#             [self.from_value(value=el, exp=int(tokenB["decimals"])) for el in _distribution_y],
#         )

#     def get_curve_distribution_from_bin_range(self, active_id, bin_range, parsed_amounts):
#         parsed_amount_a, parsed_amount_b = parsed_amounts

#         # Initialization
#         delta_ids = []
#         _distribution_x = []
#         _distribution_y = []

#         def get_sigma(_R):
#             factor = (
#                 2.0
#                 if _R >= 20
#                 else 1.8
#                 if _R >= 15
#                 else 1.7
#                 if _R >= 10
#                 else 1.6
#                 if _R >= 8
#                 else 1.5
#                 if _R >= 6
#                 else 1.4
#                 if _R >= 5
#                 else 1.0
#             )
#             return _R / factor

#         # Range only includes B tokens (Y tokens)
#         if bin_range[1] <= active_id and parsed_amount_a == 0:
#             neg_delta = bin_range[1] - bin_range[0] + 1
#             negative_delta_ids = [
#                 -1 * (el + 1) for el in range(active_id - bin_range[0] - 1, -1, -1)
#             ][:neg_delta]

#             delta_ids = negative_delta_ids
#             if active_id == bin_range[1]:
#                 delta_ids.append(0)

#             _distribution_x = [0 for _ in range(len(delta_ids))]

#             # Radius is num of bins
#             R = len(delta_ids) - 1
#             sigma = get_sigma(R)

#             # A = 1 / (sigma * sqrt(2 * pi))
#             A = 1 / (math.sqrt(math.pi * 2) * sigma)

#             # Dist = 2 * A * exp(-0.5 * (r / sigma) ^ 2)
#             # R is distance from right-most bin
#             _distribution_y = [
#                 2 * A * math.exp(-0.5 * ((R - ind) / sigma) ** 2) for ind, _ in enumerate(delta_ids)
#             ]

#         # Range only includes A tokens (X tokens)
#         elif active_id <= bin_range[0] and parsed_amount_b == 0:
#             pos_delta = bin_range[1] - bin_range[0] + 1
#             positive_delta_ids = [(el + 1) for el in range(bin_range[1] - active_id)][::-1][
#                 :pos_delta
#             ][::-1]

#             delta_ids = positive_delta_ids
#             if active_id == bin_range[0]:
#                 delta_ids.insert(0, 0)

#             _distribution_y = [0 for _ in range(len(delta_ids))]

#             # Radius is num of bins
#             R = len(delta_ids) - 1
#             sigma = get_sigma(R)

#             # A = 1 / (sigma * sqrt(2 * pi))
#             A = 1 / (math.sqrt(math.pi * 2) * sigma)

#             # Dist = 2 * A * exp(-0.5 * (r / sigma) ^ 2)
#             # R is distance from left-most bin
#             _distribution_x = [
#                 2 * A * math.exp(-0.5 * (ind / sigma) ** 2) for ind, _ in enumerate(delta_ids)
#             ]

#         # Range includes both X and Y tokens
#         else:
#             neg_delta = active_id - bin_range[0]
#             pos_delta = bin_range[1] - active_id

#             negative_delta_ids = [-1 * el for el in range(neg_delta, 0, -1)]
#             positive_delta_ids = [el + 1 for el in range(pos_delta)]

#             delta_ids = negative_delta_ids + [0] + positive_delta_ids

#             # Radius is num of bins
#             RX = len(positive_delta_ids)
#             sigmaX = get_sigma(RX)

#             # A = 1 / (sigma * sqrt(2 * pi))
#             AX = 1 / (math.sqrt(math.pi * 2) * sigmaX)

#             # Dist = 2 * A * exp(-0.5 * (r / sigma) ^ 2)
#             # R is distance from 0
#             _distribution_x = (
#                 [0 for _ in range(neg_delta)]
#                 + [AX]
#                 + [
#                     2 * AX * math.exp(-0.5 * ((ind + 1) / sigmaX) ** 2)
#                     for ind, _ in enumerate(positive_delta_ids)
#                 ]
#             )

#             # Radius is num of bins
#             RY = len(negative_delta_ids)
#             sigmaY = get_sigma(RY)

#             # A = 1 / (sigma * sqrt(2 * pi))
#             AY = 1 / (math.sqrt(math.pi * 2) * sigmaY)

#             # Dist = 2 * A * exp(-0.5 * (r / sigma) ^ 2)
#             # R is distance from 0
#             _distribution_y = (
#                 [
#                     2 * AY * math.exp(-0.5 * ((RY - ind) / sigmaY) ** 2)
#                     for ind, _ in enumerate(negative_delta_ids)
#                 ]
#                 + [AY]
#                 + [0 for _ in range(pos_delta)]
#             )

#         return (
#             delta_ids,
#             [self.from_value(value=el, exp=18) for el in _distribution_x],
#             [self.from_value(value=el, exp=18) for el in _distribution_y],
#         )

#     def get_binstep(self):
#         binstep = self.factoryContract.functions.getAllBinSteps().call()

#         return binstep

#     def getPriceFromId(self, binId: int, binStep: int) -> float:
#         """
#         Convert a binId to the underlying price.

#         :param binId: Bin Id.
#         :param binStep: BinStep of the pair.
#         :return: Price of the bin.
#         """

#         return (1 + binStep / 10_000) ** (binId - 8388608)

#     # multicall is recommended to use here, as this might make up to 400 calls for bin step = 1
#     def get_all_reserves(self, ids):
#         bin_reserves_x = []
#         bin_reserves_y = []
#         for id in ids:
#             reserve_x, reserve_y = self.poolContract.functions.getBin(id).call()
#             bin_reserves_x.append(reserve_x)
#             bin_reserves_y.append(reserve_y)
#         return bin_reserves_x, bin_reserves_y

#     # def get_ids(self,) -> list[int]:
#     def get_ids(
#         self,
#     ):
#         bin_step = self.poolContract.functions.getBinStep().call()
#         active_bin = self.poolContract.functions.getActiveId().call()
#         percent_depth = 5000  # 200 = 2%
#         """
#         Example: for bin_step = 10 to lower a price by 2%, active bin needs to be moved by 20 bins:
#         1) clearing active bin liqudity
#         2) trading away 19 bins below
#         3) trade at least 1 token from next bin - this will be ignored
#         So in this case, there will be 39 bins taken into consideration
#         For case bin step = 15 bins amount gets rounded up
#         """
#         bins_to_move_price = math.ceil(percent_depth / bin_step)

#         start_bin = active_bin - bins_to_move_price + 1
#         end_bin = active_bin + bins_to_move_price

#         ids = [bin_id for bin_id in range(start_bin, end_bin)]
#         return ids

#     def create_intervals(self, activeId, start, end, step):
#         intervals = []
#         curr = start
#         first = True

#         while curr <= end:
#             next_value = min(curr + step - 1, end)
#             if first:
#                 next_value += 1
#                 first = False

#             intervals.append([activeId + curr, activeId + next_value])
#             curr = next_value + 1

#         return intervals

#     def create_ids(self, activeId, start, end, step):
#         ids_list = []
#         intervals = self.create_intervals(activeId, start, end, step)

#         for interval in intervals:
#             ids = list(range(interval[0], interval[1]))
#             ids.append(interval[1])

#             ids_list.append(ids)

#         return ids_list

#     def fetch_available_LBPairs(self, tokenAaddress, tokenBaddress, poolAddress):
#         self.bins = 0

#         pairs = self.factoryContract.functions.getAllLBPairs(tokenAaddress, tokenBaddress).call()

#         for pair in pairs:
#             if pair[1] == poolAddress:
#                 result = True

#                 self.bins = pair[0]

#         if self.bins == 0:
#             result = False

#         return result

#     def get_LBPair_ReservesAndId(self, isV21):
#         if isV21:
#             reserveX, reserveY = self.poolContract.functions.getReserves().call()

#             activeId = self.poolContract.functions.getActiveId().call()

#         else:
#             reserveX, reserveY, activeId = self.poolContract.functions.getReservesAndId().call()

#         return reserveX, reserveY, activeId

#     def get_IdSlippage_From_PriceSlippage(self, number_bins, binStep, priceSlippage):
#         # return SafeMath.div(1 + priceSlippage / 100, SafeMath.div(1 + binStep, 10000))

#         batch_number = number_bins // 100

#         result = math.floor(math.log(1 + priceSlippage / 100) / math.log(1 + binStep / 10000))

#         return result * batch_number

#     def token_with_token(self, payload):
#         tx = self.routerContract.functions.addLiquidity(payload).build_transaction(
#             {
#                 "from": self.account,
#                 "nonce": self.nonce,
#             }
#         )

#         return tx

#     def eth_with_token(self, payload, amount):
#         tx = self.routerContract.functions.addLiquidityNATIVE(payload).build_transaction(
#             {
#                 "from": self.account,
#                 # "gasPrice" : self.w3.toHex(25000000000),
#                 "nonce": self.nonce,
#                 "value": amount,
#             }
#         )

#         return tx

#     def check_approve_all(self, router: str, *args, **kwargs):
#         # if token == self.chains["baseContract"]:
#         #     return

#         approvedTokens = self.poolContract.functions.isApprovedForAll(self.account, router).call()

#         if not approvedTokens:
#             tx = self.routerContract.functions.approveForAll(router, True).build_transaction(
#                 {
#                     "from": self.account,
#                     "nonce": self.nonce,
#                     "value": 0,
#                 }
#             )

#             tx_receipt = self.fetch_transaction(tx, round="CHECK")
#             return tx_receipt

#         else:
#             return

#     def check_pool_price(self, tokenAsymbol, tokenBsymbol):
#         pool = self.pools[f"{tokenAsymbol}-{tokenBsymbol}"]

#         poolAddress = self.set_checksum(pool["poolAddress"])

#         result = self.create_request(self.api_url, {}, "v1", "pools", "avalanche", poolAddress)

#         token_X_price = result["tokenX"]["priceUsd"]
#         token_Y_price = result["tokenY"]["priceUsd"]

#         return token_X_price, token_Y_price

#     def get_debank_balance(self):
#         balances = []

#         debank_link = "https://api.debank.com/"

#         params = {"user_addr": self.account}

#         wallet_balance_list = self.create_request(debank_link, params, "portfolio", "project_list")[
#             "data"
#         ]

#         for token in wallet_balance_list:
#             if "dao_id" in token:
#                 if token["dao_id"] == "traderjoexyz":
#                     token_dict = token["portfolio_item_list"][0]["asset_dict"]

#                     break

#         for i, token in enumerate(token_dict):
#             balances.append(token_dict[token])

#         return balances

#     def get_coinstatus_balance(self):
#         balances = []

#         coinstatus_link = "https://api.coin-stats.com/"

#         uuid = "dfaee252-f424-4b06-a22f-bcfd9757a57a"

#         uuid_header = ["Uuid", uuid]

#         assets = self.create_request(
#             coinstatus_link,
#             {},
#             "v2",
#             "portfolios",
#             "defi",
#             "tracking?portfolioId=",
#             header=uuid_header,
#         )["protocols"][0]["investments"][0]["assets"]

#         for asset in assets:
#             balances.append(asset["amount"])

#         return balances

#     def pool_balance(self, pool_token_list):
#         balances = {}

#         try:
#             wallet_balance_list = self.get_coinstatus_balance()

#         except:
#             try:
#                 wallet_balance_list = self.get_debank_balance()

#             except:
#                 raise ValueError("wallet balance api got limit")

#         for i in range(len(wallet_balance_list)):
#             balances[pool_token_list[i]] = wallet_balance_list[i]

#         return balances

#     def get_liquidity_positions(self) -> List[int]:
#         """
#         Enumerates liquidity position tokens owned by address.
#         Returns array of token IDs.
#         """
#         positions: List[int] = []

#         number_of_positions = self.nonFungiblePositionManager.functions.balanceOf(
#             _addr_to_str(self.address)
#         ).call()
#         if number_of_positions > 0:
#             for idx in range(number_of_positions):
#                 position = self.nonFungiblePositionManager.functions.tokenOfOwnerByIndex(
#                     _addr_to_str(self.address), idx
#                 ).call()
#                 positions.append(position)
#         return positions

#     def check_position(self, tokenAsymbol, tokenBsymbol):
#         isV21 = True

#         pool = self.pools[f"{tokenAsymbol}-{tokenBsymbol}"]

#         # poolAddress = "0xb4315e873dBcf96Ffd0acd8EA43f689D8c20fB30"

#         poolAddress = self.set_checksum(pool["poolAddress"])

#         # token = self.tokens[tokenAsymbol]

#         # poolAddress = self.set_checksum(token["contract"])

#         poolAddress = self.set_checksum(poolAddress)

#         # poolContract = self.get_contract(poolAddress, self.chains["chainAbi"])

#         self.poolContract = self.get_contract(poolAddress, self.markets["poolAbi"][int(isV21)])

#         binId_result = self.create_request(
#             self.api_url,
#             {},
#             "v1",
#             "user",
#             "bin-ids",
#             self.account,
#             "avalanche",
#             pool["poolAddress"],
#         )

#         if len(binId_result) > 0:
#             result = True

#         else:
#             result = False

#         return result

#     def get_last_tx(self):
#         params = {
#             "module": "account",
#             "action": "txlist",
#             "address": self.account,
#             "startblock": 0,
#             "endblock": 99999999,
#             "page": 1,
#             "offset": 1,
#             "sort": "desc",
#             "apikey": "MMMUNDRQ3IWRI1D2XESVTYFU7MV281EZRB",
#         }

#         last_tx = self.create_request(
#             "https://api.snowtrace.io/", params, "api"
#         )  # ['result']['timeStamp']

#         return last_tx

#     # def getPriceEnter(self, binId: int, binStep: int) -> float:
#     def getPriceEnter(self, tokenAsymbol, tokenBsymbol) -> float:
#         """
#         Convert a binId to the underlying price.

#         :param binId: Bin Id.
#         :param binStep: BinStep of the pair.
#         :return: Price of the bin.
#         """

#         isV21 = True

#         pool = self.pools[f"{tokenAsymbol}-{tokenBsymbol}"]

#         # poolAddress = "0xb4315e873dBcf96Ffd0acd8EA43f689D8c20fB30"

#         poolAddress = self.set_checksum(pool["poolAddress"])

#         # token = self.tokens[tokenAsymbol]

#         # poolAddress = self.set_checksum(token["contract"])

#         poolAddress = self.set_checksum(poolAddress)

#         # poolContract = self.get_contract(poolAddress, self.chains["chainAbi"])

#         self.poolContract = self.get_contract(poolAddress, self.markets["poolAbi"][int(isV21)])

#         binId_result = self.create_request(
#             self.api_url,
#             {},
#             "v1",
#             "user",
#             "bin-ids",
#             self.account,
#             "avalanche",
#             pool["poolAddress"],
#         )

#         binId = binId_result[len(binId_result) // 2]
#         binStep = 10

#         # value = (1 + binStep / 10_000) ** (binId - 8388608)

#         value = self.poolContract.functions.getPriceFromId(binId).call()

#         return value

#         true_value = self.from_value(value=value, exp=self.decimals(tokenAsymbol))

#         return true_value
