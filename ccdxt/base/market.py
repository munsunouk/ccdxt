import json
from pathlib import Path
import os
from typing import Optional
from ccdxt.base.utils.type import is_str, is_dict
# from ccdxt.base.exchange import Exchange

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
        
        if exchangeName == None :
            return marketDict
            
        market = marketDict[exchangeName]
        
        for key in market['baseChain'][chainName] :
            market[key] = market['baseChain'][chainName][key]
            
        market['baseChain'] = chainName
        
        for key in market :
            
            if is_str(market[key]):
            
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
                result = Market.deep_extend(marketDict)
        else :
            print("marketDictPath doesnt exist")
            return {}
        
        return result
        
    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if is_dict(arg):
                if not is_dict(result):
                    result = {}
                for key in arg:
                    result[key] = Market.deep_extend(result[key] if key in result else None, arg[key])
                    
                    if Path(key).exists() :
                        with open(key, "rt", encoding="utf-8") as f:
                            keyDict = json.load(f)
                            result[key] = keyDict
            else:
                result = arg
        return result