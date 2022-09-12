import json
from pathlib import Path

class Token(object) :

    def __init__(self, chainName : str, exchangeName : str) :

        self.id = None
        self.name = None
        self.symbol = None
        self.contract = None
        self.decimal = None
        self.info = None
        
    def set_token_list(self) -> dict :
        
        if self.exchangeName in self._cache:
            return self._cache[self.exchangeName]
        
        basePath = 'src/chain'
    
        tokenDictPath = basePath / self.chainName / "contract" / "token_list.json"
        
        if Path(tokenDictPath).exists() :
            with open(tokenDictPath, "rt", encoding="utf-8") as f:
                tokenDict = json.load(f)
        else :
            print("tokenDictPath doesnt exist")
            
        self._cache[self.exchangeName] = tokenDict
        
        return self._cache[self.exchangeName]
