import json as js
from requests import request
from config import XPC_API_BASE_URL, COOKIE_DEVICE_ID, COOKIE_AUTH
from .user_center import Sess
from utils.utils import replace, append
from datetime import datetime as dt



class XpcApi():
    '''
    '''
    URL_FOLLOW = f'{XPC_API_BASE_URL}/user/{{}}/follow'

    URL_UPLOAD_CHECK_PARAMS = f'{XPC_API_BASE_URL}/v2/article/checkParams'
    URL_UPLOAD_PREPARE = f'{XPC_API_BASE_URL}/v2/upload/prepare'
    URL_UPLOAD_COMPLETE = f'{XPC_API_BASE_URL}/v2/upload/complete'
    URL_AUDIT_ARTICLES = f'{XPC_API_BASE_URL}/v2/user/auditArticles'
    URL_EDIT_ARTICLE = f'{XPC_API_BASE_URL}/v2/article/{{}}'

    URL_PRIVATE_SPACE_CHECK = f'{XPC_API_BASE_URL}/v2/privateVideo/space/check'
    URL_SEARCH_AUTH = f'{XPC_API_BASE_URL}/v2/search/auth'

    URL_IM_QUOTA = f'{XPC_API_BASE_URL}/message/im/quota'
    URL_CREATORS_AUTH = f'{XPC_API_BASE_URL}/creators/auth'
    URL_ALLOW_COMMENT = f'{XPC_API_BASE_URL}/article/{{}}/allow_comment'

    URL_DOWNLOAD_VIDEO_LIST = f'{XPC_API_BASE_URL}/article/{{}}/download_video_list'
    URL_DOWNLOAD_URL = f'{XPC_API_BASE_URL}/article/{{}}/get_download_url'
    URL_DOWNLOAD_BY_TOKEN = f'{XPC_API_BASE_URL}/article/get_download_url_by_token'
    URL_CHECK_DOWNLOAD_PERMISSION = f'{XPC_API_BASE_URL}/article/{{}}/check_download_transcoded_video_permission'
    URL_ARTICLE_SHARE = f'{XPC_API_BASE_URL}/article/{{}}/share'

    URL_CREATE_REWARD_ORDER = f'{XPC_API_BASE_URL}/v2/article/createRewardDownloadTrade'


    def __init__(self, phone='', password='999999', code='+86', sns_session=None):
        self.headers={'user-agent': 'NewStudios/2.0.5 (com.xinpianchang.newstudios.enterprise; build:938; Android 7.1.2)'}
        if sns_session:
            self.headers['device-id'] = sns_session.cookies[COOKIE_DEVICE_ID]
            self.headers['authorization'] = sns_session.cookies[COOKIE_AUTH]
        if phone:
            self.login(phone, password, code)
        

        

    def login(self, phone, password='999999', code='+86'):
        j = {
            "type": "phone",
            "regionCode": code,
            "phone": phone,
            "password": password
        }
        s = Sess()
        self.session = s
        r = s.login(json=j)
        self.headers.update(s.headers)
        self.headers['device-id'] = s.headers['device-no']
        del self.headers['device-no']

    def logout(self):
        '''
        '''
        self.session.logout()

    def follow(self, user_id, method='POST', headers=None):
        if headers is None:
            headers = self.headers
        return request(
            method,
            XpcApi.URL_FOLLOW.format(user_id),
            headers=headers
        )

    def audit_articles(self, method='GET', headers=None, params=None, **kwargs):
        '''
        :param params: {"isPrivate":0, "pageSize": 100}
        '''
        if headers is None:
            headers = self.headers
        if params is None:
            params = {"isPrivate": 0, "pageSize": 100}
        replace(kwargs, params)
        return request(
            method,
            XpcApi.URL_AUDIT_ARTICLES,
            headers=headers,
            params=params
        )
    # go-xpc-api v2 upload api

    def check_params(self, method='POST', headers=None, json=None, **kwargs):
        '''
        :param json: {
            "allow_download_type": "all",
            "authorized_type": 0,
            "categories": [
                {
                    "child_id": 204,
                    "parent_id": 69
                }
            ],
            "cover": "https://oss-xpc0.xpccdn.com/uploadfile/article/2022/4/8/43c9fdbeed489f30757162400825b62a",
            "danmaku": true,
            "is_private": false,
            "role_ids": [
                1
            ],
            "roles": [
                {
                    "id": 1,
                    "name": "出品人"
                }
            ],
            "tags": [
                "乔杉"
            ],
            "title": "视频",
            "type": "selfhost"
        }
        '''
        if headers is None:
            headers = self.headers
        if json is None:
            json = js.loads('''{
            "allow_download_type": "all",
            "authorized_type": 0,
            "categories": [
                {
                    "child_id": 204,
                    "parent_id": 69
                }
            ],
            "cover": "https://oss-xpc0.xpccdn.com/uploadfile/article/2022/4/8/43c9fdbeed489f30757162400825b62a",
            "danmaku": true,
            "is_private": false,
            "role_ids": [
                1
            ],
            "roles": [
                {
                    "id": 1,
                    "name": "出品人"
                }
            ],
            "tags": [
                "乔杉"
            ],
            "title": "视频",
            "type": "selfhost"
        }''')

        replace(kwargs, json, headers)
        return request(
            method=method,
            url=XpcApi.URL_UPLOAD_CHECK_PARAMS,
            headers=headers,
            json=json
        )

    def upload_prepare(self, method='POST', headers=None, json=None, **kwargs):
        '''
        :param json: default {
            "fileMimeType": "video/mp4",
            "fileName": "2e4901c2930f27c8ec4b10c42c8f8be6.mp4",
            "fileSize": 101715839
        }
        '''
        if headers is None:
            headers = self.headers
        if json is None:
            json = {
                "fileMimeType": "video/mp4",
                "fileName": "",
                "fileSize": 0
            }
        replace(kwargs, json, headers)
        return request(
            method,
            XpcApi.URL_UPLOAD_PREPARE,
            headers=headers,
            json=json
        )

    def upload_complete(self, method='POST', headers=None, json=None, **kwargs):
        if headers is None:
            headers = self.headers
        if json is None:
            json = js.loads(r'''{
                "complete": [
                    {
                        "body": "",
                        "headers": {
                            "ETag": "\"e2cddb87ac25f6d67b2ce58afbc07cd3\""
                        },
                        "partNumber": 1
                    }
                ],
                "fileName": "2e4901c2930f27c8ec4b10c42c8f8be6.mp4",
                "formToken": "create_article_624ff8ec73774",
                "isSubmit": true,
                "operateType": "publicCreate",
                "uploadNo": "624ff8ed73774939877258"
            }''')
        replace(kwargs, json)
        return request(
            method,
            XpcApi.URL_UPLOAD_COMPLETE,
            headers=headers,
            json=json
        )

    def edit_article(self, article_id, method='PATCH', headers=None, json=None, **kwargs):
        '''
        '''
        subfix = dt.now().strftime('%Y-%m-%d')
        if headers is None:
            headers = self.headers
        if json is None:
            json = {
                'title': f'xpctest🐶哈哈哈{subfix}',
                'cover': 'https://oss-xpc0.xpccdn.com/uploadfile/article/auto-cover/2022/3/14/fb89f46b-d4fe-42c6-a5bf-5c0f76d3fb1e.jpeg',
                'categories': [{'parent_id': 1, 'child_id': 2}], 
                'tags': ['定格'], 
                'is_reproduce': False, 
                'allow_comment': True, 
                'danmaku': False, 
                'is_private': False, 
                'allow_download_type': 'all',
                'allow_download_flags': {
                    'team': True, 
                    'vip': True, 
                    'reward': False
                },
                'reward_amounts': [660, 880, 8880],
                'role_ids': [1],
                'authorized_type': 0,
                'description': '',
                'allow_vmovier_recommend': True,
                'award': '', 'external_urls': [],
                'team_users': [],
                'stills': {'delete': [], 'update': [], 'insert': []}, 
                'quality': 0
            }
        replace(kwargs, json, headers)
        return request(method, url=XpcApi.URL_EDIT_ARTICLE.format(article_id), headers=headers, json=json)
        
    def download_video_list(self, article_id, method='GET', headers=None, **kwargs):
        '''
        '''
        if headers is None:
            headers = self.headers
        replace(kwargs, headers)
        return request(method, url=XpcApi.URL_DOWNLOAD_VIDEO_LIST.format(article_id), headers=headers)

    def download_by_token(self, method='POST', headers=None, json=None, **kwargs):
        '''
        :param json: default {'download_token': 'asdf'}
        '''
        if headers is None:
            headers = self.headers
        if json is None: json={}
        append(kwargs, json, ['download_token'])
        return request(method, url=XpcApi.URL_DOWNLOAD_BY_TOKEN, headers=headers, json=json)

    def check_private_space(self, method='POST', headers=None, json=None, **kwargs):
        '''检查私密存储空间
        '''
        if headers is None:
            headers = self.headers
        if json is None:
            json = {"fileSize": 0}
        replace(kwargs, json)
        return request(method, url=XpcApi.URL_PRIVATE_SPACE_CHECK, headers=headers, json=json)

    def allow_comment(self, article_id, method='POST', headers=None, json=None, **kwargs):
        '''关闭/开启 作品评论
        '''
        if headers is None:
            headers = self.headers
        if json is None:
            json = {
                "operate_type": "cancel"
            }
        replace(kwargs, json)
        return request(method, url=XpcApi.URL_ALLOW_COMMENT.format(article_id), headers=headers, json=json)

    def im_quota(self, method='GET', headers=None, params=None, **kwargs):
        '''私信额度
        '''
        if headers is None:
            headers = self.headers
        if params is None:
            params = {}
        append(kwargs, params, ['to'])
        return request(method, url=XpcApi.URL_IM_QUOTA, headers=headers, params=params)

    def search_auth(self, method='GET', headers=None, **kwargs):
        '''作品 专业搜索
        '''
        if headers is None:
            headers = self.headers
        return request(method, url=XpcApi.URL_SEARCH_AUTH, headers=headers)

    def creators_auth(self, method='GET', headers=None, **kwargs):
        '''创作人 高级筛选
        '''
        if headers is None:
            headers = self.headers
        return request(method, url=XpcApi.URL_CREATORS_AUTH, headers=headers)

    def get_download_url(self, article_id, method='GET', headers=None, **kwargs):
        '''下载地址 (作者下载原片)
        '''
        if headers is None:
            headers = self.headers
        return request(method, url=XpcApi.URL_DOWNLOAD_URL.format(article_id), headers=headers)

    def check_download_permission(self, article_id, method='GET', params=None, headers=None, **kwargs):
        '''下载权限 (会员下载别人转码后视频)
        '''
        if headers is None:
            headers = self.headers
        if params is None:
            params = {"quality": "360p"}
        replace(kwargs, params)
        return request(method, url=XpcApi.URL_CHECK_DOWNLOAD_PERMISSION.format(article_id), headers=headers, params=params)

    def article_share(self, article_id, method='POST', headers=None, json=None, **kwargs):
        if headers is None:
            headers = self.headers
        if json is None:
            json = {
                "allow_download": True,
                "watermark_status": 0,
                "watermark_text": ""
            }
        replace(kwargs, json)
        return request(method, url=XpcApi.URL_ARTICLE_SHARE.format(article_id), headers=headers, json=json)

    def create_reward_order(self, method='POST', headers=None, json=None, **kwargs):
        '''
        {"article_id":11295436,"amount":660}
        '''
        if headers is None:
            headers = self.headers
        if json is None:
            json = {}
        append(kwargs, json, ['article_id', 'amount'])
        return request(method, url=XpcApi.URL_CREATE_REWARD_ORDER, headers=headers, json=json)



# 金山上传
def upload_video_part(method='PUT', url='', headers=None, params=None, data=None):
    return request(method, url, params=params, headers=headers, data=data)


def upload_video(method='POST', url='', data=None, files=None):
    return request(method, url, data=data, files=files)
