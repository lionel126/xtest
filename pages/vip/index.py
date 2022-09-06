from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base import Base
from config import VIP_BASE_URL


class Index(Base):

    locator_v_general_month_subscribe = (By.CSS_SELECTOR, 'a[data-sku="v_general_month_subscribe"]')

    locator_vip_submit = (By.CSS_SELECTOR, 'button.pay-order-btn[data-type="vip"]')

    locator_payment_layer_popup = (By.CSS_SELECTOR, 'div.payment-layer-popup')

    def load(self):
        self.driver.get(VIP_BASE_URL)

    def order(self, sku="v_general_month_subscribe"):

        self.driver.find_element(*getattr(Index, f'locator_{sku}')).click()
        self.driver.find_element(*Index.locator_vip_submit).click()

    def save_qr_screenshot(self):
        wait = WebDriverWait(self.driver, 10)

        popup = wait.until(EC.visibility_of_element_located(Index.locator_payment_layer_popup))
        popup.find_element(By.CSS_SELECTOR, 'img').screenshot('tmp/qr.png')