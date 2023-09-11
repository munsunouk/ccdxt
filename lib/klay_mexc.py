import sys
from pathlib import Path
from typing import Optional
import ccxt

basePath = Path(__file__).resolve().parent.parent
sys.path.append(str(basePath))
from mars.base.utils.decode import DecodeKey
from exchange import Oneinchswap, Mooibridge, Orbitbridge, Klayswap
import logging

class Rebalance:
    
    def __init__(self, _config_change: Optional[dict] = {}):
        
        super().__init__()

        self._config = {
            "klay_account": None,
            "klay_privateKey": None,
            
            "mooi_account" : None,
            "mooi_privateKey" : None,
            
            "eth_account" : None,
            "eth_privateKey" : None,
            
            "mexc_mooi_account" : None,
            "mexc_klay_account" : None,
            "mexc_eth_account" : None,
            
            "mexc_account" : None,
            "mexc_privateKey" : None,
            
            "endurable_gasFee" : None,
        }

        self._config.update(_config_change)
        # key_map = {
        #             'mexc_api':'', 
        #             'mexc_sec':'', 
        #             'mariner1_meta':'', 
        #             'mariner1_meta_key':'', 
        #             'mariner2_meta':'',
        #             'mariner2_meta_key':''
        # }

        self._klay_account = self._config['klay_account']
        self._klay_privateKey = DecodeKey().decode_key(self._config['klay_privateKey'])
        
        self._eth_account = self._config['eth_account']
        self._eth_privateKey = DecodeKey().decode_key(self._config['eth_privateKey'])       
        
        self._mooi_account = self._config['mooi_account']
        self._mooi_privateKey = DecodeKey().decode_key(self._config['mooi_privateKey'])
        
        self._mexc_mooi_account = self._config['mexc_mooi_account']
        self._mexc_klay_account = self._config['mexc_klay_account']
        self._mexc_eth_account = self._config['mexc_eth_account']
        
        self._mexc_account = DecodeKey().decode_key(self._config['mexc_account'])
        self._mexc_privateKey = DecodeKey().decode_key(self._config['mexc_privateKey'])
        
        self.endurable_gasFee = self._config['endurable_gasFee']
        
        # self._mexc_account = self.get_encode_data(self._config['mexc_account'])
        # self._mexc_account = DecodeKey().decode_key(f"{self._config['mexc_account']}.bin")
        # self._mexc_privateKey = DecodeKey().decode_key(f"{self._config['mexc_privateKey']}.bin")
        
        self._set_rebalance()
        
    # def get_encode_data(self, _encode_data):
        
    #     if _encode_data != None:

    #         if len(_encode_data) > 200 :

    #             result = DecodeKey().decode_key(f"{_encode_data}.bin")
                
    #         else :

    #             result = _encode_data
                
    #     else :
            
    #         result = _encode_data
            
    #     return result
        
    def _set_rebalance(self):
        
        self.mexc = ccxt.mexc({
            'apiKey': self._mexc_account,
            'secret': self._mexc_privateKey,
        })
        
        # self.klaytn_1inch = Oneinchswap()
        self.klayswap = Klayswap()
        
        self.bridgeA = Mooibridge()
        self.bridgeB = Orbitbridge()
        
    async def create_rebalance(self, amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, *args, **kwargs):
        
        result = None
        
        if kwargs :
            
            if 'middle_chain' in kwargs :
                
                if kwargs['middle_chain'] == 'KLAYTN' :
                    
                    middle_chain = 'KLAYTN'
                    
                elif kwargs['middle_chain'] == 'ETH':
                    
                    middle_chain = 'ETH'
                    
                else :
                    
                    middle_chain = 'KLAYTN'
                    
            else :
                
                middle_chain = 'KLAYTN'
                
        else :
            
            if args :
                
                middle_chain = args[0]
                
            else :
            
                middle_chain = 'KLAYTN'
        
        if (fromChain == 'KLAYTN') and  (from_tokenSymbol == 'kMOOI'):
            
            self.bridgeA.account = self._klay_account
            self.bridgeA.privateKey = self._klay_privateKey
            
            if toChain == 'MEXC' :
                
                toChain = 'MOOI'
            
            tx_result = await self.bridgeA.create_bridge(amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, self._mooi_account, self._mooi_privateKey)
            
            fromChain = toChain
            self.bridgeA.account = self.bridgeA.set_checksum(self._mooi_account)
            self.bridgeA.privateKey = self._mooi_privateKey
            result = await self.bridgeA.create_transfer(tx_result['amount_out'], to_tokenSymbol, fromChain, self._mexc_mooi_account)
            
        elif (fromChain == 'KLAYTN') and (from_tokenSymbol == 'kUSDT'):

            if (middle_chain == 'KLAYTN') and (to_tokenSymbol == 'KLAY'):
                
                self.klayswap.account = self.klayswap.set_checksum(self._klay_account)
                self.klayswap.privateKey = self._klay_privateKey
                
                self.bridgeB.account = self.bridgeB.set_checksum(self._klay_account)
                self.bridgeB.privateKey = self._klay_privateKey
                
                tx_result = await self.klayswap.create_swap(amount, from_tokenSymbol, 0.0001, to_tokenSymbol)
                result = await self.bridgeB.create_transfer(tx_result['amount_out'], to_tokenSymbol, fromChain, self._mexc_klay_account)
        
        elif (fromChain == 'MEXC') and  (from_tokenSymbol == 'MOOI'):
            
            fromChain = 'MOOI'
            
            self.bridgeA.account = self._mooi_account
            self.bridgeA.privateKey = self._mooi_privateKey
            
            self.bridgeA.amount = amount
            
            self.mexc.withdraw(from_tokenSymbol, amount, self._klay_account)
            self.bridgeA.load_exchange(fromChain)
            
            time_spend, amount = self.bridgeA.check_bridge_completed(from_tokenSymbol, self._mooi_account)
            amount = self.bridgeA.to_value(amount, self.bridgeA.decimals(from_tokenSymbol))
            
            result = await self.bridgeA.create_bridge(amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain, self._klay_account, self._klay_privateKey)
        
        elif (fromChain == 'MEXC') and  (from_tokenSymbol == 'KLAY'):
            
            self.klayswap.account = self.klayswap.set_checksum(self._klay_account)
            self.klayswap.privateKey = self._klay_privateKey
            
            self.bridgeA.amount = amount
            
            self.mexc.withdraw(from_tokenSymbol, amount, self._klay_account)
            self.bridgeA.load_exchange(toChain)

            time_spend, amount = self.bridgeA.check_bridge_completed(from_tokenSymbol, self._klay_account)
            balance = self.bridgeA.to_value(amount, self.bridgeA.decimals(from_tokenSymbol))
            
            result = await self.klayswap.create_swap(balance, from_tokenSymbol, 0.0001, to_tokenSymbol)
            
        elif (fromChain == 'MEXC') and (middle_chain == 'ETH') and (from_tokenSymbol == 'USDT'):
            
            symbol = 'ETH/USDT'
            fee = 4
            
            # ticker 정보 가져오기
            ticker_info = self.mexc.fetch_ticker(symbol)

            # 현재 가격 출력하기 (ask_price: 매도 호가, bid_price: 매수 호가)
            ask_price = ticker_info['ask']
            bid_price = ticker_info['bid']
            
            self.mexc.withdraw(from_tokenSymbol, amount, self._eth_account, params={"network" : "ETH"})
            
            self.bridgeB.account = self.bridgeB.set_checksum(self._eth_account)
            self.bridgeB.privateKey = self._eth_privateKey
            self.bridgeB.load_exchange(middle_chain)
            
            self.bridgeB.amount = amount
            time_spend, amount = self.bridgeB.check_bridge_completed(from_tokenSymbol, self._eth_account, fee=fee)
            
            balance = self.bridgeB.to_value(amount, self.bridgeB.decimals(from_tokenSymbol))
            self.bridgeB.amount = balance
            
            logging.info(f"Successfully withdrawed {balance} USDT from MEXC")
            
            self.bridgeB.gas_price = bid_price # mexc gas price for compare with endurable_gasFee
            self.bridgeB.least_balance = 0.005 # base currency at least need to hold for transfer
            self.bridgeB.endurable_gasFee = self.endurable_gasFee # gas fee endurable

            result = await self.bridgeB.create_bridge(balance, from_tokenSymbol, to_tokenSymbol, middle_chain, toChain, self._klay_account)
            
            logging.info(f"Successfully bridged {balance} USDT from Orbitbridge")
        
        else :
            
            raise ValueError(f"params error {amount, from_tokenSymbol, to_tokenSymbol, fromChain, toChain}")
            
        return result