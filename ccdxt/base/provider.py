from web3 import Web3, middleware
from web3.gas_strategies.time_based import construct_time_based_gas_price_strategy
import logging

class Provider(object):

    def __init__(self, value, exp=18):
        self.value = value
        self.exp = exp
        
    def setup_gas_strategy(self, w3, transaction_wait):
        w3.eth.setGasPriceStrategy(
            construct_time_based_gas_price_strategy(transaction_wait)
        )

        w3.middleware_onion.add(middleware.time_based_cache_middleware)
        w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        w3.middleware_onion.add(middleware.simple_cache_middleware)
        
    def public(self, networkPath) :
        
        w3 = Web3(Web3.HTTPProvider(networkPath))
        self.setup_gas_strategy(w3, self.transaction_wait)
        if not w3.isConnected():
            raise ConnectionError("Web3 is not connected")

        logging.getLogger().info(f"Connected to Node {networkPath}")
        logging.getLogger().info(f"Current block is {w3.eth.blockNumber}")
        return w3