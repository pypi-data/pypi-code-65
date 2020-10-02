from selenium import webdriver
from time import sleep
import schedule
import datetime
import requests
from selenium.webdriver.common.keys import Keys

class Test:
    def __init__(self):
        self.driver = None
        
    def setupDriver(self):
        chrome_driver="C:\\Users\\kanut\\OneDrive\\Documents_KB\\python\\chrome_driver\\chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(chrome_driver, options=options)
        
    def run_web(self):
        
        self.driver.get("https://nsweb.tmd.go.th/#showMetars")
        sleep(10)
        self.driver.execute_script("window.open('https://nsweb.tmd.go.th/#showTAFs','new window')")
        self.driver.switch_to_window(self.driver.window_handles[1])
        sleep(10)
        self.driver.switch_to_window(self.driver.window_handles[0])
        
        
if __name__=='__main__':
    obj=Test()
    obj.setupDriver()
    obj.run_web()