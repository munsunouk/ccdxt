from web3.exceptions import ContractLogicError
from web3.exceptions import ABIFunctionNotFound
error_hierarchy = {
    'BaseError': {
        'ExchangeError': {
            'AuthenticationError': {
                'PermissionDenied': {
                    'AccountNotEnabled': {},
                },
                'AccountSuspended': {},
            },
            'ArgumentsRequired': {},
            'BadRequest': {
                'BadSymbol': {},
                'MarginModeAlreadySet': {},
            },
            'BadResponse': {
                'NullResponse': {},
            },
            'InsufficientFunds': {},
            'InvalidToken' : {},
            'InsufficientBalance' : {},
            
            'InvalidAddress': {
                'AddressPending': {},
            },
            'InvalidOrder': {
                'OrderNotFound': {},
                'OrderNotCached': {},
                'CancelPending': {},
                'OrderImmediatelyFillable': {},
                'OrderNotFillable': {},
                'DuplicateOrderId': {},
            },
            'NotSupported': {},
        },
        'NetworkError': {
            'DDoSProtection': {
                'RateLimitExceeded': {},
            },
            'ExchangeNotAvailable': {
                'OnMaintenance': {},
            },
            'InvalidNonce': {},
            'RequestTimeout': {},
        },
        'ContractLogicError' : {},
        'ABIFunctionNotFound' : {},
    },
}


class BaseError(Exception):
    pass


class ExchangeError(BaseError):
    pass


class AuthenticationError(ExchangeError):
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

from typing import Any


class InvalidToken(ExchangeError):
    """Raised when an invalid token address is used."""

    def __init__(self, address: Any) -> None:
        Exception.__init__(self, f"Invalid token address: {address}")


class InsufficientBalance(ExchangeError):
    """Raised when the account has insufficient balance for a transaction."""

    def __init__(self, had: int, needed: int) -> None:
        Exception.__init__(self, f"Insufficient balance. Had {had}, needed {needed}")

class RequestTimeout(NetworkError):
    pass

class ContractLogicError(ContractLogicError):
    pass

class ABIFunctionNotFound(ABIFunctionNotFound) :
    pass

__all__ = [
    'error_hierarchy',
    'InvalidToken',
    'InsufficientBalance',
    'ABIFunctionNotFound',
    'BaseError',
    'ExchangeError',
    'AuthenticationError',
    'PermissionDenied',
    'AccountNotEnabled',
    'AccountSuspended',
    'ArgumentsRequired',
    'BadRequest',
    'BadSymbol',
    'MarginModeAlreadySet',
    'BadResponse',
    'NullResponse',
    'InsufficientFunds',
    'InvalidAddress',
    'AddressPending',
    'InvalidOrder',
    'OrderNotFound',
    'OrderNotCached',
    'CancelPending',
    'OrderImmediatelyFillable',
    'OrderNotFillable',
    'DuplicateOrderId',
    'NotSupported',
    'NetworkError',
    'DDoSProtection',
    'RateLimitExceeded',
    'ExchangeNotAvailable',
    'OnMaintenance',
    'InvalidNonce',
    'RequestTimeout',
    'ContractLogicError',
]