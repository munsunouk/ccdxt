from ccdxt.exchange import Palaswap

if __name__ == "__main__" :
    
    palaswap = Palaswap()
    palaswap.account = ''
    palaswap.privateKey = ''
    
    # print(palaswap.tokens)
    
    # #Token
    # print(palaswap.fetch_balance())
    
    # Swap
    print(palaswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))