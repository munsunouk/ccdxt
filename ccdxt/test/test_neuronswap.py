from ccdxt.exchange import Neuronswap

if __name__ == "__main__" :
    
    neuronswap = Neuronswap()
    neuronswap.account = ''
    neuronswap.privateKey = ''
    
    #Token
    print(neuronswap.fetch_balance())
    
    # Swap
    print(neuronswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))