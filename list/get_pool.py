from mars.exchange import *
from mars.base import Pool, Token
import sys, inspect
import json
from pathlib import Path
import os
from mars.base.utils.type import is_dict

class LP(object) :
    
    def __init__(self) :
        
        self.swaps = None
        
        self.set_lp_abi()
        
    def set_lp_abi(self) :
        """
        Set the self.lpAbi instance variable to the result of calling the set_lpAbi method of the Pool class.
        """
        
        self.lpAbi = Pool.set_lpAbi()
        
    def save_pools(self,pools) :
        """
        Save the given pools.
        
        Parameters:
            pools (dict): A dictionary containing information about the pool to save.
            
        Returns:
            None
        """
        
        Pool.save_pool(pools)
        
    def get_data(self) :
        """
        Get data about pools of assets on a blockchain.
        
        Parameters:
            None
            
        Returns:
            None
        """
        
        exchanges = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        pool = Pool()
        token = Token()
        
        self.exchanges = []
        
        for x in exchanges :
            
            if x[0] != 'List' :
            
                try :
                    cx = x[1]()
                except TypeError :
                    continue
            
                if 'exchangeName' in dir(cx) :
                    
                    if 'bridge' not in cx.exchangeName :
                        
                        self.exchanges.append(cx)

        default_lp, default_token = {}, {}
        
        for ex_instance in self.exchanges :
            
            factoryAddress = ex_instance.set_checksum(ex_instance.markets['factoryAddress'])

            factoryContract = ex_instance.get_contract(factoryAddress, ex_instance.markets['factoryAbi'])
            
            functions = dir(factoryContract.functions)
            
            if 'allPairsLength' in functions :
                
                default_lp, default_token = self.get_all_pairs(default_lp, default_token,ex_instance)
            
            elif 'getPoolCount' in functions :
                
                default_lp, default_token = self.get_all_pools(default_lp, default_token,ex_instance)
                
        pool.save_pool(default_lp)
        token.save_token(default_token)
            
    def get_all_pools(self,default_lp, default_token,ex_instance) :
        
        factoryAddress = ex_instance.set_checksum(ex_instance.markets['factoryAddress'])
        
        factoryContract = ex_instance.get_contract(factoryAddress, ex_instance.markets['factoryAbi'])
        
        pool_count = factoryContract.functions.getPoolCount().call()
        
        
        default_lp = {}
        default_token = {}
        
        for pId in range(pool_count) :
        # for pId in range(3) :
            
            lp = factoryContract.functions.getPoolAddress(pId).call()
            lpAddress = ex_instance.set_checksum(lp)
            
            lpContract = ex_instance.get_contract(lpAddress, self.lpAbi)
            
            # default_lp = dict(ex_instance.safe_pool())
            
            decimals = lpContract.functions.decimals().call()
            tokenA = lpContract.functions.tokenA().call()
            tokenB = lpContract.functions.tokenB().call()
            
            tokenAaddress = ex_instance.set_checksum(tokenA)
            tokenBaddress = ex_instance.set_checksum(tokenB)
            
            tokenAContract = ex_instance.get_contract(tokenAaddress, ex_instance.chains['chainAbi'])
            tokenBContract = ex_instance.get_contract(tokenBaddress, ex_instance.chains['chainAbi'])
            
            if tokenAaddress == ex_instance.chains["baseContract"] :
                tokenAname = 'KLAY'
                tokenAsymbol = 'KLAY'
                tokenAdecimal = 18
            else :
                tokenAname = tokenAContract.functions.name().call()
                tokenAsymbol = tokenAContract.functions.symbol().call()
                tokenAdecimal = tokenAContract.functions.decimals().call()
                
                if tokenAsymbol.startswith('o') :
                    tokenAsymbol = tokenAsymbol.replace('o', 'k', 1)
                
            if tokenBaddress == ex_instance.chains["baseContract"] :
                tokenBname = 'KLAY'
                tokenBsymbol = 'KLAY'
                tokenBdecimal = 18
                
                if tokenBsymbol.startswith('o') :
                    tokenBsymbol = tokenBsymbol.replace('o', 'k', 1)
                    
            else :
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
                
                f"{tokens_sorted[0]}-{tokens_sorted[1]}" : {
                    
                    "name" : f"{tokens_sorted[0]}-{tokens_sorted[1]}",
                    "baseChain" : {
                        ex_instance.chains['name'] : {
                            ex_instance.exchangeName : lp
                        }
                    },
                    "tokenA" : tokens_sorted[0],
                    "tokenB" : tokens_sorted[1],
                    "decimals" : decimals
                }         
            }
            
            new_tokenA = {
                
                tokens_sorted[0] : {
                    
                    "name" : names_list[0],
                    "symbol" : tokens_sorted[0],
                    "contract" : contracts_list[0],
                    "decimals" : decimals_list[0]
                    
                }
                
            }
            
            new_tokenB = {
                
                tokens_sorted[1] : {
                    "name" : names_list[1],
                    "symbol" : tokens_sorted[1],
                    "contract" : contracts_list[1],
                    "decimals" : decimals_list[1]
                }
                
            }
            
            default_lp.update(new_lp)
            
            default_token.update(new_tokenA)
            default_token.update(new_tokenB)
            
        return default_lp, default_token
            
            # self.save_pools(default_lp)
        
    def get_all_pairs(self,default_lp, default_token, ex_instance) :
        
        factoryAddress = ex_instance.set_checksum(ex_instance.markets['factoryAddress'])
        
        factoryContract = ex_instance.get_contract(factoryAddress, ex_instance.markets['factoryAbi'])
        
        pool_count = factoryContract.functions.allPairsLength().call()
        
        for pId in range(pool_count) :
        # for pId in range(3) :
            
            lp = factoryContract.functions.allPairs(pId).call()
            lpAddress = ex_instance.set_checksum(lp)
            
            lpContract = ex_instance.get_contract(lpAddress, self.lpAbi)
            
            # default_lp = ex_instance.safe_pool()
            # default_token = ex_instance.safe_token()
            
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
                
                f"{tokens_sorted[0]}-{tokens_sorted[1]}" : {
                    
                    "name" : f"{tokens_sorted[0]}-{tokens_sorted[1]}",
                    "baseChain" : {
                        ex_instance.chains['name'] : {
                            ex_instance.exchangeName : lp
                        }
                    },
                    "tokenA" : tokens_sorted[0],
                    "tokenB" : tokens_sorted[1],
                    "decimals" : decimals
                }         
            }
            
            new_tokenA = {
                
                tokens_sorted[0] : {
                    
                    "name" : names_list[0],
                    "symbol" : tokens_sorted[0],
                    "contract" : contracts_list[0],
                    "decimals" : decimals_list[0]
                    
                }
                
            }
            
            new_tokenB = {
                
                tokens_sorted[1] : {
                    "name" : names_list[1],
                    "symbol" : tokens_sorted[1],
                    "contract" : contracts_list[1],
                    "decimals" : decimals_list[1]
                }
                
            }
            
            default_lp.update(new_lp)
            
            default_token.update(new_tokenA)
            default_token.update(new_tokenB)
            
            # self.save_pools(default_lp)
        return default_lp, default_token
            