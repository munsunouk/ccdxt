import json
from pathlib import Path
import os

class Token(object) :

    def __init__(self) :

        self.id = None
        self.name = None
        self.symbol = None
        self.contract = None
        self.decimal = None
        self.info = None
        
    def set_token(self, chainName : str = '', exchangeName : str = '') -> dict :
        '''
        get balance of token in wallet
        
        Parameters
        ----------
        chainName: chain name e.g)'klaytn'
        exchangeName : exchange name e.g)'klayswap'
        
        Returns
        -------
        {
            "MOOI" : {
                "id" : 1,
                "name" : "MOOI",
                "symbol" : "MOOI",
                "contract" : "0x4b734a4d5bf19d89456ab975dfb75f02762dda1d",
                "decimal" : 18,
                "info" : false
            },
            "oUSDT" : {
                "id" : 2,
                "name" : "Orbit Bridge Klaytn USD Tether",
                "symbol" : "oUSDT",
                "contract" : "0xcee8faf64bb97a73bb51e115aa89c17ffa8dd167",
                "decimal" : 6,
                "info" : "https://bridge.orbitchain.io/"
            }
        }
        '''
        
        basePath = 'src/chain'
        
        marketDictPath = os.path.join(basePath , chainName , "contract" , "market_list.json")
        
        if Path(marketDictPath).exists() :
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
        else :
            print("marketDictPath doesnt exist")
            return {}
    
        tokenDictPath = os.path.join(basePath , chainName , "contract" , "token_list.json")
        
        if Path(tokenDictPath).exists() :
            with open(tokenDictPath, "rt", encoding="utf-8") as f:
                tokenDict = json.load(f)
        else :
            print("tokenDictPath doesnt exist")
            return {}
        
        market = marketDict[exchangeName]

        tokenAvailable = market["symbols"]
        
        exchangeToken = {}
        
        for token in tokenAvailable :
            
            if isinstance(tokenDict[token], dict) :
                
                exchangeToken[token] = tokenDict[token]
            
        return exchangeToken
