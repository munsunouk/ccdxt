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
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
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
from src.exchange import Klayswap

if __name__ == "__main__" :
    
    klayswap = Klayswap()
    klayswap.account = ''
    klayswap.privateKey = ''
    
    #Token
    print(klayswap.fetch_balance())
    
    # Swap
    print(klayswap.create_swap(0.1, 'oUSDT' , 0.0000000000001, 'oETH'))
```

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* pip
  ```sh
  pip install web3
  ```

### Installation
_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

*  Clone the repo
   ```sh
   git clone https://github.com/MunSunouk/ccbxt.git
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Supported Cryptocurrency Exchanges -->
## Supported Cryptocurrency Exchanges


| logo                                                                                                                                                                                   | chain            | id            | name                                                                           | ver                                                                                                                                       | 
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|---------------|--------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------:|
| <img src = "https://user-images.githubusercontent.com/52026496/187066162-91d1a0bb-bf79-47f6-a8fa-e6cc70d2a628.png" width="1000" height="100">          | klaytn     | 1     | [Klayswap](https://klayswap.com/)            |                      [![API Version 2](https://img.shields.io/badge/*-lightgray)](https://ascendex.github.io/ascendex-pro-api/#ascendex-pro-api-documentation)
| <img src = "https://user-images.githubusercontent.com/52026496/190897330-6a8fdc62-262b-45af-b351-666de5cbbdeb.png" width="1000" height="100">        | klaytn     | 2       | [Klex Finance](https://app.klex.finance/trade#/)                    | [![API Version *](https://img.shields.io/badge/*-lightgray)](https://binance-docs.github.io/apidocs/spot/en)
| <img src = "https://user-images.githubusercontent.com/52026496/187066122-0d88730a-8c6f-40c1-9f41-9869e2ef86c7.png" width="1000" height="100">        | polygon    | 3       | [Meshswap](https://meshswap.fi/)                    | [![API Version *](https://img.shields.io/badge/*-lightgray)](https://binance-docs.github.io/apidocs/spot/en)                              
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

Your Name - [@munseon_ug](https://twitter.com/munseon_ug) - email@example.com

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