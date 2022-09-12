import json
from pathlib import Path

class Pool(object) :

    def __init__(self) :

        self.id = None
        self.name = None
        self.symbol = None
        self.contract = None
        self.decimal = None
        self.exchange = None
        
    def set_pool(self) -> dict :
        
        if self.exchangeName in self._cache:
            return self._cache[self.exchangeName]
        
        basePath = 'src/chain'
    
        poolListPath = basePath / self.chainName / "contract" / "pool_list.json"
        
        if Path(poolListPath).exists() :
            with open(poolListPath, "rt", encoding="utf-8") as f:
                poolList = json.load(f)
        else :
            print("poolList doesnt exist")
            
        self._cache[self.exchangeName] = poolList
        
        return self._cache[self.exchangeName]