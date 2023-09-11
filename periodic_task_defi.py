import sys
from pathlib import Path
import argparse

basePath = Path(__file__).resolve().parent.parent
sys.path.append(str(basePath))

from mars.lib.periodic_task_defi import PeriodicTasks

def main():
    
    parser = argparse.ArgumentParser(description="Argparse for task")
    
    parser.add_argument("--debug", type=bool, default=False)
    
    config = {
        'db_config' : {
            'local_private_key' : '/Users/munseon-ug/.ssh/id_rsa',
            'server_private_key' : '/home/www/.ssh/id_rsa',
            'password_path' : '../key/product_db_password.bin',
            'endpoint' : 'pv-trading-db-0-tradingdev.cluster-custom-ccs723yxzmmf.ap-northeast-2.rds.amazonaws.com',
            'port' : '3306',
            'user' : 'trade_writer',
            'db_name' : 'TRADE_DATA',
            'debug' : parser.parse_args().debug,
        }
    }
    
    accounts = {
        30000 : {
            'market_code' : 2, 
            'address' : '0xD79B294e39f81AF511589cF81550C21FeEbaa719', 
            'token_list' : [ 'kMOOI', 'kUSDT', 'KLAY', 'kMATIC' ]
        },
        30001 : {
            'market_code' : 1, 
            'address' : '0xf78961078d1480c1f21263ae89d8784b56246f0f', 
            'token_list' : [ 'MOOI', 'SD' ]
        },
        30002 : {
            'market_code' : 3, 
            'address' : '0x91280953008E5F93b03663fbaFBC3d6522a9FDAf', 
            'token_list' : [ 'USDC.p', 'oMOOI', 'MATIC', 'oKLAY' ]
        },
        30003 : {
            'market_code' : 1, 
            'address' : '0xcf8327f2e026c571582fbd16b2a839112a3e734d', 
            'token_list' : [
                'MOOI', 'XRP.m'
                ]
        },
        30004 : {
            'market_code' : 2, 
            'address' : '0xcf8327f2e026c571582fbd16b2a839112a3e734d', 
            'token_list' : [ 'kMOOI', 'kXRP', 'KLAY' ]
        },
        30005 : {
            'market_code' : 0,
            'chain_symbol' : 'ETH', 
            'address' : '0xa0CcD11f29e039606b035d35d80Fee496229052A', 
            'token_list' : [ 'ETH' ]
        },
        30006 : {
            'market_code' : 2, 
            'address' : '0xd11e6A8825c7AD7456A0DC99FC9A1F05a982D302', 
            'token_list' : [
                'kMOOI', 'kXRP', 'KLAY', 'kUSDT'
                ]
        },
        30007 : {
            'market_code' : 2,
            'address' : '0x5924C90B472A1D4005fd294AE9452F537A100072',
            'token_list' : [
                'kMOOI', 'kUSDT', 'KLAY', 'kETH'
                ]
        },
        30008 : {
            'market_code' : 2,
            'address' : '0x867609F998eC46A65c4EA0da15bfa2a6Cb9814b3',
            'token_list' : [
                'kMOOI', 'kUSDT', 'KLAY'
                ]
        },
        30009 : {
            'market_code' : 8,
            'address' : '0x972Cd4dde100eF76b9C93deD4471B64AdE4aDb40',
            'token_list' : ['mFXS', 'mUSDT', 'MATIC', 'USDC.p']
        },
        30010 : {
            'market_code' : 9,
            'address' : '0x972Cd4dde100eF76b9C93deD4471B64AdE4aDb40',
            'token_list' : ['FTM']
        },
        30011 : {
            'market_code' : 3,
            'name' : 'Metamask_PostVoyager_Mariner_Hed_test',
            'address' : '0xa0CcD11f29e039606b035d35d80Fee496229052A',
            'token_list' : ['MATIC']
        },
        30012 : {
            'market_code' : 2,
            'name' : 'Metamask_PostVoyager_Mariner_Hed_test',
            'address' : '0xa0CcD11f29e039606b035d35d80Fee496229052A',
            'token_list' : ['kMOOI', 'KLAY', 'kUSDT']
        },
        30013 : {
            'market_code' : 10,
            'name' : 'Metamask_PostVoyager_Viking',
            'address' : '0x972Cd4dde100eF76b9C93deD4471B64AdE4aDb40',
            'token_list' : ['AVAX', 'USDT.e', 'aFXS', 'aUSDC']
        },                
        30014 : {
            'market_code' : 2,
            'name' : 'Kaikas_Account_2',
            'address' : '0x2a308d52a12d4D0E6624B632bcc4151bFFCbbA9d',
            'token_list' : ['KLAY']
        },
        30015 : {
            'market_code' : 1, 
            'name' : 'MOOIwallet_PostVoyager_test',
            'address' : '0xba711275a5fa8ef3e04674a7afad64837b8abbc7', 
            'token_list' : [ 'MOOI']
        },
        30016 : {
            'market_code' : 2,
            'name' : 'Metamask_PostVoyager_Phoenix_Hed_prod',
            'address' : '0xc368f7092315a24ddbb66ac016f9cbdc532ca5af',
            'token_list' : ['KLAY', 'kUSDT']
        },        
        30017 : {
            'market_code' : 3,
            'name' : 'Metamask_PostVoyager_Phoenix_Hed_prod',
            'address' : '0xc368f7092315a24ddbb66ac016f9cbdc532ca5af',
            'token_list' : ['MATIC']
        },                
        30018 : {
            'market_code' : 1,
            'name' : 'Metamask_PostVoyager_Mariner1_Hed(MOOI)',
            'address' : '0x5924C90B472A1D4005fd294AE9452F537A100072',
            'token_list' : ['MOOI']
        },
        30019 : {
            'market_code' : 1,
            'name' : 'Metamask_PostVoyager_Mariner2_Hed(MOOI)',
            'address' : '0x867609F998eC46A65c4EA0da15bfa2a6Cb9814b3',
            'token_list' : ['MOOI']
        },
    }
    
    peridoic_taks = PeriodicTasks(config)
    
    peridoic_taks.get_balances(accounts)
    

if __name__ == "__main__":
        
    main()