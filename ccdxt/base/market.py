import json
from pathlib import Path
import os
from typing import Optional

class Market(object):

    def __init__(self) :
        self.id = None
        self.name = None
        self.symbol = None
        self.baseChain = None
        self.baseCurrency = None
        self.fee = None
        self.factoryAbi = None
        self.factoryAddress = None
        self.routerAbi = None
        self.routerAddress = None
        self.info = None
        
    def set_market(self, chainName : str = None, exchangeName : Optional[str] = None) -> dict :

        basePath = Path(__file__).resolve().parent.parent
    
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
        
        for key in market :
            
            if isinstance(market[key], str):
            
                key_path = os.path.join(basePath , "contract", "abi", market[key])
                
                if Path(key_path).exists() :
                    with open(key_path, "rt", encoding="utf-8") as f:
                        keyDict = json.load(f)
                        market[key] = keyDict
        
        return market
    
    def set_all_markets(self) :
        
        basePath = Path(__file__).resolve().parent.parent
    
        marketDictPath = os.path.join(basePath , "list", "market_list.json")
        
        if Path(marketDictPath).exists() :
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
        else :
            print("marketDictPath doesnt exist")
            return {}
        
        return marketDict