from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import config

class Base():
    def __init__(self, driver=None):
        '''
        '''
        if not driver:
            if hasattr(config, 'LOCAL_CHROME') and config.LOCAL_CHROME:
                # # disable http_proxy for local chrome 
                service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                self.driver = webdriver.Chrome(service=service)
            else:
                options = webdriver.ChromeOptions()
                self.driver = webdriver.Remote('http://192.168.3.89:4444', options=options)
        else:
            self.driver = driver

    def get_computed_style(self, elem, pseudo, prop):
        '''
        return window.getComputedStyle(document.querySelector('.okButton'),':after').getPropertyValue('content');
        '''
        # script = "return window.getComputedStyle(document.querySelector('{}'),'{}').getPropertyValue('{}');".format(css_selector, pseudo, prop)
        script = "return window.getComputedStyle(arguments[0],'{}').getPropertyValue('{}');".format(pseudo, prop)
        # print(script)
        return self.driver.execute_script(script, elem)

    
