import time
from selenium.webdriver.common.by import By
from pages.base import Base
from config import PASSPORT_BASE_URL, PIC


class PersonVerify(Base):
    locator_submit = By.CSS_SELECTOR, 'button[type="submit"]'
    locator_role_dropdown_box = By.CSS_SELECTOR, 'div#role'
    locator_role_list = By.CSS_SELECTOR, 'ul[role="listbox"] li'
    locator_desc = By.CSS_SELECTOR, 'textarea'
    locator_credential = By.CSS_SELECTOR, 'input#credential'
    locator_agree = By.CSS_SELECTOR, 'input#agree'

    def load(self):        
        self.driver.get(f'{PASSPORT_BASE_URL}/verify/person')

    def load_with_auth(self, auth):
        self.load()
        self.driver.delete_cookie('TEST-Authorization')
        self.driver.add_cookie({'name': 'TEST-Authorization', 'value': auth})
        self.load()

    def submit(self):
        self.driver.find_element(*PersonVerify.locator_submit).click()

    def is_role_null(self):
        # todo
        pass
    
    def is_desc_empty(self):
        # todo
        textarea = self.driver.find_element(*PersonVerify.locator_desc)
        return textarea.get_property("value") == ''

    def choose_role(self, idx=0):
        self.driver.find_element(*PersonVerify.locator_role_dropdown_box).click()
        time.sleep(1)
        self.driver.find_element(*PersonVerify.locator_role_list).click()

    def desc(self, description:str):
        textarea = self.driver.find_element(*PersonVerify.locator_desc)
        textarea.send_keys(description)

    def upload_credential(self):
        self.driver.find_element(*PersonVerify.locator_credential).send_keys(PIC)
        time.sleep(2)

    def agree(self):
        self.driver.find_element(*PersonVerify.locator_agree).click()