from errors import ExchangeError
from errors import NetworkError
from errors import NotSupported
from errors import AuthenticationError
from errors import DDoSProtection
from errors import RequestTimeout
from errors import ExchangeNotAvailable
from errors import InvalidAddress
from errors import InvalidOrder
from errors import ArgumentsRequired
from errors import BadSymbol
from errors import NullResponse
from errors import RateLimitExceeded

class Chain(object):
    
    def __init__(self, config={}):
        
        self.headers = dict() if self.headers is None else self.headers
         
        if self.markets :
            self.set_markets(self.markets)
            
    def set_markets(self, markets, currencies=None):
        
        values = []
        marketValues = self.to_array(markets)
        for i in range(0, len(marketValues)):
            market = self.deep_extend(self.safe_market(), marketValues[i])
            values.append(market)
        self.markets = self.index_by(values, 'symbol')
        self.markets_by_id = self.index_by(markets, 'id')
        
    def safe_market(self, marketId=None, marketSymbol=None, delimiter=None):
        result = {
            'id': marketId,
            'symbol': marketId,
            'baseCurrency' : None,
            'factoryAbi' : None,
            'factoryAddress' : None,
            'routerAbi' : None,
            'routerAddress' : None, 

        }
        
    def set_currencies(self,)