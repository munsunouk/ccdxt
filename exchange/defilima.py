from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchWindowException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from pyvirtualdisplay import Display
import time
import os
import logging
from functools import wraps
from datetime import datetime
from collections import defaultdict
from webdriver_manager.chrome import ChromeDriverManager
import regex
from typing import Optional
from ..base.exchange import Exchange


class Defilima(Exchange):
    def __init__(self, config_change: Optional[dict] = {}):
        super().__init__()

        config = {
            "chainName": "MATIC",
            "exchangeName": "defilima",
            "retries": 3,
            "retriesTime": 10,
            "host": None,
            "account": None,
            "privateKey": None,
            "log": None,
            "proxy": False,
        }

        config.update(config_change)

        # market info
        self.id = 1
        self.chainName = config["chainName"]
        self.exchangeName = config["exchangeName"]
        self.duration = False
        self.addNounce = 0
        self.retries = config["retries"]
        self.retriesTime = config["retriesTime"]
        self.host = config["host"]
        self.account = config["account"]
        self.privateKey = config["privateKey"]
        self.log = config["log"]
        self.proxy = config["proxy"]
        self.install_wallet = config["metamask_extension"]

        self.load_exchange(self.chainName, self.exchangeName)
        self.set_logger(self.log)

        self.swap_page = "https://swap.defillama.com/"

        self.slippage = str(params["price_imp_klay"])

        self.retries = params["retries"]

        self.retriesTime = params["retriesTime"]

        self.tokenA = params["klayswap_tokenA"]
        self.tokenB = params["klayswap_tokenB"]

        self.password = params["kaikas_password"]

        self.seed = params["kaikas_seed"]

        self.klayswap_click_own_token = False

        # swap 위치에서 symbol 클릭 위치
        self.from_symbol = 1
        self.to_symbol = 3

    def set_crawling(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")  # resource access
        chrome_options.add_argument("--disable-dev-shm-usage")  # stop error by memory
        chrome_options.add_argument("--disable-setuid-sandbo")  # stop crush chrome
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/97.0.4692.71 Safari/537.36"
        )  # for not being catched as bot
        chrome_options.add_argument("lang=ko_KR")  # for korea site
        chrome_options.add_extension(os.path.expanduser(self.install_wallet))  # wallet extension

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.wait = WebDriverWait(driver=self.driver, timeout=self.retriesTime)

    def retry(method):
        """
        retry method on certain time
        result : 2022-08-13 18:44:03,221 - root - WARNING - 2022-08-13 18:44:03.221394 - flip_token - Attempt 0
        """

        @wraps(method)
        def retry_method(self, *args):
            for i in range(self.retries):
                logging.warning("{} - {} - Attempt {}".format(datetime.now(), method.__name__, i))
                time.sleep(self.retriesTime)
                try:
                    return method(self, *args)
                except (
                    TimeoutException,
                    NoSuchWindowException,
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                ):
                    if i == self.retries - 1:
                        raise

        return retry_method

    def retry_quote(method):
        """
        retry method on certain time for quote
        result : 2022-08-13 18:40:48,953 - root - WARNING - 2022-08-13 18:40:48.953195 - get_quoteData - Attempt 0
        """

        @wraps(method)
        def retry_method(self, *args):
            for i in range(self.retries):
                logging.warning("{} - {} - Attempt {}".format(datetime.now(), method.__name__, i))
                time.sleep(self.interval_time_pool_rt)
                try:
                    return method(self, *args)
                except (
                    TimeoutException,
                    NoSuchWindowException,
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                ):
                    if i == self.retries - 1:
                        raise

        return retry_method

    def main(self):
        """
        for start swap instance

        result : [
            2022-08-13 18:00:59,901 - WDM - INFO - ====== WebDriver manager ======
            2022-08-13 18:00:59,939 - WDM - INFO - Get LATEST chromedriver version for google-chrome 104.0.5112
            2022-08-13 18:01:00,170 - WDM - INFO - Driver [/root/.wdm/drivers/chromedriver/linux64/104.0.5112/chromedriver] found in cache
            2022-08-13 18:01:03,535 - root - WARNING - 2022-08-13 18:01:03.535196 - get_web - Attempt 0
            2022-08-13 18:01:10,622 - root - WARNING - 2022-08-13 18:01:10.622370 - get_klayswap - Attempt 0
            2022-08-13 18:01:15,634 - swap.klayswap - INFO - KLAY Get Web : None
            2022-08-13 18:01:15,634 - root - WARNING - 2022-08-13 18:01:15.634276 - connect_wallet - Attempt 0
            2022-08-13 18:01:21,312 - swap.klayswap - INFO - Connect Wallet : None
            2022-08-13 18:01:21,312 - root - WARNING - 2022-08-13 18:01:21.312410 - create_wallet - Attempt 0
            2022-08-13 18:01:26,667 - swap.klayswap - INFO - Create Wallet : None
            2022-08-13 18:01:26,667 - root - WARNING - 2022-08-13 18:01:26.667361 - restore_wallet - Attempt 0
            2022-08-13 18:01:34,469 - swap.klayswap - INFO - Restore Wallet : None
            2022-08-13 18:01:34,469 - root - WARNING - 2022-08-13 18:01:34.469619 - reconnect_wallet - Attempt 0
            2022-08-13 18:01:39,640 - swap.klayswap - INFO - Reconnect Wallet : None
            2022-08-13 18:01:42,674 - swap.klayswap - INFO - Get wallet risk info : None
            2022-08-13 18:01:42,674 - swap.klayswap - INFO - KLAY Get Wallet : None
            2022-08-13 18:01:42,674 - root - WARNING - 2022-08-13 18:01:42.674677 - retry_network - Attempt 0
            2022-08-13 18:01:53,599 - root - WARNING - 2022-08-13 18:01:53.599184 - click_asset - Attempt 0
            2022-08-13 18:01:58,669 - root - WARNING - 2022-08-13 18:01:58.669087 - click_swap - Attempt 0
            2022-08-13 18:02:03,802 - root - WARNING - 2022-08-13 18:02:03.802354 - get_token_info - Attempt 0
            2022-08-13 18:02:08,835 - root - WARNING - 2022-08-13 18:02:08.835435 - get_token_symbol - Attempt 0
            2022-08-13 18:02:14,129 - root - WARNING - 2022-08-13 18:02:14.129693 - get_riskWarning - Attempt 0
            2022-08-13 18:02:24,311 - root - WARNING - 2022-08-13 18:02:24.311076 - get_token_info - Attempt 0
            2022-08-13 18:02:29,393 - root - WARNING - 2022-08-13 18:02:29.393402 - get_token_symbol - Attempt 0
            2022-08-13 18:02:34,951 - root - WARNING - 2022-08-13 18:02:34.951341 - get_slippage - Attempt 0
            2022-08-13 18:02:40,580 - swap.klayswap - INFO - KLAY Get Slippage : None
            2022-08-13 18:02:40,580 - root - WARNING - 2022-08-13 18:02:40.580282 - confirm_slippage - Attempt 0
            2022-08-13 18:02:46,228 - swap.klayswap - INFO - KLAY Confirm Slippage : None
            2022-08-13 18:02:46,228 - swap.klayswap - INFO - KLAY Restore Swap : None
        ]
        """

        self.logger.info(f"KLAY Get Web : {self.get_web()}")
        self.logger.info(f"KLAY Get Wallet : {self.get_wallet()}")
        self.logger.info(f"KLAY Restore Swap : {self.restore_swap()}")

    def get_wallet(self):
        """
        get wallet for the first time in a specific swap site
        """

        self.logger.info(f"Connect Wallet : {self.connect_wallet()}")
        self.logger.info(f"Create Wallet : {self.create_wallet()}")
        self.logger.info(f"Restore Wallet : {self.restore_wallet()}")
        self.logger.info(f"Reconnect Wallet : {self.reconnect_wallet()}")
        self.logger.info(f"Get wallet risk info : {self.get_walletRiskinfo()}")

    def get_swap(self, size, flip):
        """
        do swap in specific swap site and wallet with the gasfee information calculated
        :param str size : amount of order size to swap
        :param bool flip : True flipping a token from -> to , to -> from
        """

        try:
            self.logger.info(f"Get Swap Size : {self.get_swapSize(size,flip)}")
            self.logger.info(f"Get Swap Size Click : {self.get_swapSize_click()}")
            self.logger.info(f"Get Swap Info : {self.get_swapInfo()}")
            self.logger.info(f"Get Swap Info Click : {self.get_swapInfo_click()}")
            gasfee_info = self.get_swapWallet()
            self.logger.info(f"Get swap Wallet Fee : {gasfee_info}")
            self.logger.info(f"Get Swap Info Click : {self.get_swapWallet_click()}")

        except:
            if len(self.driver.window_handles) < 2:
                gasfee_info = False

            else:
                self.logger.info(f"Get Swap Info Click : {self.get_swapWallet_click()}")
                self.logger.info(f"Get Swap Info : {self.get_swapInfo()}")
                self.logger.info(f"Get Swap Info Click : {self.get_swapInfo_click()}")
                gasfee_info = self.get_swapWallet()
                self.logger.info(f"Get Swap Info Click : {self.get_swapWallet_click()}")

        time.sleep(self.retriesTime)

        return gasfee_info

    def restore_swap(self):
        """
        restore swap site for fail swap
        """

        self.retry_network()

        try:
            self.get_token_info(self.from_symbol)
            self.get_token_symbol(self.tokenA)

            try:
                self.get_riskWarning()

            except:
                pass

            time.sleep(self.retriesTime)

            self.get_token_info(self.to_symbol)

            self.get_token_symbol(self.tokenB)

            self.logger.info(f"KLAY Get Slippage : {self.get_slippage()}")
            self.logger.info(f"KLAY Confirm Slippage : {self.confirm_slippage()}")

        except:
            self.restore_swap()

    @retry
    def get_web(self):
        """
        get web after close kaikas wallet
        """

        klayswap = self.driver.get(self.swap_page)

        change_window_kaikas_ins = self.driver.switch_to.window(self.driver.window_handles[0])

        kaikas_close = self.driver.close()

        get_klayswap = self.get_klayswap()

    @retry
    def get_klayswap(self):
        """
        get klayswap window
        """
        klaswap_window = self.driver.switch_to.window(self.driver.window_handles[0])

    @retry
    def connect_wallet(self):
        """
        click connect wallet button
        """

        connect_wallet1 = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[contains(@class,"main-access-btn")]')
            )
        ).send_keys(Keys.ENTER)

        connect_kaikas1 = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(@id,"modals-container")]//li[contains(@class,"select-wallet-modal__service__row pointer")]',
                )
            )
        ).click()

    @retry
    def create_wallet(self):
        """
        input password and click button
        """

        change_window_kaikas_wallet1 = self.driver.switch_to.window(self.driver.window_handles[-1])

        create_password = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="create-password"]'))
        ).send_keys(self.password)

        confirm_password = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="confirm-password"]'))
        ).send_keys(self.password)

        click_button1 = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="btn-container"]/button[1]'))
        ).send_keys(Keys.ENTER)

    @retry
    def restore_wallet(self):
        """
        click restore button, input seed, click 4 button to finish process of wallet
        """
        back_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//ul[@class="tabs__list"]/li[2]'))
        ).click()

        # input_seed
        for i in range(1, 13):
            elem = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@class="input-grid"]/div[{i}]//input[1]')
                )
            )
            elem.send_keys(self.seed[i - 1])

        button1 = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@class="button btn-primary first-time-flow__button"]')
            )
        ).send_keys(Keys.ENTER)

        button2 = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="security-guide"]//button[1]'))
        )

        self.driver.execute_script("arguments[0].click();", button2)

        click_check1 = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="checkbox-icon"]'))
        ).click()

        button3 = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//button[@class="button btn-primary btn--large page-container__footer-button"]',
                )
            )
        ).send_keys(Keys.ENTER)

    @retry
    def reconnect_wallet(self):
        """
        click connect wallet button , kaikas wallet button
        """

        change_window_klayswap = self.driver.switch_to.window(self.driver.window_handles[0])

        connect_wallet2 = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[contains(@class,"main-access-btn")]')
            )
        ).send_keys(Keys.ENTER)

        connect_kaikas2 = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(@id,"modals-container")]//li[contains(@class,"select-wallet-modal__service__row pointer")]',
                )
            )
        ).click()

    def get_walletRiskinfo(self):
        """
        click wallet risk info button
        """

        click_check2 = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="modals-container"]/div/div/div[2]/div/div/section[4]/div[1]/div[1]',
                )
            )
        ).click()

        click_check1_button = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="modals-container"]/div[2]/div/div[2]/div/section/article/button',
                )
            )
        ).send_keys(Keys.ENTER)

        click_check3 = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="modals-container"]/div/div/div[2]/div/div/section[4]/div[2]/div[1]',
                )
            )
        ).click()

        click_check4 = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="about-risk-modal__disable__check"]')
            )
        ).click()

        click_button2 = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="modals-container"]/div/div/div[2]/div/div/section[6]/button')
            )
        ).click()

    @retry
    def get_slippage(self):
        """
        click slippage button in swap site, input size of slippage
        """
        click_slippage = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="pointer"]'))
        )

        self.driver.execute_script("arguments[0].click();", click_slippage)

        click_slippage_input = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="modals-container"]/div/div/div[2]/div/section/article[4]//input[1]',
                )
            )
        )

        input_slippage = click_slippage_input.send_keys(self.slippage)

    @retry
    def confirm_slippage(self):
        """
        click slippage confirm button
        """

        click_button = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="base-modal HandleSlippageModal"]//article[@class="gen-modal-submit-wrap"]/button',
                )
            )
        ).send_keys(Keys.ENTER)

        confirm_button = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="base-modal CommonWarningModal"]//button[@class="common-warning-modal__submit"]',
                )
            )
        ).send_keys(Keys.ENTER)

    @retry
    def click_asset(self):
        """
        click asset button in swap site for refresh network
        """

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//nav[contains(@class,"main-header__nav")]//li[1]')
            )
        ).click()

    @retry
    def click_swap(self):
        """
        click swap button in swap site for refresh network
        """

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//nav[contains(@class,"main-header__nav")]//li[2]/span')
            )
        ).click()

    @retry
    def retry_network(self):
        """
        refresh network
        """
        self.driver.get(self.swap_page)

        try:
            self.get_walletRiskinfo()
        except:
            pass

        self.click_asset()
        self.click_swap()

    @retry
    def get_riskWarning(self):
        """
        click when riskwarning occurred
        """

        # 3-1 안전 유의사항 존재할시 클릭
        click_check = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(@class,"base-modal SelectUnsafeTokenModal")]//div[contains(@class,"confirm-on-modal-option__check")]',
                )
            )
        ).click()

        click_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//article[contains(@class,"gen-modal-submit-wrap")]')
            )
        ).click()

    @retry
    def get_token_info(self, symbol):
        """
        click from or to symbol icon to enter symbol address input site
        :param int symbol : token location, (from -> 1 , to -> 3)
        """

        change_window_klayswap = self.driver.switch_to.window(self.driver.window_handles[0])

        click_from_icon = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//section[contains(@class,"exchange-swap-page")]/article[{symbol}]//div[contains(@class,"ic-wrap")]',
                )
            )
        )

        self.driver.execute_script("arguments[0].click();", click_from_icon)

    @retry
    def get_token_symbol(self, token):
        """
        input token symbol,click confirm button
        :param str token : token symbol or address ex) klay, ZEMIT, 0X9...
        """

        click_from_input2 = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@id,"modals-container")]//input[1]')
            )
        )

        click_from_input2.send_keys(token)

        click_token2 = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//section[contains(@class,"ps")]//div[1]'))
        )

        self.driver.execute_script("arguments[0].click();", click_token2)

    @retry
    def get_swapSize(self, size, flip):
        """
        click flip button or not , input size
        :param str size : amount of order size to swap
        :param bool flip : True flipping a token from -> to , to -> from
        """

        change_window_klayswap = self.driver.switch_to.window(self.driver.window_handles[0])

        if flip == True:
            click_from_swapinput1 = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '(//article[contains(@class,"exchange-value-input")])[2]//input[@class="md-input"]',
                    )
                )
            )

        else:
            click_from_swapinput1 = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//article[contains(@class,"exchange-value-input")]//input[@class="md-input"]',
                    )
                )
            )

        length = len(click_from_swapinput1.get_attribute("value"))
        click_from_swapinput1.send_keys(length * Keys.BACKSPACE)
        click_from_swapinput1.send_keys(size)

    @retry
    def get_swapSize_click(self):
        """
        click swap button in swap size
        if error occurred -> close last window
        """

        try:
            click_exchange = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="exchange-page"]/div/section[1]/div[2]/article[2]')
                )
            ).click()

        except:
            if len(self.driver.window_handles) == 2:
                change_window_kaikas_ins = self.driver.switch_to.window(
                    self.driver.window_handles[-1]
                )

                kaikas_close = self.driver.close()

            else:
                logging.warning("swap click 실패")
                print("swap click 실패")

    @retry
    def get_swapInfo(self):
        """
        get transaction info in a swap site
        """

        change_window_metamask_wallet = self.driver.switch_to.window(self.driver.window_handles[-1])

        self.transaction_info = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="modals-container"]/div/div/div[2]/div/div/div[3]')
            )
        ).get_attribute("textContent")

    @retry
    def get_swapInfo_click(self):
        """
        click confirm swap button in a swap site
        """

        click_swap_info = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="modals-container"]/div/div/div[2]/div/div/div[4]/button')
            )
        ).send_keys(Keys.ENTER)

    @retry
    def get_swapWallet(self):
        """
        get gasfee info in a wallet

        """

        change_window_metamask_wallet = self.driver.switch_to.window(self.driver.window_handles[-1])

        gasfee_info = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="fee-detail-row__discountedFee"]')
            )
        ).text

        logging.warning(f"KLAY GAS FEE : {gasfee_info}")

        return gasfee_info

    @retry
    def get_swapWallet_click(self):
        """
        click confirm button in a wallet
        """

        change_window_metamask_wallet = self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            click_kaikas_swap = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//button[@class="button btn-primary btn--large page-container__footer-button"]',
                    )
                )
            ).send_keys(Keys.ENTER)
            logging.warning("pass swap click method 1")
        except:
            print("klayswap swap try 1 fail")

            try:
                click_kaikas_swap = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/header/button[2]')
                    )
                )
                self.driver.execute_script("arguments[0].click();", click_kaikas_swap)
                logging.warning("pass swap click method 2")
            except:
                print("klayswap swap try 2 fail")

                try:
                    click_kaikas_swap = self.wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="app-content"]/div/div[2]/div/div[3]/header/button[2]',
                            )
                        )
                    ).click()
                    logging.warning("pass swap click method 3")
                except:
                    print("nothing accept")

        logging.warning("pass swap click method 1")

    @retry_quote
    def get_quoteData(self, size):
        """
        get klayswap token balance data
        """
        # 6

        self.driver.switch_to.window(self.driver.window_handles[0])

        click_from_swapinput1 = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '(//section[contains(@class, "exchange-swap-page")]//article[contains(@class,"exchange-value-input")][1])//div[@class="md-input-wrap"]/input[1]',
                )
            )
        )

        length = len(click_from_swapinput1.get_attribute("value"))
        click_from_swapinput1.send_keys(length * Keys.BACKSPACE)

        click_from_swapinput1.send_keys(size)

        token_info = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//article[contains(@class,"exchange-rate-and-pool-info")]')
            )
        ).get_attribute("textContent")

        result = defaultdict(lambda: [])

        # swap 결과값 정리
        tmps_klay = regex.split("[ \n]", token_info)

        result_klay = [tmp for tmp in tmps_klay if tmp != ""]

        result["Exchange_Rate_A"].append(f"{result_klay[4]}")
        result["Exchange_Rate_B"].append(f"{result_klay[7]}")
        result["Slippage"].append(f"{result_klay[result_klay.index('Slippage')+1]}")

        try:
            result["Fee"].append(
                f"{result_klay[result_klay.index('Fee')+1]+''.join(dict.fromkeys(result_klay[result_klay.index('Fee')+2]))}"
            )
            result["swap"].append("Klayswap")
        except:
            return False

        return result

    @retry
    def get_balance(self):
        """
        get balance of tokenA , tokenB
        return tuple : tokenA_balance, tokenB_balance ex) (' 50.596579 ', ' 98.555308 ')
        """

        change_window = self.driver.switch_to.window(self.driver.window_handles[0])

        tokenA_balance = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '(//span[@class = "pointer"])[2]'))
        ).get_attribute("textContent")

        tokenB_balance = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '(//span[@class="pointer"])[3]'))
        ).get_attribute("textContent")

        return float(tokenA_balance.replace(",", "")), float(tokenB_balance.replace(",", ""))

    @retry_quote
    def flip_token(self):
        """
        click flip button
        """

        flip_swap = self.driver.switch_to.window(self.driver.window_handles[0])

        click_flip = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//article[@class="exchange-center-icon"]//img')
            )
        )

        self.driver.execute_script("arguments[0].click();", click_flip)
