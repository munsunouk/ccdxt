import sys
from pathlib import Path
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
from enum import Enum

basePath = Path(__file__).resolve().parent.parent

sys.path.append(str(basePath))

from lib import Sql
from exchange import Klayswap, Meshswap, Mooiswap, Oneinchswap, Openocean
from base import Exchange

class ExchangeName(Enum) :
    
    Exchange = 0
    Mooiswap = 1
    Klayswap = 2
    Meshswap = 3
    Oneinchswap = 6
    Openocean_MATIC = 8
    Openocean_FTM = 9
    Openocean_AVAX = 10

class PeriodicTasks:
    
    def __init__(self, config):
        
        self.db = None
        self.exchanges = {}
        self.accounts = {}
        
        self.set_task(config)
        
    def set_task(self, config):
        
        self.set_db(config['db_config'])
        self.set_exchange()
            
    def set_exchange(self):
        
        for market in ExchangeName.__members__.values() :
            
            if "_" in market.name :
    
                tmp_market = market.name.split("_")
                
                tmp_market_config = {'chainName' : tmp_market[1]}
                
                self.exchanges[market.value] = eval(tmp_market[0] + f"({tmp_market_config})")
                
            else :
        
                self.exchanges[market.value] = eval(market.name + "()")
        
    def set_db(self, db_config):
        
        debug = db_config['debug']
        
        if debug :
            
            private_key_path = db_config['local_private_key']
            
        else :
            
            private_key_path = db_config['server_private_key']
        
        password_path = db_config['password_path']
        
        db_password = self.decode_key(private_key_path, password_path)
        
        db_config = {
            'password' : db_password,
            'endpoint' : db_config['endpoint'],
            'port' : db_config['port'],
            'user' : db_config['user'],
            'db_name' : db_config['db_name']
        }
    
        self.db = Sql(db_config)
        
    def decryption(self, arg_privatekey, arg_b64text):
        decoded_data = base64.b64decode(arg_b64text)
        decryptor = PKCS1_OAEP.new(arg_privatekey)
        decrypted = decryptor.decrypt(decoded_data)
        return decrypted.decode('ascii')
    
    def decode_key(self, private_key_path, password_path):

        with open(private_key_path, 'rb') as f_privkey:
            privatekey = RSA.importKey(f_privkey.read())

        with open(password_path, "rb") as file_in:
            encoded_key = file_in.readline()
            
        result = self.decryption(privatekey, encoded_key)

        return result

    def get_balance(self, exchange, address, token_list, chain_symbol=None):
        
        if chain_symbol :
            
            exchange.load_exchange(chain_symbol)
        
        exchange.account = address
        
        balance = exchange.fetch_balance(token_list)
        
        raw_balance = balance['result']
        assets = {}
        
        for token in raw_balance :
            
            assets[token] = {"free" : raw_balance[token], "used" : 0, "total" : raw_balance[token], "profit" : 0, "wallet" : 0}
            
        return assets, raw_balance
    
    def get_balances(self, accounts):

        for account in accounts :
            
            if 'chain_symbol' in accounts[account] :
                
                assets, raw_balance = self.get_balance(self.exchanges[accounts[account]['market_code']], accounts[account]['address'], accounts[account]['token_list'], accounts[account]['chain_symbol'])
                
            else :
            
                assets, raw_balance = self.get_balance(self.exchanges[accounts[account]['market_code']], accounts[account]['address'], accounts[account]['token_list'])
            
            new_assets = {}
            for old_key, value in assets.items():
                if old_key[0] in ('k', 'w'):
                    
                    if old_key[1:] == 'MOOI' :
                        
                        new_key = old_key[1:]
                        
                    else :
                    
                        new_key = 'o' + old_key[1:]
                        
                elif old_key[0].islower() :
                    
                    new_key = old_key[1:]
                
                else:
                    new_key = old_key
                new_assets[new_key] = value

            self.db.insert_balance(accounts[account]['market_code'], account, new_assets, raw_balance)
