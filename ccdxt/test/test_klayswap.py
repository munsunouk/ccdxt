import sys
sys.path.append('/Users/munseon-ug/ccdxt')
from ccdxt.exchange import Klayswap

if __name__ == "__main__" :
    
    klayswap = Klayswap()
    klayswap.account = ''
    klayswap.privateKey = ''
    
    # #Token
<<<<<<< HEAD
    print(klayswap.fetch_balance(['KUSDT']))
=======
    # print(klayswap.fetch_balance(['MOOI','KETH']))
>>>>>>> b7b378547437940162b5ce590f14c744c431e0d8
    
    # # Swap
    # print(klayswap.create_swap(0.1, 'KUSDT' , 0.0000000000001, 'KETH'))