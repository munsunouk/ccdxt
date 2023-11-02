from ..base.exchange import Exchange
from ..base.utils.errors import InsufficientBalance

# from ..base.utils.validation import *
from ..base.utils.retry import retry

from eth_typing import HexAddress
from eth_typing.evm import Address, ChecksumAddress

from web3.logs import DISCARD
import logging
import datetime


class Multichain(Exchange):
    # https://github.com/andrecronje/anyswap-v1-core/blob/master/contracts/AnyswapV3Router.sol

    has = {
        "create_bridge": True,
        "fetchTicker": True,
        "fetchBalance": True,
    }

    def __init__(self, config):
        super().__init__()

        # market info
        self.id = 3
        # self.chainName = "MULTI"
        self.exchangeName = "multichain"
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.addNounce = 0
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]

        self.load_bridge(self.exchangeName)
        self.set_logger(self.log)

    async def anySwapInAuto(self, tx_hash, tokenSymbol, amount, from_dex, to_dex):
        self.host = to_dex.host
        self.load_exchange(to_dex.chainName)

        token = self.tokens[tokenSymbol]
        anytoken = token["destChains"][from_dex.chainName]["fromanytoken"]
        bridgeAddress = token["destChains"][from_dex.chainName]["router"]

        fromChain = from_dex.chains["mainnet"]["chain_id"]

        tokenAddress = self.set_checksum(anytoken)
        bridgeAddress = self.set_checksum(bridgeAddress)

        amount = self.from_value(value=amount, exp=int(token["decimals"]))

        self.nonce = self.pv_w3.eth.get_transaction_count(self.account)

        self.routerContract = self.get_contract(bridgeAddress, self.bridge["bridgeAbi"])

        tx = self.routerContract.functions.anySwapInUnderlying(
            tx_hash, tokenAddress, self.account, amount, fromChain
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )

        tx_receipt = self.fetch_transaction(tx, round="WITHDRAW")

        return tx_receipt

    async def withdraw(self, amount, tokenSymbol, from_dex, to_dex):
        self.host = to_dex.host
        self.load_exchange(to_dex.chainName)

        token = self.tokens[tokenSymbol]
        anytoken = token["destChains"][from_dex.chainName]["fromanytoken"]
        amount = self.from_value(value=amount, exp=int(token["decimals"]))

        tokenAddress = self.set_checksum(anytoken)

        self.nonce = self.pv_w3.eth.get_transaction_count(self.account)

        self.routerContract = self.get_contract(tokenAddress, self.bridge["bridgeAbi"])

        tx = self.routerContract.functions.withdraw(amount).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )

        tx_receipt = self.fetch_transaction(tx, round="WITHDRAW")

        return tx_receipt

    @retry
    # async def create_bridge(self, amount, tokenSymbol, fromChain, toChain, toAddr):
    async def create_bridge(
        self, amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, toAddr, *args
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
        self.load_exchange(fromChain)

        self.baseCurrency = self.chains["baseCurrency"]
        self.tokenSymbol = from_tokenSymbol
        self.fromChain = fromChain
        self.toChain = toChain
        self.amount = amount

        token = self.tokens[from_tokenSymbol]
        anytoken = token["destChains"][toChain]["fromanytoken"]

        bridgeAddress = token["destChains"][toChain]["router"]
        bridgeFunction = token["destChains"][toChain]["routerABI"]

        toChainId = token["destChains"][toChain]["ID"]

        tokenBalance = self.partial_balance(from_tokenSymbol)

        self.require(fromChain == toChain, ValueError("Same Chain"))
        self.require(
            token["MinimumBridge"] >= tokenBalance["balance"],
            InsufficientBalance(tokenBalance, token["MinimumBridge"]),
        )

        amount = self.from_value(value=amount, exp=int(token["decimals"]))

        tokenAddress = self.set_checksum(token["contract"])
        anytokenAddress = self.set_checksum(anytoken)
        self.account = self.set_checksum(self.account)
        self.toAddrress = self.set_checksum(toAddr)

        bridgeAddress = self.set_checksum(bridgeAddress)

        # TODO Hardcoding -> Soft
        self.bridge_token = "LogAnySwapOut"
        self.check_approve(
            amount=amount, token=tokenAddress, account=self.account, router=bridgeAddress
        )

        logging.info("pass_approved")

        self.nonce = self.pv_w3.eth.get_transaction_count(self.account) + self.addNounce

        self.routerContract = self.get_contract(bridgeAddress, self.bridge["bridgeAbi"])

        if from_tokenSymbol == self.baseCurrency:
            tx = self._anySwapOutNative(anytokenAddress, toChainId, self.toAddrress, amount)

        else:
            logging.info(
                f"params : {anytokenAddress, toChainId, self.toAddrress, amount, bridgeFunction}"
            )

            tx = self._anySwapOut(
                anytokenAddress, toChainId, self.toAddrress, amount, bridgeFunction
            )

        tx_receipt = self.fetch_transaction(tx, round="BRIDGE")

        fee = self._calculate_bridge_fee(tx_receipt["amountIn"], toChain, from_tokenSymbol)

        tx_receipt["amountIn"] = tx_receipt["amountIn"] - fee

        self.amount = tx_receipt["amountIn"]

        time_spend, amount = self.check_bridge_completed(to_tokenSymbol, self.toAddrress)

        return tx_receipt

    def _anySwapOutNative(
        self, tokenAddress: ChecksumAddress, toChainId: int, toAddr: ChecksumAddress, amount: int
    ):
        # nonce = self.w3.eth.get_transaction_count(self.account)

        tx = self.routerContract.functions.anySwapOutNative(
            tokenAddress, toAddr, toChainId
        ).build_transaction(
            {
                "from": self.account,
                # 'gas' : 4000000,
                "nonce": self.nonce,
                "value": amount,
            }
        )

        return tx

    def _anySwapOut(
        self,
        tokenAddress: ChecksumAddress,
        toChainId: int,
        toAddr: ChecksumAddress,
        amount: int,
        bridgeFunction: str,
    ):
        # result = requests.get('https://gasstation-mainnet.matic.network/v2').json()

        # fast_maxPriorityFeePerGas = result['fast']['maxPriorityFee']
        # fast_maxFeePerGas = result['fast']['maxFee']

        # nonce = self.w3.eth.get_transaction_count(self.account)

        tx = self.routerContract.functions[bridgeFunction](
            tokenAddress, toAddr, amount, toChainId
        ).build_transaction(
            {
                "from": self.account,
                "nonce": self.nonce,
            }
        )

        return tx

    def _calculate_bridge_fee(self, amountOut, toChain, tokenSymbol):
        fee = amountOut * ((self.bridge["fee"] / 100))

        token = self.tokens[tokenSymbol]

        if "destChains" in token:
            if float(token["destChains"][toChain]["MinimumSwap"]) > amountOut:
                fee = amountOut

            else:
                if fee > float(token["destChains"][toChain]["MinimumSwapFee"]):
                    fee = fee

                else:
                    fee = float(token["destChains"][toChain]["MinimumSwapFee"])

        else:
            pass

        return fee

    def check_bridge_completed(self, tokenSymbol, toAddr):
        start_bridge = datetime.datetime.now()

        start_time = datetime.datetime.now()

        current_account = self.account

        self.account = toAddr

        start_balance = self.partial_balance(tokenSymbol)

        while True:
            current_time = datetime.datetime.now()

            current_balance = self.partial_balance(tokenSymbol)

            if (
                ((current_balance["balance"] - start_balance["balance"]) >= (self.amount))
                or (current_balance["balance"] >= self.amount)
                or (current_time - start_time).seconds > 1800
            ):
                break

        end_bridge = datetime.datetime.now()

        bridge_time = (end_bridge - start_bridge).seconds

        time_spend = {"bridge_time": bridge_time}

        self.account = current_account

        balance = self.from_value(current_balance["balance"], self.decimals(tokenSymbol))

        return time_spend, balance

    def decode(self, tokenSymbol, fromChain, tx_hash):
        self.load_bridge(self.exchangeName)
        self.load_exchange(fromChain)

        token = self.tokens[tokenSymbol]

        bridgeAddress = self.bridge["type"][token["bridge"]]["bridgeAddress"][token["chain"]][
            fromChain
        ]

        bridgeAddress = self.set_checksum(bridgeAddress)

        routerContract = self.get_contract(
            bridgeAddress, self.bridge["type"]["Minter"]["bridgeAbi"]
        )

        transaction = self.w3.eth.get_transaction(tx_hash)

        result = routerContract.decode_function_input(transaction.input)
        # result = result[1]
        # result = deposit.processReceipt(tx_hash,errors=DISCARD)

        return result

    def decode(self, tokenSymbol, fromChain, toChain, tx_hash):
        self.load_bridge(self.exchangeName)
        self.load_exchange(fromChain)

        token = self.tokens[tokenSymbol]

        tokenAaddress = self.set_checksum(token["destChains"][toChain]["fromanytoken"])

        tokenContract = self.get_contract(tokenAaddress, self.bridge["bridgeAbi"])

        bridgeAddress = token["destChains"][toChain]["router"]

        bridgeAddress = self.set_checksum(bridgeAddress)

        routerContract = self.get_contract(bridgeAddress, self.bridge["bridgeAbi"])

        transaction = self.pv_w3.eth.get_transaction(tx_hash)

        result = routerContract.decode_function_input(transaction.input)

        # result = tokenContract.decode_function_input(transaction.input)

        return result
