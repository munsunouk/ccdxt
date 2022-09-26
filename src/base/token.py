import json
from pathlib import Path
import os

class Token(object) :

    def __init__(self) :

        self.name = None
        self.symbol = None
        self.contract = None
        self.detail = None
        
    def set_token(self, chainName : str = '', exchangeName : str = '') -> dict :
        '''
        get balance of token in wallet
        
        Parameters
        ----------
        chainName: chain name e.g)'klaytn'
        exchangeName : exchange name e.g)'klayswap'
        
        Returns
        -------
        "oUSDT" : {
            "id" : 2,
            "name" : "Orbit Bridge Klaytn USD Tether",
            "symbol" : "oUSDT",
            "contract" : {
                "klaytn" : "0xcee8faf64bb97a73bb51e115aa89c17ffa8dd167",
                "polygon" : "0x957da9EbbCdC97DC4a8C274dD762EC2aB665E15F"
            },
            "decimal" : 6,
            "detail" : None,
            "info" : "https://bridge.orbitchain.io/"
        }
        '''
        
        basePath = 'src'
    
        marketDictPath = os.path.join(basePath , "list", "market_list.json")
        
        if Path(marketDictPath).exists() :
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
        else :
            print("marketDictPath doesnt exist")
            return {}
    
        tokenDictPath = os.path.join(basePath, "list", "token_list.json")
        
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
                exchangeToken[token]["contract"] = exchangeToken[token]["contract"][chainName]

        return exchangeToken
