from ..crawler.wallet import Metamask
from typing import Optional
from ..crawler.exchange.crawling import Crawling
from ..base import Exchange
from ..base.utils.retry import retry
import asyncio


class Liamaswap(Crawling, Exchange):
    def __init__(self, config_change: Optional[dict] = {}) -> None:
        super().__init__()

        config = {
            "chainName": "MATIC",
            "exchangeName": "liamaswap",
            "retries": 3,
            "retriesTime": 10,
            "host": None,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
            "wallet_name": "Metamask",
            "wallet_config": {},
            "driver_path": None,
        }

        config.update(config_change)

        # market info
        self.id = 13
        self.chainName = config["chainName"]
        self.exchangeName = config["exchangeName"]
        self.duration = False
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.proxy = config["proxy"]
        self.wallet_name = config["wallet_name"]
        self.wallet_config = config["wallet_config"]
        self.driver_path = config["driver_path"]

        self.load_exchange(self.chainName, self.exchangeName)

        self.set_logger(self.log)
        self.load_crawling()

        # site_config = self.set_site_config(self.chains['baseChain'], tokenA, tokenB)

    # @retry
    async def fetch_ticker(self, amountAin, tokenAsymbol, tokenBsymbol, **kwargs):
        best_route = None

        amountIn = amountAin

        tokenA = self.tokens[tokenAsymbol]
        tokenB = self.tokens[tokenBsymbol]

        tokenAaddress = tokenA["contract"]
        tokenBaddress = tokenB["contract"]

        site_config = self.set_site_config(self.chains["baseChain"], tokenAaddress, tokenBaddress)
        self.set_site(site_config)
        self.click_liama_hide_ip()
        self.input_liama_size(amountAin)

        self.click_liama_perform_reload()

        route_lists = self.click_liama_perform_route()

        route_lists = list(map(lambda x: x[-1].lower(), route_lists))

        self.load_markets(self.chainName, None)

        for route_list in route_lists:
            if route_list in self.markets:
                best_route = route_list

        return best_route

    def set_site_config(self, chain, tokenA, tokenB):
        site_config1 = {"chain": chain}

        site_config2 = {"from": tokenA, "to": tokenB}

        site_config = [("?", site_config1), ("&", site_config2)]

        return site_config
