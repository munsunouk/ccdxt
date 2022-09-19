from src.exchange import Klayswap

if __name__ == "__main__" :
    
    klayswap = Klayswap()
    klayswap.account = ''
    klayswap.privateKey = ''
    
    #decode
    print(klayswap.decode('0xb18a25ee9fca4ae27b80d50b9d1f74f19775bd25c1425bc5483fc0a35033c889'))
    
    # #Token
    # print(klayswap.fetch_balance())
    
    # # Swap
    # print(klayswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))