#this app for rebalancing between Klaytn <-> Mexc

import asyncio
import argparse
import sys
from pathlib import Path
import logging

basePath = Path(__file__).resolve().parent.parent
sys.path.append(str(basePath))

from mars.lib.klay_mexc import Rebalance

parser = argparse.ArgumentParser(description="Argparse for Rebalance")

#parameters for class
parser.add_argument("--klay_account", type=str, default=None)
parser.add_argument("--klay_privateKey", type=str, default=None)

parser.add_argument("--eth_account", type=str, default=None)
parser.add_argument("--eth_privateKey", type=str, default=None)

parser.add_argument("--mooi_account", type=str, default=None)
parser.add_argument("--mooi_privateKey", type=str, default=None)

parser.add_argument("--mexc_mooi_account", type=str, default=None)
parser.add_argument("--mexc_klay_account", type=str, default=None)
parser.add_argument("--mexc_eth_account", type=str, default=None)

parser.add_argument("--mexc_account", type=str, default=None)
parser.add_argument("--mexc_privateKey", type=str, default=None)


# parameters for function
parser.add_argument("--amount", type=float, default=0.0)
parser.add_argument("--from_tokenSymbol", type=str, default='kUSDT')
parser.add_argument("--to_tokenSymbol", type=str, default='USDT')
parser.add_argument("--fromChain", type=str, default='KLAYTN')
parser.add_argument("--toChain", type=str, default='MEXC')
parser.add_argument("--middle_chain", type=str, default=None)
parser.add_argument("--endurable_gasFee", type=float, default=1.0)




if __name__ == "__main__":
    
    config = {
        "klay_account": parser.parse_args().klay_account,
        "klay_privateKey": parser.parse_args().klay_privateKey,
        
        "eth_account" : parser.parse_args().eth_account,
        "eth_privateKey" : parser.parse_args().eth_privateKey,
        
        "mooi_account" : parser.parse_args().mooi_account,
        "mooi_privateKey" : parser.parse_args().mooi_privateKey,
        
        "mexc_mooi_account" : parser.parse_args().mexc_mooi_account,
        "mexc_klay_account" : parser.parse_args().mexc_klay_account,
        "mexc_eth_account" : parser.parse_args().mexc_eth_account,
        
        "mexc_account" : parser.parse_args().mexc_account,
        "mexc_privateKey" : parser.parse_args().mexc_privateKey,
        
        "endurable_gasFee" : parser.parse_args().endurable_gasFee
    }
    
    amount = parser.parse_args().amount
    from_tokenSymbol = parser.parse_args().from_tokenSymbol
    to_tokenSymbol = parser.parse_args().to_tokenSymbol
    fromChain = parser.parse_args().fromChain
    toChain = parser.parse_args().toChain
    middle_chain = parser.parse_args().middle_chain
    
    rebalance = Rebalance(
        config
    )
    
    async def main():
        result = await rebalance.create_rebalance(amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, middle_chain=middle_chain)
        
        return result
            
    result = asyncio.run(main())
    logging.info(result)
    
    