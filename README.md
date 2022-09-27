# CCDXT – CryptoCurrency Decentralized eXchange Trading Library

<!-- PROJECT SHIELDS -->
![LanguagesCount][languagesCount-shield]
![LanguagesTop][languagesTop-shield]
[![Commit][commit-shield]][commit-url]
![CommitLast][commitLast-shield]
[![MIT License][license-shield]][license-url]
[![Blog][blog-shield]][blog-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

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
from ccdxt.exchange import Klayswap

if __name__ == "__main__" :
    
    klayswap = Klayswap()
    klayswap.account = ''
    klayswap.privateKey = ''
    
    #Token
    print(klayswap.fetch_balance())
    
    # Swap
    print(klayswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))
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
| [![klayswap](ccdxt/icon/market-icons/klayswap.jpg)](https://klayswap.com/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)    | 1       | [Klayswap](https://klayswap.com/)            |                      [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://klayswap.com/)
| [![Klex Finance](ccdxt/icon/market-icons/klex-finance.jpg)](https://app.klex.finance/trade#/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      | 2       | [Klex Finance](https://app.klex.finance/trade#/)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://app.klex.finance/trade#/)
| [![Pala swap](ccdxt/icon/market-icons/pala.jpg)](https://pala.world/dex/swap)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      | 3       | [Pala swap](https://pala.world/dex/swap)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://pala.world/dex/swap)
|[![Pangea swap](ccdxt/icon/market-icons/pangea-swap.jpg)](https://app.pangeaswap.com/swap)           | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      |  4      | [Pangea swap](https://app.pangeaswap.com/swap)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://app.pangeaswap.com/swap)
| [![neuron swap](ccdxt/icon/market-icons/neuronswap.jpg)](https://www.neuronswap.com/swap)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      |  5       | [neuron swap](https://www.neuronswap.com/swap)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://www.neuronswap.com/swap)
| [![claimswap](ccdxt/icon/market-icons/claimswap.jpg)](https://app.claimswap.org/swap)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)      |  6       | [claimswap](https://app.claimswap.org/swap)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://app.claimswap.org/swap)
| [![definix](ccdxt/icon/market-icons/definix.jpg)](https://bsc.definix.com/)          | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/) [![bsc](ccdxt/icon/chain-icons/rsz_binance.jpg)](https://bscscan.com/)   |  7       | [definix](https://bsc.definix.com/)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://bsc.definix.com/)
|[![Meshswap](ccdxt/icon/market-icons/meshswap.jpg)](https://meshswap.fi/)          | [![polygon](ccdxt/icon/chain-icons/rsz_polygon.jpg)](https://polygon.technology/)    |  6       | [Meshswap](https://meshswap.fi/)                    | [![API Version 1](https://img.shields.io/badge/1-lightgray)](https://meshswap.fi/)                              
|

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Multi chains Support
    - [ ] klaytn
    - [ ] polygon
    - [ ] fantom
    - [ ] etherium

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

[blog-shield]: https://img.shields.io/badge/-Blog-000000?style=for-the-badge&logo=Tistory&&logoColor=white
[blog-url]: https://baobao.tistory.com/

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://www.linkedin.com/in/%EC%84%A0%EC%9A%B1-%EB%AC%B8-854b5219a/

[Python-shield]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Solidity-shield]: https://img.shields.io/badge/Solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white