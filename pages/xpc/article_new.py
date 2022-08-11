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
    
    locator_download = (By.CSS_SELECTOR, 'button[aria-label="下载"]')
    
    # 下载列表弹窗
    locator_download_dialog = (By.CSS_SELECTOR, 'div[id^="headlessui-dialog-panel-:"]')
    locator_dialog_title = (By.CSS_SELECTOR, 'div[id^="headlessui-dialog-panel-:"] > div.relative > h2')
    
    # 赞赏下载 title
    # locator_reward_title = (By.CSS_SELECTOR, 'div.open-list li.apply-download-title > p > span')
    locator_reward_title = (By.XPATH, '//span[text()="赞赏下载"]/parent::h3')
    # 赞赏下载项
    locator_reward_item = (By.XPATH, '//span[text()="赞赏下载"]/parent::h3/parent::div/div/div')
    # locator_reward_item_title = (By.CSS_SELECTOR, 'div.open-list span.download-title.border-btn')
    # locator_reward_item_btn = (By.CSS_SELECTOR, 'div.open-list span:is(.reward-btn, .reward-download-btn)')
    locator_reward_item_reward_btn = (By.CSS_SELECTOR, 'span.reward')

    # # 其他下载列表(除了 赞赏下载)
    # locator_download_list = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box')
    # team title
    locator_team_title = (By.XPATH, '//span[text()="支持下载"]/parent::div/parent::h3')
    # team下载项 
    locator_team_download_items = (By.XPATH, '//span[text()="支持下载"]/parent::div/parent::h3/parent::div/div/div')
    # 普通会员 title
    locator_vip_title = (By.XPATH, '//span[text()="会员支持下载"]/parent::div/parent::h3')
    # vip下载项 
    locator_vip_download_items = (By.XPATH, '//span[text()="会员支持下载"]/parent::div/parent::h3/parent::div/div/div')

    # 超级会员 title
    locator_svip_title = (By.XPATH, '//span[text()="超级会员支持下载"]/parent::div/parent::h3')   
    # svip下载项 
    locator_svip_download_items = (By.XPATH, '//span[text()="超级会员支持下载"]/parent::div/parent::h3/parent::div/div/div')
    
    # 下载项 title 相对
    locator_item_title = (By.CSS_SELECTOR, 'span')
    # 下载项 button 相对
    locator_item_btn = (By.CSS_SELECTOR, 'button')
    locator_icon_vip = (By.CSS_SELECTOR, 'div > button > span > span')
    # # # 非vip下载按钮
    # # locator_item_non_vip_download = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.vip + ul > li.list_item > span.download-btn:not(.vip-download-btn):not(.svip-download-btn)')
    # # # vip下载按钮  模版
    # locator_item_vip_download = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.vip + ul > li.list-item:nth-child({}) span.download-btn.vip-download-btn')
    # # svip下载按钮
    # locator_item_svip_download = (By.CSS_SELECTOR, 'div.open-list div.open-list-detail-box p.downloadlist-type.svip + ul > li.list-item:nth-child({}) span.download-btn.vip-download-btn')
    # # 非vip下载按钮
    # locator_item_non_vip_download = (By.CSS_SELECTOR, 'span.download-btn:not(.vip-download-btn):not(.svip-download-btn)')
    
    
    locator_download_auth = (By.CSS_SELECTOR, 'div[id^="headlessui-dialog-panel-:"] > div > section > div > div:nth-child(2)')

    # locator_vip_only = (By.XPATH, '//div[starts-with(@aria-labelledby, "headlessui-dialog-title")]//h3[starts-with(@id, "headlessui-dialog-title")]')
    locator_vip_only = (By.CSS_SELECTOR, 'div[aria-labelledby^="headlessui-dialog-title"] h3[id^="headlessui-dialog-title"]')
    locator_vip_dialog_x = (By.CSS_SELECTOR, 'div[aria-labelledby^="headlessui-dialog-title"] button > svg > path')

    # icons = {
    #     'https://oss-xpc0.xpccdn.com/Upload/edu/2022/06/1562a97840cd768.svg': 'vip', 
    #     'https://oss-xpc0.xpccdn.com/Upload/edu/2022/06/1562a9789ce9634.svg': 'svip'
    # }

    

    def load(self, article_id, new_article='true', **kwargs):
        url = f'{XPC_BASE_URL}/a{article_id}'
        kwargs.update(new_article=new_article)
        if kwargs:
            param = '&'.join([f'{k}={v}' for k,v in kwargs.items()])
            url = f'{url}?{param}'
        self.driver.get(url)
    
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
        

    # def display_none(self, *elems:WebElement) -> bool:
    #     '''
    #     return if class include "dn"
    #     '''
    #     return ['dn' in elem.get_attribute('class').split() for elem in elems]
    #     # return elem.value_of_css_property('display') is None

    def get_reward_download_data(self):
        d = {}
        try:
            reward_title = self.driver.find_element(*Article.locator_reward_title)
        except NoSuchElementException:
            with pytest.raises(NoSuchElementException):
                self.driver.find_element(*Article.locator_reward_item)
            d['display'] = False
        else:
            reward_item = self.driver.find_element(*Article.locator_reward_item)
            # reward_title_dn, reward_item_dn = self.display_none(reward_title, reward_item)
            # assert reward_title_dn == reward_item_dn
            reward_item_title = reward_item.find_element(*Article.locator_item_title)
            reward_item_btn = reward_item.find_element(*Article.locator_item_btn)
            # print(reward_title.text)
            # print(reward_item_title.text, reward_item_btn.text)
            d['title'] = reward_title.text
            d['display'] = True
            d['data']= [{'title': reward_item_title.text, 'button': reward_item_btn.text}]
            # print('-' * 20)
        return d

    def get_download_data_by_type(self, typ:str):
        '''vip/svip/team
        '''
        if typ == 'vip':
            locator_title = Article.locator_vip_title
            locator_items = Article.locator_vip_download_items
        elif typ == 'svip':
            locator_title = Article.locator_svip_title
            locator_items = Article.locator_svip_download_items
        elif typ == 'team':
            locator_title = Article.locator_team_title
            locator_items = Article.locator_team_download_items
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
                # icon = self.get_computed_style(download_item.find_element(*Article.locator_item_btn), ':before', 'background-image') 
                
                try:
                    icon = download_item.find_element(*Article.locator_icon_vip)
                except NoSuchElementException:
                    icon = None
                          
                d['data'].append({
                    'title': download_item_title.text,
                    'icon': icon.text if icon else None
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
        result['team'] = self.get_download_data_by_type('team')
        result['vip'] = self.get_download_data_by_type('vip')
        result['svip'] = self.get_download_data_by_type('svip')
        
        try:
            auth = dialog.find_element(*Article.locator_download_auth)
            result['auth'] = {'display': True}
            # classes = [c for c in auth.find_element(By.CSS_SELECTOR, 'i').get_attribute('class').split() if 'icon-authorization' in c]
            # result['auth']['type'] = classes[0][-1]
        except NoSuchElementException:
            result['auth'] = {'display': False}
        

        print(result)
        return result

    def click_download_btn(self, profile, type='team'):
        if type == 'team':
            locator = Article.locator_team_download_items
        elif type == 'vip':
            locator = Article.locator_vip_download_items
        elif type == 'svip':
            locator = Article.locator_svip_download_items
        else: # type == 'reward'
            locator = Article.locator_reward_item
        its = self.driver.find_elements(*locator)
        for it in its:
            if profile in it.text:
                it.find_element(*Article.locator_item_btn).click()
                return 
        raise NoSuchElementException

    def get_vip_only_dialog(self):
        '''
        todo:
        '''
        title = self.driver.find_element(*Article.locator_vip_only)
        return {'title': title.text}

    def close_vip_dialog(self):
        self.driver.find_element(*Article.locator_vip_dialog_x).click()
