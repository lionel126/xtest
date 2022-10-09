import copy
import json as js
from requests import request
from config import XPC_API_BASE_URL, COOKIE_DEVICE_ID, COOKIE_AUTH
from .user_center import Sess
from utils.utils import replace, append, boss_gateway_token
from datetime import datetime as dt

BOSS_HEADERS = {
    "x-user-id": "1", 
    "x-user-token": boss_gateway_token('abcdef') # appsecret 没校验
}

class XpcApi():
    '''
    xpc api 
    '''
    URL_HOME_RECOMMEND = f'{XPC_API_BASE_URL}/home/recommend'

    URL_FOLLOW = f'{XPC_API_BASE_URL}/user/{{}}/follow'
    URL_ARTICLE_LIST = f'{XPC_API_BASE_URL}/user/10265312/articles'

    URL_UPLOAD_CHECK_PARAMS = f'{XPC_API_BASE_URL}/v2/article/checkParams'
    URL_UPLOAD_PREPARE = f'{XPC_API_BASE_URL}/v2/upload/prepare'
    URL_UPLOAD_COMPLETE = f'{XPC_API_BASE_URL}/v2/upload/complete'
    URL_USER_AUDIT_ARTICLES = f'{XPC_API_BASE_URL}/v2/user/auditArticles'
    URL_EDIT_ARTICLE = f'{XPC_API_BASE_URL}/v2/article/{{}}'
    URL_AUDIT_ARTICLE = f'{XPC_API_BASE_URL}/article/{{}}/audit'

    URL_UPLOAD_TOKEN = f'{XPC_API_BASE_URL}/upload/token'
    URL_UPLOAD_FINISH = f'{XPC_API_BASE_URL}/upload/finish'
    URL_PUBLISH_ARTICLE = f'{XPC_API_BASE_URL}/v2/article'

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
    URL_PUBLIC_STATUS = f'{XPC_API_BASE_URL}/v2/article/{{}}/publicStatus'

    URL_SEM_SUBMIT = f'{XPC_API_BASE_URL}/v2/sem/submit'
    URL_SEM_KEYWORDS = f'{XPC_API_BASE_URL}/v2/sem/keyword/{{}}'
    URL_SEM_ORDER_LIST = f'{XPC_API_BASE_URL}/v2/sem/user/order/list'
    
    URL_ZPT_TRADE_CONFIRM = f'{XPC_API_BASE_URL}/v2/user/zpt/trade/confirm'

    URL_LOG = f'{XPC_API_BASE_URL}/log'
    

    def __init__(self, phone='', password='999999', code='+86', sns_session=None, ua=None, accept_version=None):
        self.headers = {
            'user-agent': 'NewStudios/2.0.8 (com.xinpianchang.newstudios.enterprise; build:938; Android 7.1.2)' if not ua else ua,
            'accept-version': '2.1.7' if not accept_version else accept_version
        }
        if sns_session:
            self.headers['device-id'] = sns_session.cookies[COOKIE_DEVICE_ID]
            self.headers['authorization'] = sns_session.cookies[COOKIE_AUTH]
        if phone:
            user = self.login(phone, password, code)
            self.user_id = user['id']

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
        user = r.json()['data']['user']
        # self.user_id = user['id']
        self.headers.update(s.headers)
        self.headers['device-id'] = s.headers['device-no']
        del self.headers['device-no']
        return user

    def logout(self):
        '''
        '''
        self.session.logout()

    def home_recommend(self, method='GET', params=None, headers=None, **kwargs):
        '''
        '''
        if headers is None:
            headers = copy.copy(self.headers)
        if params is None:
            params={
                'page': 1,
                'pageSize': 10
            }
        replace(kwargs, params)
        return request(method, url=XpcApi.URL_HOME_RECOMMEND, headers=headers, params=params)

    def article_list(self, user_id, method='GET', params=None, **kwargs):
        '''temporary
        '''
        if params is None:
            params = {
                'is_hide_in_space': 0,
                'return_struct_type': 'user_home'
            }
        append(kwargs, params, ['page'])
        return request(method=method, url=XpcApi.URL_ARTICLE_LIST.format(user_id), params=params)


    def follow(self, user_id, method='POST', headers=None):
        if headers is None:
            headers = copy.deepcopy(self.headers)
        return request(
            method,
            XpcApi.URL_FOLLOW.format(user_id),
            headers=headers
        )

    def user_audit_articles(self, method='GET', headers=None, params=None, **kwargs):
        '''
        用户审核中作品列表？
        :param params: {"isPrivate":0, "pageSize": 100}
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if params is None:
            params = {"isPrivate": 0, "pageSize": 100}
        replace(kwargs, params)
        return request(
            method,
            XpcApi.URL_USER_AUDIT_ARTICLES,
            headers=headers,
            params=params
        )

    def audit_article(self, article_id, method='POST', headers=None, json=None, **kwargs):
        '''管理员审核作品
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            # 评级差 审核通过
            json = {"quality": 3, "is_audit": 1}
        replace(kwargs, json, headers)
        return request(method, url=XpcApi.URL_AUDIT_ARTICLE.format(article_id), headers=headers, json=json)

    # php xpc-api v1 upload api
    def upload_token(self, method='POST', headers=None, json=None, **kwargs):
        '''v1

        :param json:default {
                "fileSize": 0,
                # "filePartSize": 0, # optional
                "key": "filename.mp4",
                "fileMimeType": [
                    "video/mp4"
                ],
                "fileUploadAction":"createPublicVideo"
            }
        {
            "fileSize": 999999,
            "filePartSize": 333333,
            "key": "filename.mp4",
            "fileMimeType": [
                "video/mp4"
            ],
            "fileUploadAction":"createPublicVideo"
        }

        createPrivateVideo	上传私密视频
        createPublicVideo	上传公开作品的视频
        updatePrivateVideo	修改私密视频
        updatePublicVideo	修改公开作品
        publicVideoTransPrivateVideo	公开作品转私密视频
        privateVideoTransPublicVideo	私密视频转公开作品
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {
                "fileSize": 0,
                "filePartSize": 0,
                "key": "filename.mp4",
                "fileMimeType": [
                    "video/mp4"
                ],
                "fileUploadAction": "createPublicVideo"
            }
        replace(kwargs, json, headers)
        # append(kwargs, json, ['filePartSize'])
        # if 'filePartSize' not in json:
        #     json['filePartSize'] = json['fileSize']
        return request(method, XpcApi.URL_UPLOAD_TOKEN, headers=headers, json=json)

    def upload_finish(self, method='POST', headers=None, json=None, **kwargs):
        '''v1 
        :param json: default 
        {
            "data": {
                "body": "<CompleteMultipartUpload><Part><PartNumber>1</PartNumber><ETag></ETag></Part></CompleteMultipartUpload>",
                "uploadId": ""
            },
            "uploadNo": ""
        }

        {
            "data": {
                "body": "<CompleteMultipartUpload><Part><PartNumber>1</PartNumber><ETag></ETag></Part><Part><PartNumber>2</PartNumber><ETag></ETag></Part><Part><PartNumber>3</PartNumber><ETag></ETag></Part><Part><PartNumber>4</PartNumber><ETag></ETag></Part><Part><PartNumber>5</PartNumber><ETag></ETag></Part><Part><PartNumber>6</PartNumber><ETag></ETag></Part></CompleteMultipartUpload>",
                "uploadId": "4f690f3735d64ec59d21dbaca3096c24"
            },
            "uploadNo": "60bf2a1a635f8"
        }
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {
                "data": {
                    "body": "<CompleteMultipartUpload><Part><PartNumber>1</PartNumber><ETag></ETag></Part></CompleteMultipartUpload>",
                    "uploadId": ""
                },
                "uploadNo": ""
            }
        if 'partCount' in kwargs:
            l = [
                f'<Part><PartNumber>{i+1}</PartNumber><ETag></ETag></Part>' for i in range(kwargs['partCount'])]
            body = '<CompleteMultipartUpload>{}</CompleteMultipartUpload>'.format(
                ''.join(l))
            kwargs['body'] = body
        replace(kwargs, json, headers)
        return request(method, XpcApi.URL_UPLOAD_FINISH, headers=headers, json=json)

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
            headers = copy.deepcopy(self.headers)
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
            headers = copy.deepcopy(self.headers)
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
            headers = copy.deepcopy(self.headers)
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
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {
                'title': f'xpctest🐶测试edit{subfix}',
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

    def publish_article(self, method='POST', headers=None, json=None, **kwargs):
        '''
        '''
        subfix = dt.now().strftime('%y%b%d %H:%M:%S.%f %W%a%j')
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {
                'title': f'🐶{subfix}',
                'cover': '', # https://oss-xpc0.xpccdn.com/newupload/assets/article/cover/2022/5/6286fe3bd99fb
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
                # 'reward_amounts': [660, 880, 8880],
                'role_ids': [1],
                'authorized_type': 0,
                'description': '',
                'allow_vmovier_recommend': True,
                # 'award': '',
                # 'external_urls': [],
                # 'team_users': [],
                # 'stills': {'delete': [], 'update': [], 'insert': []},
                # 'stills': [],
                # 'quality': 0,
                'type': 'selfhost',
                'public_status': 0,
                'upload_no': ''
            }
        replace(kwargs, json, headers)
        return request(method, url=XpcApi.URL_PUBLISH_ARTICLE, headers=headers, json=json)

    def download_video_list(self, article_id, method='GET', headers=None, **kwargs):
        '''
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        replace(kwargs, headers)
        return request(method, url=XpcApi.URL_DOWNLOAD_VIDEO_LIST.format(article_id), headers=headers)

    def download_by_token(self, method='POST', headers=None, json=None, **kwargs):
        '''
        :param json: default {'download_token': 'asdf'}
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {}
        append(kwargs, json, ['download_token'])
        return request(method, url=XpcApi.URL_DOWNLOAD_BY_TOKEN, headers=headers, json=json)

    def check_private_space(self, method='POST', headers=None, json=None, **kwargs):
        '''检查私密存储空间
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {"fileSize": 0}
        replace(kwargs, json)
        return request(method, url=XpcApi.URL_PRIVATE_SPACE_CHECK, headers=headers, json=json)

    def allow_comment(self, article_id, method='POST', headers=None, json=None, **kwargs):
        '''关闭/开启 作品评论
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
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
            headers = copy.deepcopy(self.headers)
        if params is None:
            params = {}
        append(kwargs, params, ['to'])
        return request(method, url=XpcApi.URL_IM_QUOTA, headers=headers, params=params)

    def search_auth(self, method='GET', headers=None, **kwargs):
        '''作品 专业搜索
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        return request(method, url=XpcApi.URL_SEARCH_AUTH, headers=headers)

    def creators_auth(self, method='GET', headers=None, **kwargs):
        '''创作人 高级筛选
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        return request(method, url=XpcApi.URL_CREATORS_AUTH, headers=headers)

    def get_download_url(self, article_id, method='GET', headers=None, **kwargs):
        '''下载地址 (作者下载原片)
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        return request(method, url=XpcApi.URL_DOWNLOAD_URL.format(article_id), headers=headers)

    def check_download_permission(self, article_id, method='GET', params=None, headers=None, **kwargs):
        '''下载权限 (会员下载别人转码后视频)
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if params is None:
            params = {"quality": "360p"}
        replace(kwargs, params)
        return request(method, url=XpcApi.URL_CHECK_DOWNLOAD_PERMISSION.format(article_id), headers=headers, params=params)

    def article_share(self, article_id, method='POST', headers=None, json=None, **kwargs):
        if headers is None:
            headers = copy.deepcopy(self.headers)
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
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {}
        append(kwargs, json, ['article_id', 'amount'])
        return request(method, url=XpcApi.URL_CREATE_REWARD_ORDER, headers=headers, json=json)

    def public_status(self, article_id, method='POST', headers=None, json=None, **kwargs):
        '''修改公开作品的发布状态
        0公开发布, 1主页隐藏, 2仅分享可见
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {}
        append(kwargs, json, ['public_status'])
        return request(method, url=XpcApi.URL_PUBLIC_STATUS.format(article_id), headers=headers, json=json)

    def sem_submit(self, method='POST', headers=None, json=None, **kwargs):
        '''sem 下单
        :param json:  
        {
            "article_id": 11297576, 
            "keyword_id": 2, 
            "position": 11,
            "date_list": ["2022-09-08 19:00:00", "2022-09-08 21:00:00"]
        }
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        if json is None:
            json = {
                "article_id": 0, 
                "keyword_id": 0, 
                "position": 0,
                "date_list": ["2022-09-08 19:00:00", "2022-09-08 21:00:00"]
            }
        replace(kwargs, json)
        return request(method, url=XpcApi.URL_SEM_SUBMIT, headers=headers, json=json)

    def sem_keywords(self, article_id, method='GET', headers=None):
        '''作品相关的sem词 
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        return request(method, url=XpcApi.URL_SEM_KEYWORDS.format(article_id), headers=headers)

    def sem_order_list(self, method='GET', headers=None):
        '''sem 订单列表
        '''
        if headers is None:
            headers = copy.deepcopy(self.headers)
        return request(method, url=XpcApi.URL_SEM_ORDER_LIST, headers=headers)

    def zpt_trade_confirm(self, method='POST', data=None, headers=None, **kwargs):
        '''
        '''
        if data is None:
            data = {
                'article_id': 0,
                'price': 2800
            }
        if headers is None:
            headers = copy.deepcopy(self.headers)
        replace(kwargs, data, headers)
        return request(method=method, url=XpcApi.URL_ZPT_TRADE_CONFIRM, data=data, headers=headers)

    def log(self, method='POST', json=None, headers=None, **kwargs):
        '''上报行为: 作品通展示/作品通播放
        '''
        if headers is None:
            headers = copy.copy(self.headers)
        if json is None:
            json = {
                "event_extend": {
                    "from": "首页-推荐",
                    "number": "0",
                    "request_id": "NQfTUK5Kx6vj3UatQ3i6iVM3TB0XGGOP",
                    "type": "作品通大卡片（播放器居中）"
                },
                "event_source": None,
                "event_type": "display",
                "event_value": None,
                "resource_id": "2615",
                "resource_type": "zpt"
            }
        replace(kwargs, json, headers)
        return request(method, url=XpcApi.URL_LOG, json=json, headers=headers)

class XpcBackend():
    '''
    xpcapi boss接口
    #todo: 登录
    '''
    URL_SEM_LIST = f'{XPC_API_BASE_URL}/backend/sem/order/list'
    URL_ZPT_REVIEW = f'{XPC_API_BASE_URL}/backend/zpt/{{}}/review'
    URL_ZPT_LIST = f'{XPC_API_BASE_URL}/backend/zpt'

    def sem_order_list(self, method='GET', params=None, headers=None, **kwargs):
        '''
        :param params: userids=10265312%2C10000010&status=1&page=1&pageSize=10
        '''
        if headers is None:
            headers = copy.copy(BOSS_HEADERS)
        if params is None:
            params = {
                'userids': '10265312,10000010',
                'status': 1,
                'page': 1,
                'pageSize': 10
            }
        replace(kwargs, params, headers)
        return request(method=method, url=XpcBackend.URL_SEM_LIST, params=params, headers=headers)

    def zpt_list(self, method='GET', params=None, headers=None, **kwargs):
        if headers is None:
            headers = copy.copy(BOSS_HEADERS)
        if params is None:
            params = {
                'status':0
            }
        replace(kwargs, params, headers)
        append(kwargs, params, ['user_ids'])
        return request(method, url=XpcBackend.URL_ZPT_LIST, params=params, headers=headers)

    def zpt_review(self, zpt_id, method='PUT', json=None, headers=None, **kwargs):
        '''
        '''
        if headers is None:
            headers = copy.copy(BOSS_HEADERS)
        if json is None:
            json={
                'is_allow': True
            }
        replace(kwargs, json, headers)
        append(kwargs, json, ['reason'])
        return request(method, url=XpcBackend.URL_ZPT_REVIEW.format(zpt_id), json=json, headers=headers)

class XpcServerApi():
    @staticmethod
    def zpt_status(zpt_id, method='POST', json=None, headers=None, **kwargs):
        '''
        :param json:{
                'status': 'completed', # required, completed or working
                'display_count': 998 # required if status is completed
            }
        '''
        url = f'{XPC_API_BASE_URL}/server-api/zpt/{{}}/status'
        if headers is None:
            headers = {'host': '10.25.98.5'}
        if json is None:
            json = {
                'status': 'completed',
                'display_count': 998,
                'ZDLg': '7ftMq1zCMwQ5doks'
            }
        replace(kwargs, json)
        return request(method, url=url.format(zpt_id), headers=headers, json=json)