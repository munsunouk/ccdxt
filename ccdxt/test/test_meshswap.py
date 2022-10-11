import sys
sys.path.append('/Users/munseon-ug/ccdxt')
from ccdxt.exchange import Meshswap

if __name__ == "__main__" :
    
    meshswap = Meshswap()
    meshswap.account = ''
    meshswap.privateKey = ''
    
    # #Token
    # print(klayswap.fetch_balance())
    
    # # Swap
    # print(klayswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))