import json
from pathlib import Path
from typing import Optional, Type, Union

from eth_typing import HexAddress
from web3 import Web3
from web3.contract import Contract

import sys, os

class Abi :

    def __init__(self) : 
        self.factoryAbi = None
        self.factoryAddress = None
        self.routerAbi = None
        self.routerAddress = None

    def set_abi(self, chainName : str = '', exchangeName : str = '') -> dict:
        """Reads a embedded ABI file and returns it.
        Example::
            abi = get_abi_by_filename("ERC20Mock.json")
        You are most likely interested in the keys `abi` and `bytecode` of the JSON file.
        Loaded ABI files are cache in in-process memory to speed up future loading.
        :param web3: Web3 instance
        :param fname: `JSON filename from supported contract lists <https://github.com/tradingstrategy-ai/web3-ethereum-defi/tree/master/eth_defi/abi>`_.
        :return: Full contract interface, including `bytecode`.
        """
        
        basePath = 'src/chain'

        chainInfoPath = os.path.join(basePath , chainName , "contract" , "chain_info.json")
        marketDictPath = os.path.join(basePath , chainName , "contract" , "market_list.json")
        
        if Path(chainInfoPath).exists() :
            with open(chainInfoPath, "rt", encoding="utf-8") as f:
                chainInfoAbi = json.load(f)
        else :
            print("chainInfoPath doesnt exist")
            
        if Path(marketDictPath).exists() :
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
        else :
            print("marketDictPath doesnt exist")
        
        market = marketDict[exchangeName]
        
        # print(Abi().__dir__)
        
        
        result = {}
        # result = {
        #     "chainInfoAbi" : chainInfoAbi,
        #     "marketDictAbi" : marketDictAbi            
        # }

        return result
    

# Abi().set_abi()
