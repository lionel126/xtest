import re, pytest
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from pages.base import Base
from utils.utils import parse_url
from config import XPC_BASE_URL

class Article(Base):
    
    locator_download = (By.CSS_SELECTOR, 'a#article-page-download-btn')
    
    # 下载列表弹窗
    locator_download_dialog = (By.CSS_SELECTOR, 'div.open-list')
    locator_dialog_title = (By.CSS_SELECTOR, 'div.open-list div.open-list-top > span.open-list-dl')
    
    # 赞赏下载 title
    # locator_reward_title = (By.CSS_SELECTOR, 'div.open-list li.apply-download-title > p > span')
    locator_reward_title = (By.CSS_SELECTOR, 'div.open-list li.apply-download-title')
    # 赞赏下载项
    locator_reward_item = (By.CSS_SELECTOR, 'div.open-list li.list-item.apply-download-item')
    # locator_reward_item_title = (By.CSS_SELECTOR, 'div.open-list span.download-title.border-btn')
    # locator_reward_item_btn = (By.CSS_SELECTOR, 'div.open-list span:is(.reward-btn, .reward-download-btn)')
    locator_reward_item_reward_btn = (By.CSS_SELECTOR, 'span.reward')

    # # 其他下载列表(除了 赞赏下载)
    # locator_download_list = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box')
    # non-vip title
    locator_non_vip_title = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type:not(.vip):not(.svip)')
    # non-vip下载项 
    locator_non_vip_download_items = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type:not(.vip):not(.svip) + ul > li.list-item')
    # 普通会员 title
    locator_vip_title = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.vip')
    # vip下载项 
    locator_vip_download_items = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.vip + ul > li.list-item')

    # 超级会员 title
    locator_svip_title = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.svip')    
    # svip下载项 
    locator_svip_download_items = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.svip + ul > li.list-item')
    
    # 下载项 title 相对
    locator_item_title = (By.CSS_SELECTOR, 'span.download-title.border-btn')
    # 下载项 button 相对
    locator_item_btn = (By.CSS_SELECTOR, 'div > span.download-btn')
    # # # 非vip下载按钮
    # # locator_item_non_vip_download = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.vip + ul > li.list_item > span.download-btn:not(.vip-download-btn):not(.svip-download-btn)')
    # # # vip下载按钮  模版
    # locator_item_vip_download = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.vip + ul > li.list-item:nth-child({}) span.download-btn.vip-download-btn')
    # # svip下载按钮
    # locator_item_svip_download = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.svip + ul > li.list-item:nth-child({}) span.download-btn.vip-download-btn')
    # # 非vip下载按钮
    # locator_item_non_vip_download = (By.CSS_SELECTOR, 'span.download-btn:not(.vip-download-btn):not(.svip-download-btn)')
    
    locator_download_auth = (By.CSS_SELECTOR, 'div.open-list li.download-authorization')

    icons = {
        'https://oss-xpc0.xpccdn.com/Upload/edu/2022/06/1562a97840cd768.svg': 'vip', 
        'https://oss-xpc0.xpccdn.com/Upload/edu/2022/06/1562a9789ce9634.svg': 'svip'
    }

    locator_download_auth = (By.CSS_SELECTOR, 'li.download-authorization')

    def load(self, article_id):
        self.driver.get(f'{XPC_BASE_URL}/a{article_id}')
    
    def is_loaded(self):
        r = re.compile(fr'{XPC_BASE_URL}/a(\d{{1,8}})$').match(parse_url(self.driver.current_url))
        if r:
            self.article_id = r.group(1)
            return True
        return False

    def open_download_dialog(self):
        '''
        '''
        self.driver.find_element(*Article.locator_download).click()
        

    def display_none(self, *elems:WebElement) -> bool:
        '''
        return if class include "dn"
        '''
        return ['dn' in elem.get_attribute('class').split() for elem in elems]
        # return elem.value_of_css_property('display') is None

    def get_reward_download_data(self):
        reward_title = self.driver.find_element(*Article.locator_reward_title)
        reward_item = self.driver.find_element(*Article.locator_reward_item)
        reward_title_dn, reward_item_dn = self.display_none(reward_title, reward_item)
        assert reward_title_dn == reward_item_dn
        reward_item_title = self.driver.find_element(*Article.locator_item_title)
        reward_item_btn = self.driver.find_element(*Article.locator_item_btn)
        # print(reward_title.text)
        # print(reward_item_title.text, reward_item_btn.text)
        d = {'title': reward_title.text}
        d['display'] = not reward_item_dn
        d['data']= [{'title': reward_item_title.text, 'button': reward_item_btn.text}]
        # print('-' * 20)
        return d

    def get_download_data_by_type(self, typ:str):
        '''vip/svip/non-vip
        '''
        if typ == 'vip':
            locator_title = Article.locator_vip_title
            locator_items = Article.locator_vip_download_items
        elif typ == 'svip':
            locator_title = Article.locator_svip_title
            locator_items = Article.locator_svip_download_items
        elif typ == 'non-vip':
            locator_title = Article.locator_non_vip_title
            locator_items = Article.locator_non_vip_download_items
        else:
            raise Exception(f'unknow type: {typ}')
        try:
            title = self.driver.find_element(*locator_title)
        except NoSuchElementException:
            assert len(self.driver.find_elements(*locator_items)) == 0
            d = {'display': False}
        else:
            d = {'title': title.text, 'display': True, 'data': []}
            download_items = self.driver.find_elements(*locator_items)
            for download_item in download_items:
                download_item_title = download_item.find_element(*Article.locator_item_title)
                
                # icon = self.driver.execute_script(f"return window.getComputedStyle(document.querySelector('{Article.locator_item_vip_download[1]}'),':before').getPropertyValue('background-image');")
                # icon = self.get_computed_style(Article.locator_item_vip_download[1].format(idx+1), ':before', 'background-image')
                icon = self.get_computed_style(download_item.find_element(*Article.locator_item_btn), ':before', 'background-image') 
                          
                d['data'].append({
                    'title': download_item_title.text,
                    'icon': Article.icons[icon[5:-2]] if icon != 'none' else None
                })
        return d


    def get_download_list(self):
        '''
        '''
        result = {}
        
        dialog = WebDriverWait(self.driver, 2).until(ec.visibility_of(self.driver.find_element(*Article.locator_download_dialog)))
        title = dialog.find_element(*Article.locator_dialog_title)
        result['title'] = title.text
        
        result['reward'] = self.get_reward_download_data()
        result['non-vip'] = self.get_download_data_by_type('non-vip')
        result['vip'] = self.get_download_data_by_type('vip')
        result['svip'] = self.get_download_data_by_type('svip')
        
        try:
            auth = dialog.find_element(*Article.locator_download_auth)
            result['auth'] = {'display': True}
            classes = [c for c in auth.find_element(By.CSS_SELECTOR, 'i').get_attribute('class').split() if 'icon-authorization' in c]
            result['auth']['type'] = classes[0][-1]
        except NoSuchElementException:
            result['auth'] = {'display': False}
        

        print(result)
        return result

    
    
