import json
from pathlib import Path
from typing import Optional, Type, Union

from eth_typing import HexAddress
from web3 import Web3
from web3.contract import Contract

import sys, os

class Abi :

    def __init__(self, chainName : str, exchangeName : str) : 

        super().__init__()
        self._cache = {}
        self.chainName = chainName
        self.exchangeName = exchangeName

    def set_abi(self) -> dict:
        """Reads a embedded ABI file and returns it.
        Example::
            abi = get_abi_by_filename("ERC20Mock.json")
        You are most likely interested in the keys `abi` and `bytecode` of the JSON file.
        Loaded ABI files are cache in in-process memory to speed up future loading.
        :param web3: Web3 instance
        :param fname: `JSON filename from supported contract lists <https://github.com/tradingstrategy-ai/web3-ethereum-defi/tree/master/eth_defi/abi>`_.
        :return: Full contract interface, including `bytecode`.
        """

        if self.exchangeName in self._cache:
            return self._cache[self.exchangeName]
        
        basePath = 'src/chain'

        chainInfoPath = basePath / self.chainName / "contract" / "chain_info.json"
        marketListPath = basePath / self.chainName / "contract" / "market_list.json"
        
        if Path(chainInfoPath).exists() :
            with open(chainInfoPath, "rt", encoding="utf-8") as f:
                chainInfoAbi = json.load(f)
        else :
            print("chainInfoPath doesnt exist")
            
        if Path(marketListPath).exists() :
            with open(marketListPath, "rt", encoding="utf-8") as f:
                marketListAbi = json.load(f)
        else :
            print("marketListPath doesnt exist")
        
        marketListAbi = marketListAbi[self.exchangeName]
        self._cache[self.exchangeName] = {
            
            "chainInfoAbi" : chainInfoAbi,
            "marketListAbi" : marketListAbi
            
        }

        return self._cache[self.exchangeName]
