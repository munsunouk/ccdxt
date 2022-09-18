from src.exchange import Klexfinance

if __name__ == "__main__" :
    
    klexfinance = Klexfinance()
    klexfinance.account = ''
    klexfinance.privateKey = ''
    
    #Token
    print(klexfinance.fetch_tokens())
    
    #Swap
    print(klexfinance.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))