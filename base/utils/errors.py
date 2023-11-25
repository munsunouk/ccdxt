from web3.exceptions import ContractLogicError
from web3.exceptions import NoABIFunctionsFound
from web3.exceptions import TransactionNotFound
from web3.exceptions import BadResponseFormat
from typing import Optional
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError

# ccxt error handling + web3 error handling

error_hierarchy = {
    "BaseError": {
        "ExchangeError": {
            "AuthenticationError": {
                "BadResponseFormat": {},
                "PermissionDenied": {
                    "AccountNotEnabled": {},
                },
                "AccountSuspended": {},
            },
            "ArgumentsRequired": {},
            "BadRequest": {
                "BadSymbol": {},
                "MarginModeAlreadySet": {},
            },
            "BadResponse": {"NullResponse": {}, "HTTPError": {}},
            "alwaysFail": {},
            "InsufficientFunds": {},
            "InvalidToken": {},
            "InsufficientBalance": {},
            "InvalidAddress": {
                "AddressPending": {},
            },
            "InvalidOrder": {
                "OrderNotFound": {},
                "OrderNotCached": {},
                "CancelPending": {},
                "OrderImmediatelyFillable": {},
                "OrderNotFillable": {},
                "DuplicateOrderId": {},
            },
            "NotSupported": {},
            "RevertError": {},
            "UnknownTransaction": {},
        },
        "NetworkError": {
            "DDoSProtection": {
                "RateLimitExceeded": {},
            },
            "ExchangeNotAvailable": {
                "OnMaintenance": {},
            },
            "InvalidNonce": {},
            "RequestTimeout": {},
            "RemoteDisconnected": {},
            "ProtocolError": {},
            "OSError": {},
            "ConnectionError": {},
        },
        "ValueError": {"ContractLogicError": {}, "ReplacementTransactionUnderpriced": {}},
        "ABIFunctionNotFound": {},
        "DataTypeError": {},
        "AddressError": {},
        "AssetError": {},
        "MathError": {
            "AdditionOverFlowError",
            "SubtractionOverFlowError",
            "MultiplicationOverFlowError",
            "DivisionByZero",
            "ModuloByZeroError",
            "NegativeNumbers",
        },
        "TransactionNotFound": {},
        "TransactionPending": {},
        "TooManyTriesException": {},
        "StrategyError": {},
    },
}


class BaseError(Exception):
    pass


class TooManyTriesException(Exception):
    pass


class StrategyError(Exception):
    pass


class ExchangeError(BaseError):
    pass


class AuthenticationError(ExchangeError):
    pass


class TransactionDisallowed(ExchangeError):
    pass


class PermissionDenied(AuthenticationError):
    pass


class AccountNotEnabled(PermissionDenied):
    pass


class AccountSuspended(AuthenticationError):
    pass


class ArgumentsRequired(ExchangeError):
    pass


class BadRequest(ExchangeError):
    pass


class BadSymbol(BadRequest):
    pass


class MarginModeAlreadySet(BadRequest):
    pass


class BadResponse(ExchangeError):
    pass


class NullResponse(BadResponse):
    pass


class HTTPError(BadResponse):
    pass


class alwaysFail(ExchangeError):
    pass


class InsufficientFunds(ExchangeError):
    pass


class InvalidAddress(ExchangeError):
    pass


class AddressPending(InvalidAddress):
    pass


class InvalidOrder(ExchangeError):
    pass


class OrderNotFound(InvalidOrder):
    pass


class OrderNotCached(InvalidOrder):
    pass


class CancelPending(InvalidOrder):
    pass


class OrderImmediatelyFillable(InvalidOrder):
    pass


class OrderNotFillable(InvalidOrder):
    pass


class DuplicateOrderId(InvalidOrder):
    pass


class NotSupported(ExchangeError):
    pass


class NetworkError(BaseError):
    pass


class RemoteDisconnected(NetworkError):
    pass


class DDoSProtection(NetworkError):
    pass


class RateLimitExceeded(DDoSProtection):
    pass


class ExchangeNotAvailable(NetworkError):
    pass


class OnMaintenance(ExchangeNotAvailable):
    pass


class InvalidNonce(NetworkError):
    pass


class OSError(NetworkError):
    pass


class InvalidToken(ExchangeError):
    pass


class InsufficientBalance(ExchangeError):
    pass


class RevertError(ExchangeError):

    """
    Reverts the transaction and breaks.
    All the changes of state DB in current transaction will be rolled back.
    """

    def __init__(self, message: Optional[str] = None, code: int = 0) -> None:
        Exception.__init__(self, f"Revert error: {code} or {message} is invalid")


class DataTypeError(BaseError):
    """Error when data type is invalid."""

    def __init__(self, message: Optional[str]):
        Exception.__init__(self, f"Datatype error: {message}")


class AddressError(BaseError):
    """Error when having an invalid address."""

    def __init__(self, message: Optional[str]):
        Exception.__init__(self, f"Address error: {message}")


class RequestTimeout(NetworkError):
    pass


class ConnectionError(NetworkError):
    pass


class ContractLogicError(ValueError):
    pass


class ABIFunctionNotFound(NoABIFunctionsFound):
    pass


class MathError(BaseError):
    pass


class AdditionOverFlowError(MathError):
    pass


class SubtractionOverFlowError(MathError):
    pass


class MultiplicationOverFlowError(MathError):
    pass


class DivisionByZero(MathError):
    pass


class ModuloByZeroError(MathError):
    pass


class AssetError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NegativeNumbers(MathError):
    pass


class TransactionNotFound(ExchangeError):
    pass


class TransactionPending(ExchangeError):
    pass


class UnknownTransaction(ExchangeError):
    pass


class BadResponseFormat(AuthenticationError):
    pass


class ReplacementTransactionUnderpriced(ValueError):
    """Raised when a replacement transaction is rejected by the blockchain"""

    def __init__(self, message: Optional[str]):
        Exception.__init__(self, f"replacement transaction underpriced")


__all__ = [
    "error_hierarchy",
    "InvalidToken",
    "InsufficientBalance",
    "ABIFunctionNotFound",
    "BaseError",
    "ExchangeError",
    "AuthenticationError",
    "PermissionDenied",
    "AccountNotEnabled",
    "AccountSuspended",
    "ArgumentsRequired",
    "BadRequest",
    "BadSymbol",
    "MarginModeAlreadySet",
    "BadResponse",
    "NullResponse",
    "InsufficientFunds",
    "InvalidAddress",
    "AddressPending",
    "InvalidOrder",
    "OrderNotFound",
    "OrderNotCached",
    "CancelPending",
    "OrderImmediatelyFillable",
    "OrderNotFillable",
    "DuplicateOrderId",
    "NotSupported",
    "NetworkError",
    "DDoSProtection",
    "RateLimitExceeded",
    "ExchangeNotAvailable",
    "OnMaintenance",
    "InvalidNonce",
    "RequestTimeout",
    "ContractLogicError",
    "RevertError",
    "DataTypeError",
    "AddressError",
    "AdditionOverFlowError",
    "SubtractionOverFlowError",
    "MultiplicationOverFlowError",
    "DivisionByZero",
    "ModuloByZeroError",
    "NegativeNumbers",
    "ReplacementTransactionUnderpriced",
    "TransactionNotFound",
    "TransactionPending",
    "RemoteDisconnected",
    "ProtocolError",
    "OSError",
    "TooManyTriesException",
    "alwaysFail",
    "UnknownTransaction",
    "TransactionDisallowed",
    "StrategyError",
    "AssetError",
]
