import json
from pathlib import Path
import os
from mars.base.utils.type import is_dict
from typing import Dict

class Pool:
    """
    Stores data for a pool.
    """
    def __init__(self):
        
        {}
        
    @staticmethod
    def set_lpAbi() -> Dict:
        """
        Returns data for lpAbi.
        
        Returns:
        --------------
        - (Dict): data for lpAbi
        """
        
        basePath = Path(__file__).resolve().parent.parent
        
        lpAbi_path = os.path.join(basePath , "contract", "abi", 'lpABI.json')
        
        if Path(lpAbi_path).exists() :
            with open(lpAbi_path, "rt", encoding="utf-8") as f:
                lpAbi = json.load(f)
        
        return lpAbi
        
    def set_pool(self, chainName : str = '', exchangeName : str = None, passing = None) -> Dict :
        
        """
        Returns data for a pool.
        
        Parameters:
        - chainName (str): name of the chain (optional)
        - exchangeName (str): name of the exchange (optional)
        
        Returns:
        --------------
        - (Dict): data for the pool
        """
        
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
        
        if (exchangeName == None) or (passing) :
            
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
        """
        Returns data for all pools.
        
        Returns:
        --------------
        - (dict): data for all pools
        """
        
        basePath = Path(__file__).resolve().parent.parent
    
        poolDictPath = os.path.join(basePath , "list", "pool_list.json")
        
        if Path(poolDictPath).exists() :
            with open(poolDictPath, "rt", encoding="utf-8") as f:
                poolDict = json.load(f)
        else :
            print("poolDictPath doesnt exist")
            return {}
        
        return poolDict
    
    def save_pool(self, pools) :
        
        basePath = Path(__file__).resolve().parent.parent
    
        poolDictPath = os.path.join(basePath , "list", "pool_list.json")
        
        cur_pool_dict = self.set_all_pools()
        new_pool_dict = pools
        
        future_pool_dict = self.deep_extend(cur_pool_dict, new_pool_dict)
        
        if Path(poolDictPath).exists() :
            with open(poolDictPath, 'w', encoding="utf-8") as f:     
                json.dump(future_pool_dict, f, indent=4)
                
        else :
            print("poolDictPath doesnt exist")
            
    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if is_dict(arg):
                if not is_dict(result):
                    result = {}
                for key in arg:
                    result[key] = Pool.deep_extend(
                        result[key] if key in result else None, arg[key]
                    )
            else:
                result = arg
        return result