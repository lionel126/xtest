from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from pages.base import Base
from pages.xpc.index import XpcIndex
from config import XPC_BASE_URL
from utils.utils import parse_url


class Login(Base):

    locator_phone = (By.CSS_SELECTOR, 'input#login_phone')
    locator_password = (By.CSS_SELECTOR, 'input#login_password')
    locator_login = (By.CSS_SELECTOR, 'button[type="submit"]')
    locator_tabs = (By.CSS_SELECTOR, 'div.ant-tabs-nav-wrap div[role="tab"]')

    def load(self, type=''):
        
        params = f'?type={type}' if type else ''
        self.driver.get(f'{XPC_BASE_URL}/login{params}')
    
    def is_loaded(self):
        assert parse_url(self.driver.current_url) == f'{XPC_BASE_URL}/login'

    def switch_tab(self):
        '''
        '''

    def login(self, phone='', password='999999', code='+86', redirect_page:Base=XpcIndex) -> XpcIndex:
        self.driver.find_element(*Login.locator_tabs).click()
        if phone:
            self.driver.find_element(*Login.locator_phone).send_keys(phone)
        if password:
            self.driver.find_element(*Login.locator_password).send_keys(password)
        self.driver.find_element(*Login.locator_login).click()
        
        if redirect_page:
            page = redirect_page(self.driver)
            WebDriverWait(self.driver, 10).until(lambda d: page.is_loaded())
            return page