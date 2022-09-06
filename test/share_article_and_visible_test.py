import pytest
from copy import deepcopy
from datetime import datetime
from api.xpcapi import XpcApi
from api.upload import get_file, FilePartSize, upload
from api.testapi import verify_realname

# TITLE = datetime.now().strftime('%W%a%j %S.%f')

# 私密作品字段 后端
def get_default_private_template():
    return {
        "upload_no": "",
        "title": "",
        "type": "selfhost",
        "is_private": True,

        "allow_download_type": "only_team",
        "allow_comment": True, 
    }
# 私密作品字段 前端
PRIVATE_REALITY = {
    "title": "", 
    "cover": "", 
    "categories": [], 
    "tags": [], 
    "is_reproduce": False, 
    "allow_comment": True, 
    "danmaku": False, 
    "is_private": True, 
    "allow_download_type": "only_team",
    "role_ids": [], 
    "description": "", 
    "allow_vmovier_recommend": False, 
    "award": "", 
    "external_urls": [], 
    "team_users": [], 
    "stills": [], 
    "type": "selfhost", 
    "upload_no": ""
}

# 公开作品 基础表单字段 后端
def get_default_public_base_template():
    return {
        "title":"",
        "allow_comment":True,
        "is_private":False,
        "allow_download_type":"all",
        # "allow_download_flags":{"team":False,"vip":False,"reward":False},
        # "reward_amounts":[],    
        "public_status":2,
        "type":"selfhost",
        "upload_no":""
    }
# 公开作品 基础表单字段 前端
PUBLIC_BASE_REALITY = {
    "title":"",
    "cover":"",
    "is_reproduce":False,
    "allow_comment":True,
    "danmaku":False,
    "is_private":False,
    "allow_download_type":"all",
    "allow_download_flags":{"team":False,"vip":False,"reward":False},
    "reward_amounts":[],
    "authorized_type":0,
    "description":"",
    "stills":[],
    "quality":4,
    "public_status":2,
    "type":"selfhost",
    "upload_no":""
}

# 公开作品 专业表单字段 默认
def get_default_public_pro_template():
    return {
        "title":"",
        "cover":"",
        "categories":[{"parent_id":1,"child_id":2}],
        "tags":["创意"],
        "allow_comment":True,
        "is_private":False,
        "allow_download_type":"all",
        # "allow_download_flags":{"team":False,"vip":True,"reward":True},
        # "reward_amounts":[660,880,1660],
        "role_ids":[1],
        "public_status":0,
        "type":"selfhost",
        "upload_no":""
    }

# 公开作品 专业表单字段 前端
PUBLIC_PRO_REALITY = {
    "title":"",
    "cover":"",
    "categories":[{"parent_id":1,"child_id":2}],
    "tags":["创意"],
    "is_reproduce":False,
    "allow_comment":True,
    "danmaku":False,
    "is_private":False,
    "allow_download_type":"all",
    "allow_download_flags":{"team":False,"vip":True,"reward":True},
    "reward_amounts":[660,880,1660],
    "role_ids":[1],
    "authorized_type":0,
    "description":"",
    "allow_vmovier_recommend":True,
    "award":"",
    "external_urls":[],
    "team_users":[],
    "stills":[],
    "quality":4,
    "public_status":0,
    "type":"selfhost",
    "upload_no":""
}

def get_title(pre=""):
    return datetime.now().strftime(f'{pre}%W%a%j %H%M%S.%f')

@pytest.fixture
def non_verified_user():
    session = XpcApi('18238472139')
    yield session
    session.logout()

@pytest.fixture
def verified_user():
    session = XpcApi('13484848484')
    yield session
    session.logout()

@pytest.fixture
def admin():
    session = XpcApi('13521141218')
    yield session
    session.logout()

def test_non_verified_user_publish_private_article(non_verified_user:XpcApi):
    key, file_size = get_file()
    j = non_verified_user.upload_token(key=key, fileSize=file_size, filePartSize=FilePartSize).json()
    partCount, uploadId, uploadNo = upload(j)
    non_verified_user.upload_finish(partCount=partCount, uploadId=uploadId, uploadNo=uploadNo)
    non_verified_user.publish_article(json=get_default_private_template(), upload_no=uploadNo, title=get_title('私'))

def test_non_verified_user_publish_public_article(non_verified_user:XpcApi):
    key, file_size = get_file()
    j = non_verified_user.upload_token(key=key, fileSize=file_size, filePartSize=FilePartSize).json()
    partCount, uploadId, uploadNo = upload(j)
    non_verified_user.upload_finish(partCount=partCount, uploadId=uploadId, uploadNo=uploadNo)
    res = non_verified_user.publish_article(json=get_default_public_base_template(), upload_no=uploadNo, title=get_title('公'))
    return res

def test_non_verified_user_update_public_status(non_verified_user:XpcApi, admin:XpcApi):
    '''
    仅分享 改为 公开
    仅分享 改为 仅分享 请先补充作品信息？ #todo
    '''
    res = test_non_verified_user_publish_public_article(non_verified_user)
    article_id = res.json()['data']['article_id']
    admin.audit_article(article_id)
    for res in (
        non_verified_user.public_status(article_id, public_status=0),
        non_verified_user.public_status(article_id, public_status=1),
        
    ):
        j = res.json()
        assert j['status'] == 1020
        assert j['message'] == '未认证用户不能上传公开作品'

    j = non_verified_user.public_status(article_id, public_status=2).json()
    assert j['status'] == 1036
    assert j['message'] == "请先补充作品信息"

def test_verified_user_publish_public_article_status_2(verified_user:XpcApi):
    '''
    fail : 认证用户基础发布的校验？
    '''
    key, file_size = get_file()
    j = verified_user.upload_token(key=key, fileSize=file_size, filePartSize=FilePartSize).json()
    partCount, uploadId, uploadNo = upload(j)
    verified_user.upload_finish(partCount=partCount, uploadId=uploadId, uploadNo=uploadNo)
    verified_user.publish_article(json=get_default_public_base_template(), upload_no=uploadNo, title=get_title('公基'))
    

def test_verified_user_publish_public_article_status_0(verified_user:XpcApi):
    
    key, file_size = get_file()
    j = verified_user.upload_token(key=key, fileSize=file_size, filePartSize=FilePartSize).json()
    partCount, uploadId, uploadNo = upload(j)
    verified_user.upload_finish(partCount=partCount, uploadId=uploadId, uploadNo=uploadNo)
    res = verified_user.publish_article(json=get_default_public_pro_template(), upload_no=uploadNo, title=get_title('公专'))
    return res
    

def test_verified_user_publish_public_article_status_1(verified_user:XpcApi):
    
    key, file_size = get_file()
    j = verified_user.upload_token(key=key, fileSize=file_size, filePartSize=FilePartSize).json()
    partCount, uploadId, uploadNo = upload(j)
    verified_user.upload_finish(partCount=partCount, uploadId=uploadId, uploadNo=uploadNo)
    verified_user.publish_article(json=get_default_public_pro_template(), upload_no=uploadNo, title=get_title('公专'), public_status=1)
    

def test_verified_user_update_public_status(verified_user:XpcApi):
    res = test_verified_user_publish_public_article_status_0(verified_user)
    article_id = res.json()['data']['article_id']
    for res in (
        verified_user.public_status(article_id, public_status=0),
        verified_user.public_status(article_id, public_status=1),
        verified_user.public_status(article_id, public_status=2),
    ):
        j = res.json()
        assert j['status'] == 0
        assert j['message'] == 'OK'

def test_yyy():
    verify_realname(user_id=11488649)

def test_zzz(verified_user:XpcApi):
    verified_user.public_status(11297569, public_status=2)

