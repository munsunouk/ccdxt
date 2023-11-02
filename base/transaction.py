from web3.logs import DISCARD
from web3.datastructures import AttributeDict
from web3.types import TxParams, Wei, HexBytes, Address
from web3._utils.threads import Timeout

from ccdxt.base.utils.errors import (
    ReplacementTransactionUnderpriced,
    InsufficientBalance,
    alwaysFail,
    TransactionPending,
    UnknownTransaction,
    NetworkError,
    TransactionDisallowed,
)
from ccdxt.base.event import Event

from enum import Enum
import datetime
import time
import json
import logging
import time
from typing import Optional, Union, Dict, Any
from ccdxt.base.utils.retry import retry_normal

# from pytz import timezone


class Transaction(object):
    def __init__(
        self,
    ):
        self.transaction_hash = None
        self.status = None
        self.block = None
        self.created_at = None
        # self.from = None
        self.amountIn = None
        self.to = None
        self.amountOut = None
        self.gas_fee = None

        self.event = Event

    def inspect_client_error(self, val_err: ValueError):
        """
        Info
        ----------
        Inspects a ValueError raised by the client and raises a corresponding custom error if necessary.

        Parameters
        ----------
        val_err: ValueError
            The ValueError raised by the client.

        Returns
        ------
        InsufficientBalance
            If the error message indicates insufficient funds.
        alwaysFail
            If the error message indicates that the transaction always fails.
        ReplacementTransactionUnderpriced
            If the error message indicates that the replacement transaction is underpriced.
        TransactionPending
            If the error message indicates that the transaction is known.
        UnknownTransaction
            If the error message indicates that the transaction is unknown.
        """

        json_response = str(val_err).replace("'", '"').replace('("', "(").replace('")', ")")
        error = json.loads(json_response)

        if error["code"] == -32000:
            if "insufficient funds" in error["message"]:
                return InsufficientBalance
            elif "always failing transaction" in error["message"]:
                return alwaysFail
            elif error["message"] == "replacement transaction underpriced":
                return ReplacementTransactionUnderpriced
            elif error["message"].startswith("nonce too low"):
                return ReplacementTransactionUnderpriced
            elif error["message"].startswith("known transaction:"):
                return TransactionPending
            elif error["message"].startswith("Could not find"):
                return UnknownTransaction
            elif error["message"].startswith("invalid unit price"):
                return UnknownTransaction
            elif error["message"].startswith("there is another tx"):
                return ReplacementTransactionUnderpriced

    def fetch_transaction(self, tx, round=None, api=None, *args, **kwargs):
        """
        Info
        ----------
        Takes a built transaction and transmits it to Ethereum.

        Parameters
        ----------
        tx : Transaction
            The transaction to be transmitted.
        round : str, optional
            The round of the transaction, either "CHECK", "BRIDGE", or "SWAP".

        Returns
        -------
        Transaction receipt = Swap

        {
            'transaction_hash' : tx_receipt['transactionHash'].hex(),
            'status' : tx_receipt["status"],
            'block' :  tx_receipt['blockNumber'],
            'created_at' : datetime.datetime.now(),
            'function' : str(function),
            'from' : tx_receipt['from'],
            'amountIn' : amount_in,
            'tokenA' : self.tokenSymbol,
            'to' : tx_receipt['to'],
            'from_chain' : self.fromChain,
            'to_chain' : self.toChain,
            'gas_fee:' : tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18 ,
        }
        """

        if round == "FUSION_SWAP":
            return self.fetch_fusion_swap(tx)

        elif round == "FAIL":
            return self.fetch_trade_fail()

        else:
            pass

        tokenBalance = self.partial_balance(self.tokenSymbol)
        baseCurrency = self.partial_balance(self.chains["baseCurrency"])
        gas = self.w3.eth.estimate_gas(tx)

        self.gas_fee = self.to_value(
            value=int(int(gas) * self.gas_price), exp=self.decimals(self.chains["baseCurrency"])
        )

        # self.require(self.check_sync() == True, NetworkError("Network sync fail"))

        if round == "ADD":
            pass

        else:
            self.require(
                self.amount > tokenBalance["balance"],
                InsufficientBalance(tokenBalance, f"need :{self.amount}"),
            )

        self.require(
            self.least_balance > baseCurrency["balance"],
            InsufficientBalance(baseCurrency, f"at lest need : {self.least_balance}"),
        )
        self.require(
            self.endurable_gasFee < self.gas_fee,
            TransactionDisallowed(
                self.gas_fee,
                f"gasfee :{self.gas_fee} should be less then endurable_gasFee :{self.endurable_gasFee}",
            ),
        )

        signed_tx = self.w3.eth.account.signTransaction(tx, self.privateKey)

        try:
            self.tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.get_tx_receipt()
        except ValueError as e:
            action = self.inspect_client_error(e)
            if action == InsufficientBalance:
                raise InsufficientBalance("Insufficient Token for transaction")
            elif action == ReplacementTransactionUnderpriced:
                raise ReplacementTransactionUnderpriced(
                    "Transaction was rejected. This is potentially "
                    "caused by the reuse of the previous transaction "
                    "nonce as well as paying an amount of gas less than or "
                    "equal to the previous transaction's gas amount"
                )
            elif action == UnknownTransaction:
                raise UnknownTransaction("maybe invalid unit price")
        except Timeout:
            if hasattr(self, "get_transaction"):
                function = getattr(self, "get_transaction")
                tx_receipt = function(self.tx_hash)
            else:
                logging.info("Function", "get_transaction", "does not exist in the class")

        # self.tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        tx_receipt = self.get_tx_receipt()

        if tx_receipt["status"] != 1:
            return self.fetch_trade_fail(self.tx_hash)

        if round == "CHECK":
            return self.logger.info("approved token")

        if round == "DEPOSIT":
            return self.logger.info("wrapped token")

        if round == "WITHDRAW":
            return self.logger.info("unwrapped token")

        if round == "BRIDGE":
            return self.fetch_bridge(tx, tx_receipt, api)

        if round == "SWAP":
            return self.fetch_swap(tx, tx_receipt, api)

        if round == "TRANSFER":
            return self.fetch_transfer(tx, tx_receipt, api)

        if round == "ADD":
            # return self.fetch_add_liquidity(tx, tx_receipt, api, payload=kwargs['payload'])
            return self.fetch_add_liquidity(tx, tx_receipt, api)

        if round == "REMOVE":
            # return self.fetch_remove_liquidity(tx, tx_receipt, api, payload=kwargs['payload'])
            return self.fetch_remove_liquidity(tx, tx_receipt, api)

    def fetch_add_liquidity(
        self, tx: Optional[AttributeDict] = None, tx_receipt=None, api=False, *args, **kwargs
    ) -> Dict[str, Any]:
        """
        Info
        ----------
        Fetches the details of a swap transaction.

        Parameters:
        ----------
        - tx (dict): Transaction object.
        - tx_receipt (dict): Transaction receipt object.

        Returns:
        ----------
        - txDict (dict): Dictionary containing the transaction details.
        """

        if tx is None and tx_receipt is None:
            raise ValueError("Either 'tx' or 'tx_receipt' must be provided.")

        if (tx is not None) and (tx_receipt is None):
            tx_receipt = self.get_transaction_receipt(tx)

        if (tx is None) and (tx_receipt is not None):
            raise ValueError("tx should be provided")

            # tx = self.w3.eth.get_transaction(tx_hash)

        else:
            try:
                function, input_args = self.routerContract.decode_function_input(
                    self.get_transaction_data_field(tx)
                )
                fn_name = str(function.fn_name)

            except:
                fn_name = "addLiquidity"

        txDict = {
            "tx_hash": tx_receipt["transactionHash"].hex(),
            "status": tx_receipt["status"],
            "block": tx_receipt["blockNumber"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": fn_name,
            "pool_name": self.pool_name,
            "pool_address": self.poolAddress,
            "address": tx_receipt["from"],
            "input": self.input,
            "gas_fee": tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"] / 10**18
            + self.additionalGasFee,
            "tx_scope": f"{self.chains['mainnet']['block_scope']}/tx/{tx_receipt['transactionHash'].hex()}",
        }

        return txDict

    def fetch_remove_liquidity(
        self, tx: Optional[AttributeDict] = None, tx_receipt=None, api=False, *args, **kwargs
    ) -> Dict[str, Any]:
        """
        Info
        ----------
        Fetches the details of a swap transaction.

        Parameters:
        ----------
        - tx (dict): Transaction object.
        - tx_receipt (dict): Transaction receipt object.

        Returns:
        ----------
        - txDict (dict): Dictionary containing the transaction details.
        """

        if tx is None and tx_receipt is None:
            raise ValueError("Either 'tx' or 'tx_receipt' must be provided.")

        if (tx is not None) and (tx_receipt is None):
            tx_receipt = self.get_transaction_receipt(tx)

        if (tx is None) and (tx_receipt is not None):
            raise ValueError("tx should be provided")

            # tx = self.w3.eth.get_transaction(tx_hash)

        else:
            try:
                function, input_args = self.routerContract.decode_function_input(
                    self.get_transaction_data_field(tx)
                )
                fn_name = str(function.fn_name)

            except:
                fn_name = "removeLiquidity"

        txDict = {
            "tx_hash": tx_receipt["transactionHash"].hex(),
            "status": tx_receipt["status"],
            "block": tx_receipt["blockNumber"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": fn_name,
            "pool_name": self.pool_name,
            "pool_address": self.poolAddress,
            "address": tx_receipt["from"],
            "input": self.input,
            "gas_fee": tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"] / 10**18
            + self.additionalGasFee,
            "tx_scope": f"{self.chains['mainnet']['block_scope']}/tx/{tx_receipt['transactionHash'].hex()}",
        }

        return txDict

    def fetch_transfer(self, tx, tx_receipt, api=False):
        """
        Info
        ----------
        Returns a dictionary containing information about a bridge transaction.

        Parameters:
        ----------
        - tx: A transaction object.
        - tx_receipt: A transaction receipt object.

        Returns:
        ----------
        - A dictionary containing the following keys:
            * transaction_hash: the hash of the transaction
            * status: the status of the transaction (either 1 for success or 0 for failure)
            * block: the block number in which the transaction was included
            * created_at: the created_at of when the transaction was processed
            * function: the function name that was called in the transaction
            * from: the chain where the transaction originated
            * amountIn: the amount of tokenA that was sent in the transaction
            * tokenA: the symbol of the token being sent in the transaction
            * to: the chain where the transaction was sent
            * amountOut: the amount of tokenB received in the transaction
            * tokenB: the symbol of the token being received in the transaction
            * gas_fee: the fee paid for the transaction in ETH
        """

        # amount_in = Event.transfer(
        #     self.bridge["name"],
        #     tx_receipt,
        #     self.routerContract,
        # )

        # amount_in = self.amount

        # amount_in = self.to_value(amount_in, self.decimals(self.tokenSymbol))

        if tx is None and tx_receipt is None:
            raise ValueError("Either 'tx' or 'tx_receipt' must be provided.")

        if (tx is not None) and (tx_receipt is None):
            tx_receipt = self.get_transaction_receipt(tx)

        if (tx is None) and (tx_receipt is not None):
            pass

            # function = self.decode(tx_receipt)[0].fn_name

        else:
            transaction = self.w3.eth.get_transaction(self.tx_hash)

            # function, input_args = self.routerContract.decode_function_input(
            #     transaction.input
            #     # self.get_transaction_data_field(tx)
            # )

        txDict = {
            "from_network": self.fromChain,
            "to_network": self.toChain,
            "tx_hash": tx_receipt["transactionHash"].hex(),
            "status": tx_receipt["status"],
            "block": tx_receipt["blockNumber"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": "Transfer",
            "from_address": tx_receipt["from"],
            # "amount_in": amount_in,
            "token_in": self.tokenSymbol,
            "to_address": self.toAddrress,
            # "amount_out": amount_in,
            "token_out": self.tokenSymbol,
            "gas_fee": tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"] / 10**18
            + self.additionalGasFee,
            "tx_scope": f"{self.chains['mainnet']['block_scope']}/tx/{tx_receipt['transactionHash'].hex()}",
        }

        return txDict

    def fetch_bridge(self, tx, tx_receipt, api=None, *args, **kwargs):
        """
        Info
        ----------
        Returns a dictionary containing information about a bridge transaction.

        Parameters:
        ----------
        - tx: A transaction object.
        - tx_receipt: A transaction receipt object.

        Returns:
        ----------
        - A dictionary containing the following keys:
            * transaction_hash: the hash of the transaction
            * status: the status of the transaction (either 1 for success or 0 for failure)
            * block: the block number in which the transaction was included
            * created_at: the created_at of when the transaction was processed
            * function: the function name that was called in the transaction
            * from: the chain where the transaction originated
            * amountIn: the amount of tokenA that was sent in the transaction
            * tokenA: the symbol of the token being sent in the transaction
            * to: the chain where the transaction was sent
            * amountOut: the amount of tokenB received in the transaction
            * tokenB: the symbol of the token being received in the transaction
            * gas_fee: the fee paid for the transaction in ETH
        """

        amount_in = Event.bridge(self.bridge["name"], tx_receipt, self.routerContract, version=api)

        # amount_in = self.amount

        amount_in = self.to_value(amount_in, self.decimals(self.tokenSymbol))

        if tx is None and tx_receipt is None:
            raise ValueError("Either 'tx' or 'tx_receipt' must be provided.")

        if (tx is not None) and (tx_receipt is None):
            tx_receipt = self.get_transaction_receipt(tx)

        if (tx is None) and (tx_receipt is not None):
            pass

            # function = self.decode(tx_receipt)[0].fn_name

        else:
            transaction = self.w3.eth.get_transaction(self.tx_hash)

            function, input_args = self.routerContract.decode_function_input(
                transaction.input
                # self.get_transaction_data_field(tx)
            )

        txDict = {
            "from_network": self.fromChain,
            "to_network": self.toChain,
            "tx_hash": tx_receipt["transactionHash"].hex(),
            "status": tx_receipt["status"],
            "block": tx_receipt["blockNumber"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": str(function.fn_name),
            "from_address": tx_receipt["from"],
            "amount_in": amount_in,
            "token_in": self.tokenSymbol,
            "to_address": self.toAddrress,
            "amount_out": amount_in,
            "token_out": self.tokenSymbol,
            "gas_fee": tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"] / 10**18
            + self.additionalGasFee,
            "tx_scope": f"{self.chains['mainnet']['block_scope']}/tx/{tx_receipt['transactionHash'].hex()}",
        }

        return txDict

    def fetch_fusion_swap(self, tx: Optional[AttributeDict] = None):
        amountIn = self.to_value(int(tx["order"]["makingAmount"]), self.decimals(self.tokenSymbol))
        amountOut = self.to_value(
            int(tx["order"]["takingAmount"]), self.decimals(self.tokenBsymbol)
        )

        txDict = {
            "from_network": self.chains["name"],
            "to_network": self.chains["name"],
            "tx_hash": None,
            "status": 1,
            "block": None,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": str(function.fn_name),
            "from_address": tx["order"]["maker"],
            "amount_in": amountIn,
            "token_in": self.tokenSymbol,
            "to_address": tx["order"]["maker"],
            "amount_out": amountOut,
            "token_out": self.tokenBsymbol,
            "gas_fee": 0,
        }

        return txDict

    def fetch_swap(
        self, tx: Optional[AttributeDict] = None, tx_receipt=None, api=False
    ) -> Dict[str, Any]:
        """
        Info
        ----------
        Fetches the details of a swap transaction.

        Parameters:
        ----------
        - tx (dict): Transaction object.
        - tx_receipt (dict): Transaction receipt object.

        Returns:
        ----------
        - txDict (dict): Dictionary containing the transaction details.
        """

        if tx is None and tx_receipt is None:
            raise ValueError("Either 'tx' or 'tx_receipt' must be provided.")

        if (tx is not None) and (tx_receipt is None):
            tx_receipt = self.get_transaction_receipt(tx)

        if (tx is None) and (tx_receipt is not None):
            raise ValueError("tx should be provided")

            # tx = self.w3.eth.get_transaction(tx_hash)

        else:
            try:
                function, input_args = self.routerContract.decode_function_input(
                    self.get_transaction_data_field(tx)
                )
                fn_name = str(function.fn_name)

            except:
                fn_name = "swap"

        if not api:
            amountIn, amountOut = Event.swap(
                self.chains["name"],
                self.markets["name"],
                tx_receipt,
                self.routerContract,
            )

        else:
            params = {"hash": tx_receipt["transactionHash"].hex()}

            logging.info(f"hash : {tx_receipt['transactionHash'].hex()}")

            quote_total_tx = self.create_request(
                params, "v3", f'{self.chains["mainnet"]["chain_id"]}', "getTransaction"
            )

            logging.info(f"result : {quote_total_tx}")

            amountIn = int(quote_total_tx["in_amount"])
            amountOut = int(quote_total_tx["out_amount"])

        amountIn = self.to_value(amountIn, self.decimals(self.tokenSymbol))
        amountOut = self.to_value(amountOut, self.decimals(self.tokenBsymbol))

        txDict = {
            "from_network": self.chains["name"],
            "to_network": self.chains["name"],
            "tx_hash": tx_receipt["transactionHash"].hex(),
            "status": tx_receipt["status"],
            "block": tx_receipt["blockNumber"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": fn_name,
            "from_address": tx_receipt["from"],
            "amount_in": amountIn,
            "token_in": self.tokenSymbol,
            "to_address": tx_receipt["to"],
            "amount_out": amountOut,
            "token_out": self.tokenBsymbol,
            "gas_fee": tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"] / 10**18
            + self.additionalGasFee,
            "tx_scope": f"{self.chains['mainnet']['block_scope']}/tx/{tx_receipt['transactionHash'].hex()}",
        }

        return txDict

    def fetch_trade_fail(self, tx_hash=""):
        self.logger.info("fail")

        if tx_hash:
            blockNumber = self.w3.eth.get_transaction(tx_hash).blockNumber
            tx_hash = tx_hash.hex()

        else:
            blockNumber = ""

        txDict = {
            "from_network": self.chains["name"],
            "to_network": self.chains["name"],
            "tx_hash": tx_hash,
            "status": 2,  # pending
            "block": blockNumber,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": "",
            "from_address": "",
            "amount_in": 0,
            "token_in": self.tokenSymbol,
            "to_address": "",
            "amount_out": 0,
            "token_out": self.tokenBsymbol,
            "gas_fee": 0,
            "tx_scope": "",
        }

        return txDict

    def get_transaction_data_field(self, tx: AttributeDict) -> str:
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

    @retry_normal
    def get_tx_receipt(self):
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.tx_hash, timeout=self.timeOut)

        return tx_receipt
