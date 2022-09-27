import sys
sys.path.append('/Users/munseon-ug/ccdxt')
from ccdxt.exchange import Klayswap

if __name__ == "__main__" :
    
    klayswap = Klayswap()
    klayswap.account = ''
    klayswap.privateKey = ''
    
    # #Token
    # print(klayswap.fetch_balance())
    
    # # Swap
    # print(klayswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))