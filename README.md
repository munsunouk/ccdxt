# CCDXT – CryptoCurrency Decentralized eXchange Trading Library

<!-- PROJECT SHIELDS -->
![LanguagesCount][languagesCount-shield]
![LanguagesTop][languagesTop-shield]
[![Commit][commit-shield]][commit-url]
![CommitLast][commitLast-shield]
[![MIT License][license-shield]][license-url]

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#Exchanges">Supported Cryptocurrency Exchanges</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Here's why:
* ccxt only has centralized exchange not on Decentralized
* each swap has there own function
* It is intended to be used by coders, developers, technically-skilled traders, data-scientists and financial analysts for building trading algorithms.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* ![Python][Python-shield]
* ![Solidity][Solidity-shield]

<!-- GETTING STARTED -->
## Getting Started

```python
from ccdxt.exchange import Klayswap,Meshswap,Orbitbridge

if __name__ == "__main__" :
    
    klayswap = Klayswap()
    klayswap.account = ''
    klayswap.privateKey = ''
    
    #Token
    print(klayswap.fetch_balance(['KETH','ZEMIT']))
    '''
    [
      {
        'symbol': 'KETH', 
        'balance': 0.000587
      }, 
      {
        'symbol': 'ZEMIT', 
        'balance': 1.888802
      }
    ]
    '''
    
    # Swap
    print(meshswap.create_swap(0.1, 'USDC' , 0.0000000000001, 'oZEMIT'))
    
    '''
    Return 
    {
      'transaction_hash': '0x21895bbec44e6dab91668fb338a43b3eb59fa78ae623499bf8f313ef827301c4', 
      'status': 1, 
      'block': 34314499, 
      'timestamp': datetime.datetime(2022, 10, 14, 10, 17, 58, 885156), 
      'function': <Function swapExactTokensForTokens(uint256,uint256,address[],address,uint256)>, 
      'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF', 
      'amountIn': 0.1, 
      'tokenA': 'USDC', 
      'to': '0x10f4A785F458Bc144e3706575924889954946639', 
      'amountOut': 0.623371, 
      'tokenB': 'oZEMIT', 
      'transaction_fee:': 0.023495964646856035
    }
    '''

    orbitbridge = Orbitbridge()

    orbitbridge.account = klayswap.account
    orbitbridge.privateKey = klayswap.privateKey

    '''
    {
      'transaction_hash': '0x6ea0feb76b39e4a2b03e553b4fbbacf8aefb8e5a1f7911893891fc49e5d8db79', 
      'status': 1, 
      'block': 34314503, 
      'timestamp': datetime.datetime(2022, 10, 14, 10, 18, 6, 614884), 
      'function': <Function requestSwap(address,string,bytes,uint256)>,
      'from': '0x78352F58E3ae5C0ee221E64F6Dc82c7ef77E5cDF', 
      'amountIn': 0.622748, 
      'tokenA': 'oZEMIT', 
      'to': '0x9Abc3F6c11dBd83234D6E6b2c373Dfc1893F648D', 
      'from_chain': 'MATIC', 
      'to_chain': 'KLAYTN', 
      'transaction_fee:': 0.009408398005397502
    }
    '''



```

### Installation
_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

* pip
  ```sh
  pip install git+https://github.com/MunSunouk/ccdxt.git
  ```

*  Clone the repo
   ```sh
   git clone https://github.com/MunSunouk/ccdxt.git
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Supported Cryptocurrency Exchanges -->
## Supported Cryptocurrency Exchanges

| logo                                                                                                                                                                                   | chain            | id            | name                                                                           | ver                                                                                                                                       | 
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|---------------|--------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------:|
| [![klayswap](ccdxt/icon/market-icons/klayswap.jpg)](https://klayswap.com/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)    | 1       | [Klayswap](https://klayswap.com/)            |                      [![API Version 1](https://img.shields.io/badge/*-lightgray)](https://klayswap.com/)
| [![Klex Finance](ccdxt/icon/market-icons/klex-finance.jpg)](https://app.klex.finance/trade#/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      | 2       | [Klex Finance](https://app.klex.finance/trade#/)                    | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://app.klex.finance/trade#/)
| [![Pala swap](ccdxt/icon/market-icons/pala.jpg)](https://pala.world/dex/swap)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      | 3       | [Pala swap](https://pala.world/dex/swap)                    | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://pala.world/dex/swap)
|[![Pangea swap](ccdxt/icon/market-icons/pangea-swap.jpg)](https://app.pangeaswap.com/swap)           | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      |  4      | [Pangea swap](https://app.pangeaswap.com/swap)                    | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://app.pangeaswap.com/swap)
| [![neuron swap](ccdxt/icon/market-icons/neuronswap.jpg)](https://www.neuronswap.com/swap)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      |  5       | [neuron swap](https://www.neuronswap.com/swap)                    | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://www.neuronswap.com/swap)
| [![claimswap](ccdxt/icon/market-icons/claimswap.jpg)](https://app.claimswap.org/swap)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      |  6       | [claimswap](https://app.claimswap.org/swap)                    | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://app.claimswap.org/swap)
| [![definix](ccdxt/icon/market-icons/definix.jpg)](https://bsc.definix.com/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/) [![bsc](ccdxt/icon/chain-icons/rsz_binance.jpg)](https://bscscan.com/)   |  7       | [definix](https://bsc.definix.com/)                    | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://bsc.definix.com/)
|[![Meshswap](ccdxt/icon/market-icons/meshswap.jpg)](https://meshswap.fi/)          | [![polygon](ccdxt/icon/chain-icons/rsz_polygon.jpg)](https://polygon.technology/)    |  6       | [Mesh swap](https://meshswap.fi/)                    | [![API Version 1](https://img.shields.io/badge/*-lightgray)](https://meshswap.fi/)                              
|[![Oribitbridge](ccdxt/icon/market-icons/orbitbridge.jpg)](https://bridge.orbitchain.io/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/) [![polygon](ccdxt/icon/chain-icons/rsz_polygon.jpg)](https://polygon.technology/)   |  7       | [Orbit bridge](https://bridge.orbitchain.io/)                    | [![API Version 1](https://img.shields.io/badge/*-lightgray)](https://bridge.orbitchain.io/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Multi chains Support
    - [x] klaytn
    - [ ] polygon
    - [ ] fantom
    - [ ] etherium
- [x] Multi call Support
- [x] Cross chsins Support
- [ ] Optimism path Support
- [ ] Async Support

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License
Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Contributor :[@munseon_ug](https://twitter.com/munseon_ug) 

Project Link: [https://github.com/MunSunouk/ccdxt](https://github.com/MunSunouk/ccdxt)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[languagesCount-shield]: https://img.shields.io/github/languages/count/MunSunouk/ccbxt?style=for-the-badge
[languagesTop-shield]: https://img.shields.io/github/languages/top/MunSunouk/ccbxt?style=for-the-badge

[commit-shield]: https://img.shields.io/github/commit-activity/w/MunSunouk/ccbxt?style=for-the-badge
[commit-url]: https://github.com/MunSunouk/ccbxt/graphs/commit-activity

[commitLast-shield]: https://img.shields.io/github/last-commit/MunSunouk/ccbxt?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/MunSunouk/ccbxt?style=for-the-badge
[license-url]: https://github.com/MunSunouk/ccbxt/master/LICENSE.txt

[Python-shield]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Solidity-shield]: https://img.shields.io/badge/Solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white
