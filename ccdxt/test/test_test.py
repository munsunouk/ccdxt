import sys
sys.path.append('/Users/munseon-ug/ccdxt')
from ccdxt.base.test import binance

if __name__ == "__main__" :
    
    klayswap = binance()
    print(klayswap.__dict__)
    print(klayswap.chains)