from contextlib import contextmanager
import datetime
from functools import wraps
import asyncio
import time

from ccdxt.base.utils.errors import (
    TransactionNotFound,
    ReplacementTransactionUnderpriced,
    RemoteDisconnected,
    ProtocolError,
    InsufficientBalance,
    OSError,
    ConnectionError,
    # HTTPError,
    # BadResponseFormat,
    TooManyTriesException,
    TransactionDisallowed,
)

# from gspread.exceptions import APIError
from web3.exceptions import BadResponseFormat
from web3._utils.threads import Timeout
from requests.exceptions import HTTPError, ReadTimeout, ProxyError, SSLError, ConnectTimeout
from aiohttp.client_exceptions import ServerDisconnectedError, ClientResponseError


def retry_normal(func):
    @wraps(func)
    def retry_method(self, *args, **kwargs):
        for i in range(self.retries):
            if i == 0:
                self.addNounce = i

            if i > 0:
                self.logger.warning("{} - Attempt {}".format(func.__name__, i))
                self.addNounce = i
            try:
                return func(self, *args, **kwargs)
            except Timeout:
                if i == self.retries - 1:
                    raise TooManyTriesException(func)
                self.host = self.host + 1 % self.total_node
                self.load_exchange(self.chainName, self.exchangeName)
            except (
                # APIError,
                RemoteDisconnected,
                ProtocolError,
                OSError,
                ConnectionError,
                ReadTimeout,
                HTTPError,
                BadResponseFormat,
            ) as e:
                self.logger.warning(e)
                self.host = self.host + 1 % self.total_node
                self.load_exchange(self.chainName, self.exchangeName)
                time.sleep(60)
                pass

        raise TooManyTriesException(func)

    return retry_method


def retry(func):
    """decorator that can take either coroutine or normal function"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        for i in range(10):

            if i > 2:
                self.logger.warning("{} - Attempt {}".format(func.__name__, i))
                # self.addNounce = i
                # time.sleep(self.retriesTime)

            try:
                return await func(self, *args, **kwargs)

            except (ReplacementTransactionUnderpriced, ValueError) as e:
                # await self.load_exchange(self.chainName, self.exchangeName)
                self.host = self.host + 1 % self.total_node
                self.addNounce = i % 3
                self.logger.warning(e)
                # await asyncio.sleep(10)
                pass

            except (
                # APIError,
                RemoteDisconnected,
                ProtocolError,
                OSError,
                ConnectionError,
                ReadTimeout,
                HTTPError,
                BadResponseFormat,
                Timeout,
                RuntimeError,
                ServerDisconnectedError,
                ClientResponseError,
            ) as e:
                self.logger.warning(e)

                # await self.load_exchange(self.chainName, self.exchangeName)
                self.host = (self.host + 1) % self.total_node
                # await asyncio.sleep(10)
                pass

            except TransactionDisallowed as e:
                return None

            except Exception as e:
                self.logger.warning(e)
                # await self.load_exchange(self.chainName, self.exchangeName)
                self.host = (self.host + 1) % self.total_node
                # await asyncio.sleep(10)
                pass

        raise TooManyTriesException(func)

    return wrapper

    # if self.retryCount > 2:

    #     self.retryTx["gas"] = 1.2
    #     self.retryTx["gasPrice"] = 1.2
    #     self.retryTx["maxPriorityFeePerGas"] = "fastest"
    #     self.retryTx["maxFeePerGas"] = "fastest"
