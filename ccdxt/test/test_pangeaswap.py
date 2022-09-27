from ccdxt.exchange import Pangeaswap

if __name__ == "__main__" :
    
    pangeaswap = Pangeaswap()
    pangeaswap.account = ''
    pangeaswap.privateKey = ''
    
    # print(pangeaswap.tokens)
    
    # #Token
    # print(pangeaswap.fetch_balance())
    
    # # Swap
    # print(pangeaswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))