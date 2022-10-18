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
    
    #Klayswap Token Balance
    print(klayswap.fetch_balance(['KETH','ZEMIT']))
    
    #Meshswap Token Swap
    print(meshswap.create_swap(0.1, 'USDC' , 0.0000000000001, 'oZEMIT'))

    orbitbridge = Orbitbridge()

    orbitbridge.account = klayswap.account
    orbitbridge.privateKey = klayswap.privateKey

    #Orbitbridge Token bridge
    print(orbitbridge.create_bridge(0.1, 'ZEMIT','KLAYTN', 'MATIC', meshswap.account))



```

### Installation
The easiest way to install the CCDXT library is to use a package manager:

- [ccdxt in **PyPI**](https://pypi.org/project/ccdxt/0.1/) (Python 3.7.3+)

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
| <img src = "https://user-images.githubusercontent.com/52026496/187066162-91d1a0bb-bf79-47f6-a8fa-e6cc70d2a628.png" width="1000" height="100">          | klaytn     | 1     | [Klayswap](https://klayswap.com/)            |                      [![API Version 2](https://img.shields.io/badge/*-lightgray)](https://klayswap.com/)
| <img src = "https://user-images.githubusercontent.com/52026496/190897330-6a8fdc62-262b-45af-b351-666de5cbbdeb.png" width="1000" height="100">        | klaytn     | 2       | [Klex Finance](https://app.klex.finance/trade#/)                    | [![API Version *](https://img.shields.io/badge/*-lightgray)](https://app.klex.finance/trade#/)
| <img src = "https://user-images.githubusercontent.com/52026496/191001922-56d713cc-0051-4221-99d1-66cf62c8bccf.png" width="1000" height="100">        | klaytn     | 3       | [Pala swap](https://pala.world/dex/swap)                    | [![API Version *](https://img.shields.io/badge/*-lightgray)](https://pala.world/dex/swap)
| <img src = "https://user-images.githubusercontent.com/52026496/191001922-56d713cc-0051-4221-99d1-66cf62c8bccf.png" width="1000" height="100">        | klaytn     | 3       | [Pala swap]https://kokonutswap.finance/swap)                    | [![API Version *](https://img.shields.io/badge/*-lightgray)]https://kokonutswap.finance/swap)
| <img src = "https://user-images.githubusercontent.com/52026496/187066122-0d88730a-8c6f-40c1-9f41-9869e2ef86c7.png" width="1000" height="100">        | polygon    | 4       | [Meshswap](https://meshswap.fi/)                    | [![API Version *](https://img.shields.io/badge/*-lightgray)](https://meshswap.fi/)                              
|

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Multi chains Support
    - [x] klaytn
    - [ ] polygon
    - [ ] fantom
    - [ ] etherium
- [x] Multi call Support
- [x] Cross chains Support
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
