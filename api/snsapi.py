import time, copy
from requests import request
from api.user_center import Sess
from config import XPC_BASE_URL, COOKIE_AUTH, COOKIE_DEVICE_ID
from utils.utils import replace, append

class Xpc():
    
    URL_APPLY_TEAM_MEMBER = f'{XPC_BASE_URL}/article/team/ts-apply'
    URL_AGREE_TEAM_APPLICATION = f'{XPC_BASE_URL}/article/team/ts-oprate'
    URL_QUIT_TEAM = f'{XPC_BASE_URL}/user/space/ts-quit'
    URL_ARTICLE = f'{XPC_BASE_URL}/a{{}}'

    
    def __init__(self, phone='', password='999999', code='+86', app_session=None):
        '''同步xpcapi session
        todo: header class, not a dict; case sensitive
        '''
        # print(xpc_session.headers)
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        self.cookies = {
            'PHPSESSID': f'phpsessionid{time.time()}'
        }
        if app_session and hasattr(app_session, 'headers'):
            if 'authorization' in app_session.headers:
                self.cookies[COOKIE_AUTH] = app_session.headers['authorization']
            if 'device-id' in app_session.headers:
                self.cookies[COOKIE_DEVICE_ID] = app_session.headers['device-id']
        if phone:
            self.login(phone, password=password, code=code)                
        # print(self.cookies)

    def login(self, phone, password='999999', code='+86'):
        ''' todo: passport login
        '''
        j = {
            "type": "phone",
            "regionCode": code,
            "phone": phone,
            "password": password
        }
        s = Sess()
        self.session = s
        r = s.login(json=j)
        self.cookies[COOKIE_AUTH] = r.headers['set-authorization']
        self.cookies[COOKIE_DEVICE_ID] = s.headers['device-no']
    
    def logout(self):
        '''todo: passport logout'''
        self.session.logout()
        
    def apply_team_member(self, method='POST', headers=None, cookies=None, data=None, **kwargs):
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if cookies is None:
            cookies = self.cookies
        if data is None: 
            data = {
                'articleid': 0,
                'role[]': 55
            }
        replace(kwargs, data, cookies)
        return request(method, url=Xpc.URL_APPLY_TEAM_MEMBER, headers=headers, cookies=cookies, data=data)
    
    def quit_team(self, method='POST', cookies=None, data=None, **kwargs):
        if cookies is None:
            cookies = self.cookies
        if data is None: 
            data = {
                'id': 0,
                'audit': 0
            }
        replace(kwargs, data, cookies)
        return request(method, url=Xpc.URL_QUIT_TEAM, cookies=cookies, data=data)
    
    def agree_application_for_team_member(self, method='POST', data=None, cookies=None, **kwargs):
        if cookies is None:
            cookies = self.cookies
        if data is None: 
            data={
                "op":1,
                "id":88585,
                "type":1
            }
        replace(kwargs, data, cookies)
        return request(method, url=Xpc.URL_AGREE_TEAM_APPLICATION, cookies=cookies, data=data)

    def article(self, article_id, method='GET', cookies=None):
        if cookies is None:
            cookies = self.cookies
        return request(method, url=Xpc.URL_ARTICLE.format(article_id), cookies=cookies)
