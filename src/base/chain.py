import json
from pathlib import Path
import os

class Chain(object):

    def __init__(self) :

        self.id = None
        self.name = None
        self.baseCurrency = None
        self.limit = None
        self.chainAbi = None
        self.mainnet = None
        self.testnet = None
        self.privatenet = None
        
    def set_chain(self, chainName : str = '') -> dict : 

        basePath = 'src/chain'
    
        chainDictPath = os.path.join(basePath , chainName , "contract" , "chain_info.json")
        
        if Path(chainDictPath).exists() :
            with open(chainDictPath, "rt", encoding="utf-8") as f:
                chain = json.load(f)
        else :
            print("chainDictPath doesnt exist")
            return {}
        
        for key in chain :
            
            if isinstance(chain[key], str):
            
                key_path = os.path.join(basePath , chainName , "contract" , "abi", chain[key])
                
                if Path(key_path).exists() :
                    with open(key_path, "rt", encoding="utf-8") as f:
                        keyDict = json.load(f)
                        chain[key] = keyDict
        
        return chain
        
        
        
        