import json
from pathlib import Path
import os
from typing import Optional, Dict
from ccdxt.base.utils.type import is_str, is_dict, is_list


class Market:
    def __init__(self):
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.symbol: Optional[str] = None
        self.baseChain: Optional[str] = None
        self.baseCurrency: Optional[str] = None
        self.fee: Optional[float] = None
        self.factoryAbi: Optional[Dict] = None
        self.factoryAddress: Optional[str] = None
        self.routerAbi: Optional[Dict] = None
        self.routerAddress: Optional[str] = None
        self.info: Optional[Dict] = None
        self.pool_pass = True
        self.token_pass = True

    def set_market(self, chainName: str = None, exchangeName: Optional[str] = None) -> dict:
        basePath = Path(__file__).resolve().parent.parent

        marketDictPath = os.path.join(basePath, "list", "market_list.json")

        if Path(marketDictPath).exists():
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
        else:
            print("marketDictPath doesnt exist")
            return {}

        if exchangeName == None:
            return {}

        market = marketDict[exchangeName]

        for key in market["baseChain"][chainName]:
            market[key] = market["baseChain"][chainName][key]

        market["baseChain"] = chainName

        result = Market.deep_extend(market)

        return result

    def set_all_markets(self, exchangeName):
        basePath = Path(__file__).resolve().parent.parent

        marketDictPath = os.path.join(basePath, "list", "market_list.json")

        if Path(marketDictPath).exists():
            with open(marketDictPath, "rt", encoding="utf-8") as f:
                marketDict = json.load(f)
                market = marketDict[exchangeName]
                result = Market.deep_extend(market)
        else:
            print("marketDictPath doesnt exist")
            return {}

        return result

    @staticmethod
    def deep_extend(*args):
        result = None
        basePath = Path(__file__).resolve().parent.parent
        for arg in args:
            if is_dict(arg):
                if not is_dict(result):
                    result = {}
                for key in arg:
                    result[key] = Market.deep_extend(
                        result[key] if key in result else None, arg[key]
                    )

                    if is_str(result[key]):
                        key_path = os.path.join(basePath, "contract", "abi", result[key])

                        if Path(key_path).exists():
                            with open(key_path, "rt", encoding="utf-8") as f:
                                keyDict = json.load(f)
                                result[key] = keyDict

                    elif is_list(result[key]):
                        keyLists = []

                        for num in result[key]:
                            key_path = os.path.join(basePath, "contract", "abi", num)

                            if Path(key_path).exists():
                                with open(key_path, "rt", encoding="utf-8") as f:
                                    keyList = json.load(f)
                                    keyLists.append(keyList)

                            else:
                                keyLists.append(num)

                        result[key] = keyLists

            else:
                result = arg
        return result
