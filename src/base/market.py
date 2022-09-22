import json
from pathlib import Path
import os

class Market(object):

    def __init__(self) :
        self.id = None
        self.name = None
        self.symbol = None
        self.baeChain = None
        self.baseCurrency = None
        self.fee = None
        self.factoryAbi = None
        self.factoryAddress = None
        self.routerAbi = None
        self.routerAddress = None
        self.pairAbi = None
        self.info = None
        self.symbols = []
        self.pools = []
        
    def set_market(self, chainName : str = '', exchangeName : str = '') -> dict :

        basePath = 'src'
    
        marketDictPath = os.path.join(basePath , "list", "market_list.json")
        
        if Path(marketDictPath).exists() :
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
        else :
            print("marketDictPath doesnt exist")
            return {}
            
        market = marketDict[exchangeName]
        
        for key in market['baseChain'][chainName] :
            market[key] = market['baseChain'][chainName][key]
        market['baseChain'] = chainName
        market["contract"] = market["contract"][chainName]
        
        for key in market :
            
            if isinstance(market[key], str):
            
                key_path = os.path.join(basePath , "contract", "abi", market[key])
                
                if Path(key_path).exists() :
                    with open(key_path, "rt", encoding="utf-8") as f:
                        keyDict = json.load(f)
                        market[key] = keyDict
        
        return market