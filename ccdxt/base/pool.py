import json
from pathlib import Path
import os
from ccdxt.base.utils.type import is_dict
from typing import Optional
class Pool(object):

    def __init__(self) :

        self.id = None
        self.name = None
        self.baseChain = None
        self.poolAddress = {}
        self.chainAbi = None
        self.tokenA = None
        self.tokenB = None
        self.decimals = None
        
    def set_lpAbi() :
        
        basePath = Path(__file__).resolve().parent.parent
        
        lpAbi_path = os.path.join(basePath , "contract", "abi", 'lpABI.json')
        
        if Path(lpAbi_path).exists() :
            with open(lpAbi_path, "rt", encoding="utf-8") as f:
                lpAbi = json.load(f)
        
        return lpAbi
        
    def set_pool(self, chainName : str = '', exchangeName : Optional[str] = None) -> dict :
        
        pass_list = ['orbitbridge', 'swapscanner']
        
        basePath = Path(__file__).resolve().parent.parent
        
        poolDictPath = os.path.join(basePath, "list", "pool_list.json")
        
        if Path(poolDictPath).exists() :
            with open(poolDictPath, "rt", encoding="utf-8") as f:
                poolDict = json.load(f)
        else :
            print("poolDictPath doesnt exist")
            return {}
        
        if exchangeName == None :
            return poolDict
        
        pool_involve = {}
        
        if (exchangeName == None) or (exchangeName in pass_list) :
            
            return poolDict
        
        for pool in poolDict :
            
            if is_dict(poolDict[pool]) :
                
                if chainName in list(poolDict[pool]['baseChain'].keys()):
                
                    if exchangeName in list(poolDict[pool]['baseChain'][chainName].keys()):
                        
                        pool_involve[pool] = poolDict[pool]
                        
                        pool_involve[pool]['poolAddress'] = poolDict[pool]['baseChain'][chainName][exchangeName]
                        pool_involve[pool]['baseChain'] = chainName

        return pool_involve
    
    def set_all_pools(self) :
        
        basePath = Path(__file__).resolve().parent.parent
    
        poolDictPath = os.path.join(basePath , "list", "pool_list.json")
        
        if Path(poolDictPath).exists() :
            with open(poolDictPath, "rt", encoding="utf-8") as f:
                poolDict = json.load(f)
        else :
            print("poolDictPath doesnt exist")
            return {}
        
        return poolDict
    
    # def save_pool(self, pools) :
        
    #     basePath = Path(__file__).resolve().parent.parent
    
    #     poolDictPath = os.path.join(basePath , "list", "pool_list.json")
        
    #     if Path(poolDictPath).exists() :
    #         with open(poolDictPath, 'w', encoding="utf-8") as f:     
    #             json.dump(pools, f, indent=4)
                
    #     else :
    #         print("poolDictPath doesnt exist")