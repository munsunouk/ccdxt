- ![Python][Python-shield]
- ![Solidity][Solidity-shield]

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

* Clone the repo
  ```sh
  git clone https://github.com/MunSunouk/ccdxt.git
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Supported Cryptocurrency Exchanges -->

## Supported Cryptocurrency Exchanges

| logo                                                                                          | chain                                                                                                                                                            | id  | name                                             |                                               ver                                                |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | ------------------------------------------------ | :----------------------------------------------------------------------------------------------: |
| [![klayswap](ccdxt/icon/market-icons/klayswap.jpg)](https://klayswap.com/)                    | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)                                                                                   | 1   | [Klayswap](https://klayswap.com/)                |       [![API Version 1](https://img.shields.io/badge/*-lightgray)](https://klayswap.com/)        |
| [![Klex Finance](ccdxt/icon/market-icons/klex-finance.jpg)](https://app.klex.finance/trade#/) | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)                                                                                   | 2   | [Klex Finance](https://app.klex.finance/trade#/) | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://app.klex.finance/trade#/) |
| [![Pala swap](ccdxt/icon/market-icons/pala.jpg)](https://pala.world/dex/swap)                 | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)                                                                                   | 3   | [Pala swap](https://pala.world/dex/swap)         |   [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://pala.world/dex/swap)    |
| [![Pangea swap](ccdxt/icon/market-icons/pangea-swap.jpg)](https://app.pangeaswap.com/swap)    | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)                                                                                   | 4   | [Pangea swap](https://app.pangeaswap.com/swap)   | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://app.pangeaswap.com/swap)  |
| [![neuron swap](ccdxt/icon/market-icons/neuronswap.jpg)](https://www.neuronswap.com/swap)     | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)                                                                                   | 5   | [neuron swap](https://www.neuronswap.com/swap)   | [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://www.neuronswap.com/swap)  |
| [![claimswap](ccdxt/icon/market-icons/claimswap.jpg)](https://app.claimswap.org/swap)         | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/)                                                                                   | 6   | [claimswap](https://app.claimswap.org/swap)      |  [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://app.claimswap.org/swap)  |
| [![definix](ccdxt/icon/market-icons/definix.jpg)](https://bsc.definix.com/)                   | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/) [![bsc](ccdxt/icon/chain-icons/rsz_binance.jpg)](https://bscscan.com/)            | 7   | [definix](https://bsc.definix.com/)              |     [![API Version 1](https://img.shields.io/badge/0.1-lightgray)](https://bsc.definix.com/)     |
| [![Meshswap](ccdxt/icon/market-icons/meshswap.jpg)](https://meshswap.fi/)                     | [![polygon](ccdxt/icon/chain-icons/rsz_polygon.jpg)](https://polygon.technology/)                                                                                | 6   | [Mesh swap](https://meshswap.fi/)                |        [![API Version 1](https://img.shields.io/badge/*-lightgray)](https://meshswap.fi/)        |
| [![Oribitbridge](ccdxt/icon/market-icons/orbitbridge.jpg)](https://bridge.orbitchain.io/)     | [![klaytn](ccdxt/icon/chain-icons/rsz_klaytn.jpg)](https://klaytn.foundation/) [![polygon](ccdxt/icon/chain-icons/rsz_polygon.jpg)](https://polygon.technology/) | 7   | [Orbit bridge](https://bridge.orbitchain.io/)    |   [![API Version 1](https://img.shields.io/badge/*-lightgray)](https://bridge.orbitchain.io/)    |

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
