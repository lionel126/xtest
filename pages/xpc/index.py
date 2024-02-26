from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pages.base import Base
from config import XPC_BASE_URL
from utils.utils import parse_url

class XpcIndex(Base):

    locator_logo = (By.CSS_SELECTOR, 'a.logo.v-center')

    def load(self):
        self.driver.get(f'{XPC_BASE_URL}')
    
    def is_loaded(self):
        try:
            self.driver.find_element(*XpcIndex.locator_logo)
        except NoSuchElementException:
            return False
        
        if parse_url(self.driver.current_url) == f'{XPC_BASE_URL}/': return True
        return False