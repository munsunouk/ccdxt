from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import os
import urllib.request
from selenium import webdriver
from selenium.webdriver.edge.options import Options
# from selenium.webdriver.chrome.options import Options
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

class Metamask :
    
    def __init__(self, config_change: Optional[dict] = {}) -> None:
        
        super().__init__()

        config = {
            "mnemonic": ['security', 'curve', 'swallow', 'few', 'tilt', 'attract', 'donor', 'tuition', 'matter', 'place', 'spoon', 'major'],
            "password" : '11111111',
            "extension_path" : os.getcwd() + '/mars/crawler/base/install/metamask.crx',
            "extension_id" : 'nemfimihgejednjoaiegllipidnpkefe',
            "version" : '10.28.1'
        }
        
        config["extension_url"] = f"chrome-extension://{config['extension_id']}/home.html"
        config.update(config_change)

        self.mnemonic = config['mnemonic']
        self.password = config['password']

        self.extension_path = config['extension_path']

        self.extension_id = config['extension_id']
        self.extension_url = config["extension_url"]
        self.version = config['version']
                            

    def downloadMetamaskExtension(self):
        print('Setting up metamask extension please wait...')

        url = f'https://chrome-stats.com/api/download?id={self.extension_id}&type=CRX&version={self.version}'
        urllib.request.urlretrieve(url, os.getcwd() + '/install/metamaskExtension.crx')


    def metamaskSetup(self, driver, wait):
        
        driver.maximize_window()
        
        handles_value = driver.window_handles
        if len(handles_value) > 1:
            driver.switch_to.window(driver.window_handles[1])

        driver.get(f"{self.extension_url}#onboarding/welcome")

        time.sleep(15)
        
        # time.sleep(1800) # test
        
        # wait.until(EC.presence_of_element_located((By.XPATH,'//*[@class="onboarding-welcome__buttons"]/li[2]/button'))).send_keys(Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div/ul/li[2]'))).click()
        # driver.find_element(By.XPATH, '//button[text()="Import an existing wallet"]').click() # import 
        # driver.find_element('xpath', '/html/body/div[1]/div/div[2]/div/div/div/ul/li[2]/button').click() # import 
        time.sleep(0.1)
        driver.find_element(By.XPATH, '//button[text()="No thanks"]').click()

        time.sleep(0.1)
        inputs = driver.find_elements(By.XPATH, '//input')
        for i, x in enumerate(self.mnemonic):
            if i == 0:
                locate_input = i
            else:
                locate_input = i * 2
            phrase = self.mnemonic[i]
            inputs[locate_input].send_keys(phrase)

        driver.find_element(By.XPATH, '//button[text()="Confirm Secret Recovery Phrase"]').click()
        time.sleep(0.1)

        inputs = driver.find_elements(By.XPATH, '//input')
        inputs[0].send_keys(self.password)
        inputs[1].send_keys(self.password)
        driver.find_element(By.CSS_SELECTOR, '.create-password__form__terms-label').click()
        driver.find_element(By.XPATH, '//button[text()="Import my wallet"]').click()

        time.sleep(1)
        driver.find_element(By.XPATH, '//button[text()="Got it!"]').click()
        time.sleep(0.1)
        driver.find_element(By.XPATH, '//button[text()="Next"]').click()
        time.sleep(0.1)
        driver.find_element(By.XPATH, '//button[text()="Done"]').click()
        time.sleep(1)

        print("Wallet has been imported successfully")
        driver.switch_to.window(driver.window_handles[0])


    # def changeMetamaskNetwork(self, networkName):
    #     # opening network
        
    #     #TODO
    #     #self.host 일때 private node 연결 
        
    #     print("Changing network")
    #     driver.switch_to.window(driver.window_handles[1])
    #     driver.get('chrome-extension://{}/home.html'.format(self.extension_id))
    #     print("closing popup")
    #     time.sleep(5)
    #     driver.find_element_by_xpath('//*[@id="popover-content"]/div/div/section/header/div/button').click()

    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
    #     time.sleep(2)
    #     print("opening network dropdown")
    #     elem = driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div')
    #     time.sleep(2)
    #     all_li = elem.find_elements_by_tag_name("li")
    #     time.sleep(2)
    #     for li in all_li:
    #         text = li.text
    #         if (text == networkName):
    #             li.click()
    #             print(text, "is selected")
    #             time.sleep(2)
    #             driver.switch_to.window(driver.window_handles[0])
    #             time.sleep(3)
    #             return
    #     time.sleep(2)
    #     print("Please provide a valid network name")

    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)


    # def connectToWebsite(self):
    #     time.sleep(3)

    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(5)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(3)
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]').click()
    #     time.sleep(1)
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    #     time.sleep(3)
    #     print('Site connected to metamask')
    #     print(driver.window_handles)
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)


    # def confirmApprovalFromMetamask(self):
    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(10)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(10)
    #     # confirm approval from metamask
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]').click()
    #     time.sleep(12)
    #     print("Approval transaction confirmed")

    #     # switch to dafi
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)


    # def rejectApprovalFromMetamask(self):
    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(10)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(10)
    #     # confirm approval from metamask
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[1]').click()
    #     time.sleep(8)
    #     print("Approval transaction rejected")

    #     # switch to dafi
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)
    #     print("Reject approval from metamask")


    # def confirmTransactionFromMetamask(self):
    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(10)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(10)

    #     # # confirm transaction from metamask
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[3]/div[3]/footer/button[2]').click()
    #     time.sleep(13)
    #     print("Transaction confirmed")

    #     # switch to dafi
    #     driver.switch_to.window(driver.window_handles[0])

    #     time.sleep(3)


    # def rejectTransactionFromMetamask(self):
    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(5)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(5)
    #     # confirm approval from metamask
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[3]/div[3]/footer/button[1]').click()
    #     time.sleep(2)
    #     print("Transaction rejected")

    #     # switch to web window
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)

    # def addToken(self, tokenAddress):
    #     # opening network
    #     print("Adding Token")
    #     driver.switch_to.window(driver.window_handles[1])
    #     driver.get('chrome-extension://{}/home.html'.format(self.extension_path))
    #     print("closing popup")
    #     time.sleep(5)
    #     driver.find_element_by_xpath('//*[@id="popover-content"]/div/div/section/header/div/button').click()

    #     # driver.find_element_by_xpath('//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
    #     # time.sleep(2)

    #     print("clicking add token button")
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[4]/div/div/div/div[3]/div/div[3]/button').click()
    #     time.sleep(2)
    #     # adding address
    #     driver.find_element_by_id("custom-address").send_keys(tokenAddress)
    #     time.sleep(10)
    #     # clicking add
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[4]/div/div[2]/div[2]/footer/button[2]').click()
    #     time.sleep(2)
    #     # add tokens
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[4]/div/div[3]/footer/button[2]').click()
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)

    # def signConfirm(self):
    #     print("sign")
    #     time.sleep(3)

    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(5)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(3)
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]').click()
    #     time.sleep(1)
    #     # driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    #     # time.sleep(3)
    #     print('Sign confirmed')
    #     print(driver.window_handles)
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)


    # def signReject(self):
    #     print("sign")
    #     time.sleep(3)

    #     driver.execute_script("window.open('');")
    #     driver.switch_to.window(driver.window_handles[1])

    #     driver.get('chrome-extension://{}/popup.html'.format(self.extension_path))
    #     time.sleep(5)
    #     driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    #     time.sleep(3)
    #     driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[3]/button[1]').click()
    #     time.sleep(1)
    #     # driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    #     # time.sleep(3)
    #     print('Sign rejected')
    #     print(driver.window_handles)
    #     driver.switch_to.window(driver.window_handles[0])
    #     time.sleep(3)