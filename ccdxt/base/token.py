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
        
        basePath = Path(__file__).resolve().parent.parent
    
        tokenDictPath = os.path.join(basePath, "list", "token_list.json")
        
        if Path(tokenDictPath).exists() :
            with open(tokenDictPath, "rt", encoding="utf-8") as f:
                tokenDict = json.load(f)
        else :
            print("tokenDictPath doesnt exist")
            return {}
        
        for token in tokenDict :
            
            if isinstance(tokenDict[token], dict) :
                
                if isinstance(tokenDict[token]['contract'], dict):
                
                    if chainName in list(tokenDict[token]['contract'].keys()):
                        
                        tokenDict[token]['contract'] = tokenDict[token]['contract'][chainName]

        return tokenDict
