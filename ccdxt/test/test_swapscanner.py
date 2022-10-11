import sys
sys.path.append('/Users/munseon-ug/ccdxt')
from ccdxt.exchange import Swapscanner

if __name__ == "__main__" :
    
    swapscanner = Swapscanner()
    
    result = swapscanner.decode('0x9b37272c3a5c379379c2fe9e3b8913f8aef246fbd88b6a8c5312e6cbc0d71cfa')
    print(result)