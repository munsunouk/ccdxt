import json
from pathlib import Path
import os
from ccdxt.base.utils.type import is_str

class Chain(object):

    def __init__(self) :

        self.id = None
        self.name = None
        self.baseChain = None
        self.baseCurrency = None
        self.limit = None
        self.chainAbi = None
        self.mainnet = None
        self.testnet = None
        self.privatenet = None
        
    def set_chain(self, chainName : str = '') -> dict : 
        
        basePath = Path(__file__).resolve().parent.parent
        
        chainDictPath = os.path.join(basePath, "list", "chain_list.json")
        
        if Path(chainDictPath).exists() :
            with open(chainDictPath, "rt", encoding="utf-8") as f:
                chainDict = json.load(f)
        else :
            print("chainDictPath doesnt exist")
            return {}
        
        chain = chainDict[chainName]
        
        for key in chain :
            
            if is_str(chain[key]):
            
                key_path = os.path.join(basePath, "contract", "abi", chain[key])
                
                if Path(key_path).exists() :
                    with open(key_path, "rt", encoding="utf-8") as f:
                        keyDict = json.load(f)
                        chain[key] = keyDict
        
        return chain
    
    def set_all_chains(self) :
        
        basePath = Path(__file__).resolve().parent.parent
        
        chainDictPath = os.path.join(basePath, "list", "chain_list.json")
        
        if Path(chainDictPath).exists() :
            with open(chainDictPath, "rt", encoding="utf-8") as f:
                chainDict = json.load(f)
        else :
            print("chainDictPath doesnt exist")
            return {}
        
        return chainDict
        
        
        
        