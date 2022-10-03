from ccdxt.exchange import *
from ccdxt.base.pool import Pool
import sys, inspect
import json
from pathlib import Path
import os

class List(object) :
    
    def __init__(self) :
        
        self.swaps = None
        
        self.set_lp_abi()
        
    def set_lp_abi(self) :
        
        self.lpAbi = Pool.set_lpAbi()
        
    def save_pools(self,pools) :
        
        Pool.save_pool(pools)
        
    def get_data(self) :
        
        exchanges = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        self.exchanges = [x for x in exchanges if x[0] != 'List']

        for exchange in self.exchanges :
            
            ex_instance = exchange[1]()
            
            factoryAddress = ex_instance.set_checksum(ex_instance.markets['factoryAddress'])

            factoryContract = ex_instance.get_contract(factoryAddress, ex_instance.markets['factoryAbi'])
            
            functions = dir(factoryContract.functions)
            
            if 'allPairsLength' in functions :
                
                self.get_all_pairs(ex_instance)
            
            elif 'getPoolCount' in functions :
                
                self.get_all_pools(ex_instance)
            
    def get_all_pools(self,ex_instance) :
        
        factoryAddress = ex_instance.set_checksum(ex_instance.markets['factoryAddress'])
        
        factoryContract = ex_instance.get_contract(factoryAddress, ex_instance.markets['factoryAbi'])
        
        pool_count = factoryContract.functions.getPoolCount().call()
        
        for pId in range(pool_count) :
            
            lp = factoryContract.functions.getPoolAddress(pId).call()
            lpAddress = ex_instance.set_checksum(lp)
            
            lpContract = ex_instance.get_contract(lpAddress, self.lpAbi)
            
            default_lp = dict(ex_instance.safe_pool())
            
            decimals = lpContract.functions.decimals().call()
            tokenA = lpContract.functions.tokenA().call()
            tokenB = lpContract.functions.tokenB().call()
            
            tokenAaddress = ex_instance.set_checksum(tokenA)
            tokenBaddress = ex_instance.set_checksum(tokenB)
            
            tokenAContract = ex_instance.get_contract(tokenAaddress, ex_instance.chains['chainAbi'])
            tokenBContract = ex_instance.get_contract(tokenBaddress, ex_instance.chains['chainAbi'])
        
            tokenAsymbol = tokenAContract.functions.symbol().call()
            tokenBsymbol = tokenBContract.functions.symbol().call()
            tokens = sorted([tokenAsymbol,tokenBsymbol])
            
            new_lp = {
                
                "name" : f"{tokens[0]}-{tokens[1]}",
                "baseChain" : ex_instance.chains['baseChain'],
                "poolAddress" : {
                    ex_instance.markets["name"] : lp
                    },
                "tokenA" : tokens[0],
                "tokenB" : tokens[1],
                "decimals" : decimals
                
            }
            
            default_lp.update(new_lp)
            
            self.save_pools(default_lp)
        
    def get_all_pairs(self,ex_instance) :
        
        factoryAddress = ex_instance.set_checksum(ex_instance.markets['factoryAddress'])
        
        factoryContract = ex_instance.get_contract(factoryAddress, ex_instance.markets['factoryAbi'])
        
        pool_count = factoryContract.functions.allPairsLength().call()
        
        for pId in range(pool_count) :
            
            lp = factoryContract.functions.allPairs(pId).call()
            lpAddress = ex_instance.set_checksum(lp)
            
            lpContract = ex_instance.get_contract(lpAddress, self.lpAbi)
            
            default_lp = ex_instance.safe_pool()
            default_token = ex_instance.safe_token()
            
            decimals = lpContract.functions.decimals().call()
            tokenA = lpContract.functions.token0().call()
            tokenB = lpContract.functions.token1().call()
            
            tokenAaddress = ex_instance.set_checksum(tokenA)
            tokenBaddress = ex_instance.set_checksum(tokenB)
            
            tokenAContract = ex_instance.get_contract(tokenAaddress, ex_instance.chains['chainAbi'])
            tokenBContract = ex_instance.get_contract(tokenBaddress, ex_instance.chains['chainAbi'])
        
            tokenAname = tokenAContract.functions.name().call()
            tokenAsymbol = tokenAContract.functions.symbol().call()
            tokenAdecimal = tokenAContract.functions.decimals().call()
            
            tokenBname = tokenBContract.functions.name().call()
            tokenBsymbol = tokenBContract.functions.symbol().call()
            tokenBdecimal = tokenBContract.functions.decimals().call()
            
            tokens_list = [tokenAsymbol,tokenBsymbol]
            names_list = [tokenAname,tokenBname]
            contracts_list = [tokenA,tokenB]
            decimals_list = [tokenAdecimal, tokenBdecimal]
            
            tokens_sorted = sorted(tokens_list)
            
            if tokens_list[0] != tokens_sorted[0] :
                
                names_list[0],names_list[1] = names_list[1],names_list[0]
                contracts_list[0],contracts_list[1] = contracts_list[1],contracts_list[0]
                decimals_list[0],decimals_list[1] = decimals_list[1],decimals_list[0]
            
            new_lp = {
                
                "name" : f"{tokens_sorted[0]}-{tokens_sorted[1]}",
                "baseChain" : ex_instance.chains['baseChain'],
                "poolAddress" : {
                    ex_instance.markets["name"] : lp
                    },
                "tokenA" : tokens_sorted[0],
                "tokenB" : tokens_sorted[1],
                "decimals" : decimals
                
            }
            
            new_tokenA = {
                
                "name" : names_list[0],
                "symbol" : tokens_sorted[0],
                "contract" : contracts_list[0],
                "decimals" : decimals_list[0]
                
            }
            
            new_tokenB = {
                
                "name" : names_list[1],
                "symbol" : tokens_sorted[1],
                "contract" : contracts_list[1],
                "decimals" : decimals_list[1]
                
            }
            
            default_lp.update(new_lp)
            
            tokenA_info = default_token.update(new_tokenA)
            tokenB_info = default_token.update(new_tokenB)
            
            print(tokenA_info)
            print(tokenB_info)
            
            self.save_pools(default_lp)
            