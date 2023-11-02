import json
from pathlib import Path
import os
import itertools
from ccdxt.base.utils.type import is_dict


class Token(object):
    def __init__(self):
        {}

    def set_token(self, chainName, exchangeName, baseCurrency, passing) -> dict:
        """
        Get token information for a specific exchange and chain.

        Parameters
        ----------
        chainName: str
            Chain name, e.g. 'klaytn'.
        exchangeName: str
            Exchange name, e.g. 'klayswap'.

        Returns
        -------
        dict
            Token information. Example:
            {
                "oUSDT": {
                    "id": 2,
                    "name": "Orbit Bridge Klaytn USD Tether",
                    "symbol": "oUSDT",
                    "contract": {
                        "klaytn": "0xcee8faf64bb97a73bb51e115aa89c17ffa8dd167",
                        "polygon": "0x957da9EbbCdC97DC4a8C274dD762EC2aB665E15F"
                    },
                    "decimal": 6,
                    "detail": None,
                    "info": "https://bridge.orbitchain.io/"
                }
            }
        """

        basePath = Path(__file__).resolve().parent.parent

        tokenDictPath = os.path.join(basePath, "list", "token_list.json")

        if Path(tokenDictPath).exists():
            with open(tokenDictPath, "rt", encoding="utf-8") as f:
                tokenDict = json.load(f)
        else:
            print("tokenDictPath doesnt exist")
            return {}

        poolDictPath = os.path.join(basePath, "list", "pool_list.json")

        if Path(poolDictPath).exists():
            with open(poolDictPath, "rt", encoding="utf-8") as f:
                poolDict = json.load(f)
        else:
            print("poolDictPath doesnt exist")
            return {}

        if exchangeName == None:
            return tokenDict

        pool_involve = {}

        if (exchangeName == None) or (passing):
            return tokenDict

        for pool in poolDict:
            if is_dict(poolDict[pool]):
                if chainName in list(poolDict[pool]["baseChain"].keys()):
                    if exchangeName in list(poolDict[pool]["baseChain"][chainName].keys()):
                        pool_involve[pool] = poolDict[pool]

                        pool_involve[pool]["poolAddress"] = poolDict[pool]["baseChain"][chainName][
                            exchangeName
                        ]
                        pool_involve[pool]["baseChain"] = chainName

        all_pools = pool_involve.keys()
        result = list(map(lambda x: x.split("-"), all_pools))
        token_list = list(set(list(itertools.chain.from_iterable(result))))

        token_involve = {}

        token_involve[baseCurrency] = tokenDict[baseCurrency]

        for token in token_list:
            token_involve[token] = tokenDict[token]

        return token_involve

    def set_all_tokens(self) -> dict:
        """
        Returns data for all tokens.

        Returns:
        --------------
        - (dict): data for all tokens
        """

        basePath = Path(__file__).resolve().parent.parent

        tokenDictPath = os.path.join(basePath, "list", "token_list.json")

        if Path(tokenDictPath).exists():
            with open(tokenDictPath, "rt", encoding="utf-8") as f:
                tokenDict = json.load(f)
        else:
            print("tokenDictPath doesnt exist")
            return {}

        return tokenDict

    def save_token(self, tokens):
        basePath = Path(__file__).resolve().parent.parent

        tokenDictPath = os.path.join(basePath, "list", "token_list.json")

        cur_token_dict = self.set_all_tokens()
        new_token_dict = tokens

        future_token_dict = self.deep_extend(cur_token_dict, new_token_dict)

        if Path(tokenDictPath).exists():
            with open(tokenDictPath, "w", encoding="utf-8") as f:
                json.dump(future_token_dict, f, indent=4)

        else:
            print("tokenDictPath doesnt exist")

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if is_dict(arg):
                if not is_dict(result):
                    result = {}
                for key in arg:
                    result[key] = Token.deep_extend(
                        result[key] if key in result else None, arg[key]
                    )
            else:
                result = arg
        return result
