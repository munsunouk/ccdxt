import json
from pathlib import Path
import os
from ..base.utils.type import is_str


class Chain:
    """
    Stores data for a chain.
    """

    def __init__(self):
        self.id: str = None
        self.name: str = None
        self.baseChain: str = None
        self.baseCurrency: str = None
        self.limit: int = None
        self.chainAbi: dict = None
        self.mainnet: str = None
        self.testnet: str = None
        self.privatenet: str = None

    def set_chain(self, chainName: str = "") -> dict:
        """
        Returns data for a chain.

        Parameters:
        --------------
        - chainName (str): name of the chain (optional)

        Returns:
        --------------
        - (dict): data for the chain
        """
        basePath = Path(__file__).resolve().parent.parent
        chainDictPath = os.path.join(basePath, "list", "chain_list.json")
        if Path(chainDictPath).exists():
            with open(chainDictPath, "rt", encoding="utf-8") as f:
                chainDict = json.load(f)
        else:
            print("chainDictPath doesnt exist")
            return {}

        chain = chainDict[chainName]
        for key in chain:
            if is_str(chain[key]):
                key_path = os.path.join(basePath, "contract", "abi", chain[key])
                if Path(key_path).exists():
                    with open(key_path, "rt", encoding="utf-8") as f:
                        keyDict = json.load(f)
                        chain[key] = keyDict
        return chain

    def set_all_chains(self):
        """
        Returns data for all chains

        Returns:
        --------------
        - (dict): data for all chains
        """
        basePath = Path(__file__).resolve().parent.parent
        chainDictPath = os.path.join(basePath, "list", "chain_list.json")
        if Path(chainDictPath).exists():
            with open(chainDictPath, "rt", encoding="utf-8") as f:
                chainDict = json.load(f)
        else:
            print("chainDictPath doesnt exist")
            return {}
        return chainDict
