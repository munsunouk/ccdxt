from typing import Optional
from TonTools import *
from tonsdk.boc import begin_cell
from tonsdk.utils import *
from tonsdk.contract.token.ft import JettonMinter, JettonWallet
from ..base.exchange import Exchange
from ..base.utils.retry import retry
from ..base.utils.asset import Asset
from base64 import b64decode


class Mega(Exchange):
    has = {
        "createSwap": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "chainName": "TON",
            "exchangeName": "mega",
            "retries": 3,
            "retriesTime": 10,
            "mnemonics": None,
            "log": None,
            "proxy": False,
            "toncenter_api_key": None,
            "tonapi_api_key": None,
            "tonapi_url": "https://tonapi.io/",
            "api_url": "https://megaton.fi/",
            "sleep": 10,
            "swap_address": None,
        }

        config.update(config_change)

        # market info
        self.id = 1
        self.addNounce = 0
        self.chainName = config["chainName"]
        self.exchangeName = config["exchangeName"]
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.mnemonics = config["mnemonics"]
        self.log = config["log"]
        self.proxy = config["proxy"]
        self.toncenter_api_key = config["toncenter_api_key"]
        self.tonapi_api_key = config["tonapi_api_key"]
        self.tonapi_url = config["tonapi_url"]
        self.api_url = config["api_url"]
        self.sleep = config["sleep"]
        self.gasPrice = None
        self.swap_address = config["swap_address"]

        self.set_ton_client()
        self.set_ton_wallet(self.mnemonics)

    async def fetch_balance(self, tokens: list):

        total_balances = []

        jetton_dict = await self.fetch_jetton_balances()

        for tokenSymbol in tokens:

            token = self.tokens[tokenSymbol]

            if self.chains["baseCurrency"] == tokenSymbol:

                balance = await self.tool_wallet.get_balance()
                balance = self.to_value(balance, int(token["decimals"]))

            elif token["origin_symbol"] in jetton_dict:

                balance = int(jetton_dict[token["origin_symbol"]])
                balance = self.to_value(balance, int(token["decimals"]))

            else:

                balance = 0

            balance_info = {
                "symbol": token["symbol"],
                "balance": balance,
            }

            total_balances.append(balance_info)

        return total_balances

    # @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol):

        fee, reserveA, reserveB = await self.get_reserves(tokenAsymbol, tokenBsymbol)

        self.require(amountAin <= 0, ValueError("put proper amount"))
        self.require((reserveA == 0) or (reserveB == 0), ValueError("check pool reserve"))

        amount_in = amountAin - (amountAin * (fee * 0.0001))
        numerator = amount_in * reserveB

        denominator = reserveA + amount_in

        amount_out = numerator / denominator

        result = {
            "amountAin": amountAin,
            "amountBout": amount_out,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
        }

        return result

    # @retry
    async def create_swap(
        self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs
    ):

        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        await self.load_exchange(self.chainName, self.exchangeName)

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        amountBMin = 1
        query_id = 0
        forward_amount = to_nano(0.35, "ton")

        router_address = self.markets["routerAddress"]
        tokenA_address = tokenA["contract"]
        tokenB_address = tokenB["contract"]

        current_seqno = await self.tool_wallet.get_seqno()
        self.seqno = current_seqno + self.addNounce

        body = self._create_swap_body(
            Address(router_address),
            Address(self.ton_address),
            amountA,
            Address(tokenA_address),
            amountBMin,
            Address(tokenB_address),
            query_id,
            forward_amount,
        )

        result = await self.create_transfer_message(body, Address(self.swap_address), 0.4)

        return result

    async def create_mint(
        self,
        jetton_amount: float,
    ):

        await self.load_exchange(self.chainName, self.exchangeName)

        token = self.tokens["wTON"]

        token_address = token["contract"]

        current_seqno = await self.tool_wallet.get_seqno()
        self.seqno = current_seqno + self.addNounce

        body = self._create_mint_body(
            destination=Address(self.tool_wallet.address),
            response_address=Address(self.tool_wallet.address),
            jetton_amount=to_nano(jetton_amount, "ton"),
        )

        result = await self.create_transfer_message(
            body, Address(token_address), jetton_amount + 0.1
        )

        return result

    async def create_burn(
        self,
        jetton_amount: float,
    ):

        await self.load_exchange(self.chainName, self.exchangeName)

        token = self.tokens["wTON"]

        token_address = token["contract"]

        current_seqno = await self.tool_wallet.get_seqno()
        self.seqno = current_seqno + self.addNounce

        body = self._create_burn_body(
            destination=Address(self.tool_wallet.address),
            response_address=Address(token_address),
            jetton_amount=to_nano(jetton_amount, "ton"),
        )

        result = await self.create_transfer_message(body, Address(token_address), 0.1)

        return result

    # @retry
    async def fetch_pool(self, pool_address):

        r = await self.client.run_get_method(
            "get_lp_swap_data", address=Address(pool_address).to_string(1, 1, 1), stack=[]
        )

        stack = []
        for s in r:
            if s[0] == "num":
                stack.append({"type": "int", "value": int(s[1], 16)})
            elif s[0] == "null":
                stack.append({"type": "null"})
            elif s[0] == "cell":

                stack.append(
                    {
                        "type": "cell",
                        "value": Cell.one_from_boc(b64decode(s[1]["bytes"])).begin_parse(),
                    }
                )
            elif s[0] == "slice":
                stack.append(
                    {
                        "type": "slice",
                        "value": Cell.one_from_boc(b64decode(s[1]["bytes"])).begin_parse(),
                    }
                )
            elif s[0] == "builder":
                stack.append(
                    {"type": "builder", "value": Cell.one_from_boc(b64decode(s[1]["bytes"]))}
                )

        fee = stack[0]["value"]

        reserveA, reserveB = stack[5]["value"], stack[9]["value"]

        return fee, reserveA, reserveB

    # @retry
    async def fetch_jetton_balances(self):

        params = dict()
        jetton_dict = dict()

        request_jetton_balances = (
            await self.create_request(
                self.tonapi_url,
                params,
                "v2",
                "accounts",
                "0%3A" + self.raw_address,
                "jettons",
                header=["Authorization", f"Bearer {self.tonapi_api_key}"],
            )
        )["balances"]

        for request_jetton_balance in request_jetton_balances:

            jetton_dict[request_jetton_balance["symbol"]] = request_jetton_balance["balance"]

        return jetton_dict

    async def get_reserves(self, tokenAsymbol, tokenBsymbol):

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        if f"{tokenAsymbol}-{tokenBsymbol}" in self.pools:

            pool = self.pools[f"{tokenAsymbol}-{tokenBsymbol}"]

        elif f"{tokenBsymbol}-{tokenAsymbol}" in self.pools:

            pool = self.pools[f"{tokenBsymbol}-{tokenAsymbol}"]

        else:

            ValueError(f"there is no pool available({tokenAsymbol}-{tokenBsymbol})")

        pool_address = pool["baseChain"][self.chainName][self.exchangeName]

        fee, pool_reserveA, pool_reserveB = await self.fetch_pool(pool_address)

        if (tokenAsymbol == pool["tokenA"]) and (tokenBsymbol == pool["tokenB"]):

            reserveA = self.to_value(pool_reserveA, int(tokenA["decimals"]))
            reserveB = self.to_value(pool_reserveB, int(tokenB["decimals"]))

        elif (tokenAsymbol == pool["tokenB"]) and (tokenBsymbol == pool["tokenA"]):

            reserveA = self.to_value(pool_reserveB, tokenA["decimals"])
            reserveB = self.to_value(pool_reserveA, tokenB["decimals"])

        return fee, reserveA, reserveB

    def _create_mint_body(
        self,
        destination: Address,
        response_address: Address,
        jetton_amount: int,
        query_id: int = 0,
    ) -> Cell:

        body = Cell()
        body.bits.write_uint(0x77A33521, 32)  # OP mint
        body.bits.write_uint(query_id, 64)
        body.bits.write_grams(jetton_amount)

        transfer_body = Cell()  # internal transfer
        transfer_body.bits.write_uint(0x178D4519, 32)  # OP transfer
        transfer_body.bits.write_uint(query_id, 64)
        transfer_body.bits.write_grams(jetton_amount)  # jetton amount
        transfer_body.bits.write_address(destination)  # from_address
        transfer_body.bits.write_address(response_address)  # response_address
        transfer_body.bits.write_grams(0)  # forward amount

        body.refs.append(transfer_body)
        return body

    def _create_burn_body(
        self,
        destination: Address,
        response_address: Address,  # response_address (wTON address)
        jetton_amount: int,
        query_id: int = 0,
    ) -> Cell:

        body = Cell()
        body.bits.write_uint(1204914527, 32)  # OP call Jetton Burn
        body.bits.write_uint(query_id, 64)
        body.bits.write_grams(jetton_amount)

        transfer_body = Cell()  # internal transfer
        transfer_body.bits.write_uint(0x178D4519, 32)  # OP transfer
        transfer_body.bits.write_uint(query_id, 64)
        transfer_body.bits.write_grams(jetton_amount)  # jetton amount
        transfer_body.bits.write_address(destination)  # from_address
        transfer_body.bits.write_address(response_address)
        transfer_body.bits.write_grams(0)  # forward amount

        body.refs.append(transfer_body)
        return body

    def _create_swap_body(
        self,
        destination: Address,  # router
        response_address: Address,  # My account
        jetton_amount: int,
        fromJettonAddress: Address,
        minAmount: int,
        toJettonAddress: Address,
        query_id: int,
        forward_amount: int = 0,
    ) -> Cell:

        return (
            begin_cell()
            .store_uint(0xF8A7EA5, 32)
            .store_uint(query_id, 64)
            .store_grams(jetton_amount)
            .store_address(destination)
            .store_address(response_address)
            .store_grams("2600")
            .store_grams(forward_amount)
            .store_ref(
                begin_cell()
                .store_address(fromJettonAddress)
                .store_address(toJettonAddress)
                .store_coins(minAmount)
                .end_cell()
            )
            .end_cell()
        )
