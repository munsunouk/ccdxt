from ..base.exchange import Exchange
from ..base.utils.errors import (
    InsufficientBalance,
)

from ..base.utils.retry import retry
from typing import Optional
import datetime

# from pytz import timezone
import time


class Klayswap(Exchange):
    has = {
        "createSwap": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "chainName": "KLAYTN",
            "exchangeName": "klayswap",
            "retries": 3,
            "retriesTime": 10,
            "host": 0,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
        }

        config.update(config_change)

        # market info
        self.id = 1
        self.chainName = config["chainName"]
        self.exchangeName = config["exchangeName"]
        self.duration = False
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.proxy = config["proxy"]

        # self.load_exchange(self.chainName, self.exchangeName)
        # self.set_logger(self.log)

    # @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol):

        result = {
            "amountAin": amountAin,
            "amountBout": 0,
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
        }

        await self.load_exchange(self.chainName, self.exchangeName)

        amountIn = self.from_value(value=amountAin, exp=await self.decimals(tokenAsymbol))

        pool = await self.get_pool(tokenAsymbol, tokenBsymbol)

        pool = self.set_checksum(pool)

        await self.sync(pool)

        amountBout = await self.get_amount_out(pool, tokenAsymbol, amountIn)
        # decimal = await self.decimals(tokenBsymbol)
        # amountout = self.to_value(value=amountBout, exp=decimal)

        # result["amountBout"] = amountout

        return result

    @retry
    async def create_swap(
        self, amountA, tokenAsymbol, amountBMin, tokenBsymbol, path=None, *args, **kwargs
    ):
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

        await self.load_exchange(self.chainName, self.exchangeName)

        if (path != None) and (len(path) > 2):
            self.path = [self.set_checksum(self.tokens[token]["contract"]) for token in path[1:-1]]

        else:
            self.path = []

        self.tokenSymbol = tokenAsymbol
        self.tokenBsymbol = tokenBsymbol
        self.amount = amountA

        # self.require(amountA <= amountBMin, ValueError("amountA is Less then amountBMin"))
        self.require(tokenAsymbol == tokenBsymbol, ValueError("Same Symbol"))

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]
        amountA = self.from_value(value=amountA, exp=int(tokenA["decimals"]))
        # amountBMin = self.from_value(value=amountBMin, exp=int(tokenB["decimals"]))
        amountBMin = 1

        tokenAaddress = self.set_checksum(tokenA["contract"])
        tokenBaddress = self.set_checksum(tokenB["contract"])
        self.account = self.set_checksum(self.account)
        routerAddress = self.set_checksum(self.markets["routerAddress"][0])

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        build = {
            "from": self.account,
            "gas": 4000000,
            "nonce": self.nonce,
        }

        await self.check_approve(
            amount=amountA,
            token=tokenAaddress,
            account=self.account,
            router=routerAddress,
            build=build,
        )

        self.routerContract = await self.get_contract(routerAddress, self.markets["routerAbi"][0])

        current_nonce = await self.w3.eth.get_transaction_count(self.account)
        self.nonce = current_nonce + self.addNounce

        build["nonce"] = self.nonce

        if tokenAsymbol == self.baseCurrency:
            tx = await self.eth_to_token(amountA, tokenBaddress, amountBMin, build)
        # elif tokenBsymbol == self.baseCurrency:
        #     tx = self.token_to_eth(tokenAaddress, amountA)
        else:
            tx = await self.token_to_token(tokenAaddress, amountA, tokenBaddress, amountBMin, build)

        # gas = await self.w3.eth.estimate_gas(tx)
        # tx["gas"] = gas

        tx_receipt = await self.fetch_transaction(tx, "SWAP")

        return tx_receipt

    async def token_to_token(self, tokenAaddress, amountA, tokenBaddress, amountBMin, build):
        tx = await self.routerContract.functions.exchangeKctPos(
            tokenAaddress, amountA, tokenBaddress, amountBMin, self.path
        ).build_transaction(build)

        return tx

    async def eth_to_token(self, amountA, tokenBaddress, amountBMin, build):

        build["value"] = amountA

        tx = await self.routerContract.functions.exchangeKlayPos(
            tokenBaddress, amountBMin, self.path
        ).build_transaction(build)

        return tx

    # def token_to_eth(self, tokenAaddress, amountA):

    #     tx = self.routerContract.functions.exchangeKlayNeg(
    #         tokenAaddress, amountA, self.path
    #     ).build_transaction(
    #         {
    #             "from": self.account,
    #             "gas": 4000000,
    #             "nonce": self.nonce,
    #         }
    #     )

    #     return tx

    async def get_amount_out(self, pool, tokenAsymbol, amountIn):
        tokenA = self.tokens[tokenAsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])

        poolAddress = self.set_checksum(pool)

        # self.factoryContract = await self.get_contract(poolAddress, self.markets["routerAbi"])

        self.factoryContract = await self.get_contract(poolAddress, self.markets["routerAbi"][0])

        amountOut = await self.factoryContract.functions.estimatePos(tokenAaddress, amountIn).call()

        amountOut = await self.factoryContract.functions.estimatePos

        # amountOut = type(self.factoryContract.functions.estimatePos(tokenAaddress, amountIn).call())

        return amountOut

    async def get_reserves(self, tokenAsymbol, tokenBsymbol):
        pool = self.get_pool(tokenAsymbol, tokenBsymbol)

        pool = self.set_checksum(pool)

        tokenA = self.tokens[tokenAsymbol]

        tokenAaddress = self.set_checksum(tokenA["contract"])

        factoryContract = await self.get_contract(pool, self.markets["factoryAbi"])

        tokenA = factoryContract.functions.tokenA().call()

        routerContract = await self.get_contract(pool, self.markets["routerAbi"][0])
        reserves = await routerContract.functions.getCurrentPool().call()

        if tokenA != tokenAaddress:
            reservesA = self.to_value(reserves[1], await self.decimals(tokenAsymbol))
            reservesB = self.to_value(reserves[0], await self.decimals(tokenBsymbol))

        else:
            reservesA = self.to_value(reserves[0], await self.decimals(tokenAsymbol))
            reservesB = self.to_value(reserves[1], await self.decimals(tokenBsymbol))

        reserve = reservesB / reservesA

        return {
            "pool": f"{tokenAsymbol}-{tokenBsymbol}",
            "tokenAsymbol": tokenAsymbol,
            "tokenBsymbol": tokenBsymbol,
            "tokenAreserves": reservesA,
            "tokenBreserves": reservesB,
            "poolPrice": reserve,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # def set_logger(self, logfilePath):

    #     if logfilePath == None :

    #         #default_log
    #         basePath = Path(__file__).resolve().parent.parent
    #         logfile_name = 'logfile.log'
    #         logfilePath = str(os.path.join(basePath, logfile_name))

    #     print(logfilePath)

    #     logging.basicConfig(
    #         level=logging.INFO,
    #         filename=logfilePath,
    #         filemode="w",
    #         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    #     )

    #     # logging.Formatter.converter = lambda *args: datetime.datetime.now(
    #     #     tz=timezone("Asia/Seoul")
    #     # ).timetuple()

    #     # log_formatter = logging.Formatter(
    #     #     fmt ="%(asctime)s - %(name)s - %(levelname)s - %(message)s",

    #     # )

    #     # log_formatter.converter = lambda *args: datetime.datetime.now(
    #     #     tz=timezone("Asia/Seoul")
    #     # ).timetuple()

    #     # file_log = RotatingFileHandler(
    #     #     filename=logfilePath,
    #     #     mode="a",
    #     #     maxBytes=5 * 1024 * 1024,
    #     #     backupCount=2,
    #     #     encoding=None,
    #     #     delay=0,
    #     # )

    #     # file_log.setFormatter(log_formatter)
    #     # file_log.setLevel(logging.INFO)

    #     self.logger = logging.getLogger(__name__)

    #     print("test log")
