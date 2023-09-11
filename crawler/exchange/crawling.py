from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from mars.base.utils.retry import retry_normal
import time
import os
import logging

# from mars.crawler.wallet import Metamask

class Crawling :
    
    def __init__(self) -> None:
        
        self.language = 'en-US'
        self.driver_name = 'chrome'
        self.timeout = 25
        self.agent = "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        
        self.driver_path = os.getcwd() + '/mars/crawler/base/install/chromedriver.exe' #chrome
    
    def load_crawling(self) :
        
        # self.get_wallet()
        self.launchSeleniumWebdriver()
        # self.set_wallet()
        # self.set_site()
    
    def launchSeleniumWebdriver(self):
        
        if self.driver_name == 'chrome' :
        
            options = webdriver.ChromeOptions()
            
        elif self.driver_name == 'edge' :
            
            options = Options()

        options.add_argument('--no-sandbox') # resource access
        options.add_argument('--disable-dev-shm-usage') # stop error by memory
        options.add_argument('--disable-setuid-sandbo') # stop crush chrome
        options.add_argument(self.agent) # for not being catched as bot
        # options.add_argument("lang=ko_KR") # for korea site
        options.add_argument(f"--lang={self.language}")
        options.add_experimental_option('prefs', {
            'intl.accept_languages': f'{self.language}'
        })
        # options.add_extension(self.wallet.extension_path) # wallet extension
        # options.add_argument("--app-id = nkbihfbeogaeaoehlefnkodbefgpgknn")

        self.get_driver_path()

        service = Service(executable_path=self.driver_path)

        self.driver = webdriver.Chrome(service=service, options=options)

        self.wait = WebDriverWait(driver=self.driver, timeout=self.timeout)
        
    def checkHandles(self) -> None:
        handles_value = self.driver.window_handles
        if len(handles_value) > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.checkHandles()
            
    def get_driver_path(self) :
        
        if not self.driver_path :
            
            self.driver_path = ChromeDriverManager().install()
        
    # def get_wallet(self) :
        
    #     self.wallet = eval(self.wallet_name + f"({self.wallet_config})")
        
    # def set_wallet(self) :
    
    #     self.wallet.metamaskSetup(self.driver, self.wait)

    def set_site(self, configs=[]) :

        if configs :

            full_params = ''
            
            for config in configs :
            
                params = config[0]+config[0].join('{}={}'.format(k, config[1][k]) for k in sorted(config[1]))
                
                full_params += params
            
        else :
            
            full_params = ''

        full_site = self.markets['info'] + full_params

        self.driver.get(full_site)
        
    @retry_normal
    def test_liama_hide_ip(self) :
        
        time.sleep(25)
        
        # self.wait.until(EC.presence_of_element_located((By.XPATH,'//input[@class="chakra-switch__input'))).send_keys(Keys.ENTER)
        
        result = self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="privacy-switch"]'))).send_keys(Keys.ENTER)
        
        return result
        
    @retry_normal
    def click_liama_hide_ip(self) :
        
        link = '//*[@id="__next"]/div/div/div[2]/main/div[2]/div[1]/div[1]/div[1]/div/div/button/div/label[2]/span'

        self.wait.until(EC.presence_of_element_located((By.XPATH, link))).click()
    
    
    def reset_input(self, length, input) :

        for _ in range(len(length)) :
        
            input.send_keys(Keys.BACKSPACE)
            
        input.clear()
        
        return input
    
    @retry_normal
    def input_liama_size(self, size) :
        
        link = '//*[@id="__next"]/div/div/div[2]/main/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div/input'
        
        link_located = self.wait.until(EC.presence_of_element_located((By.XPATH, link)))
        
        input = link_located.get_attribute('placeholder')
        
        link_located = self.reset_input(input, link_located)
        
        link_located.send_keys(size)
        
        time.sleep(5)
        
        while True :
            
            link_located = self.wait.until(EC.presence_of_element_located((By.XPATH, link)))
            
            input = link_located.get_attribute('placeholder')
            
            logging.info(float(input))

            if float(input) != size :
                
                link_located = self.reset_input(input, link_located)
                
                link_located.send_keys(size)
                
                time.sleep(5)
                
            else :
                
                break
                
        time.sleep(5)   
            
    @retry_normal
    def click_liama_perform_reload(self) :
        
        link = '//*[@id="__next"]/div/div/div[2]/main/div[2]/div[1]/div[2]/div[1]/div[2]/button'
        
        self.wait.until(EC.presence_of_element_located((By.XPATH, link))).click()
        
        time.sleep(5)
        
    @retry_normal
    def click_liama_perform_route(self) :
        
        link = '//*[@id="__next"]/div/div/div[2]/main/div[2]/div[1]/div[2]'
        
        second_link = './/div[@class="sc-18d0abec-0 knYyMy RouteWrapper"]'
        
        parent_link_located = self.wait.until(EC.presence_of_element_located((By.XPATH, link)))
        
        child_divs_locator = (By.XPATH, second_link)
        child_divs = parent_link_located.find_elements(*child_divs_locator)
        
        child_div_text_lists = []

        for child_div in child_divs :
            
            child_div_text = child_div.text

            child_div_text_list = child_div_text.split()
            
            child_div_text_lists.append(child_div_text_list)
            
            logging.info(f"child_div_text_list : {child_div_text_list}")

        return child_div_text_lists