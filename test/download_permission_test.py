import json
from datetime import datetime, timedelta
import requests
import pytest
import phpserialize
from bs4 import BeautifulSoup
from api.xpcapi import XpcApi
from api.snsapi import Xpc
from api import testapi, PayAdmin, MallV2
from api.user_center import InternalApi as useriapi
from utils import utils
import config
# 测试数据
# 本人/团队成员/赞赏者/会员/登录用户/未登录用户 
# 组合：本人会员/团队会员


# ARTICLE_ID = 11295436
ARTICLE_ID = 11297151
VIP_END_TIME_IN_THE_FUTURE = (datetime.now() + timedelta(days=10)).strftime('%Y%m%d')
VIP_END_TIME_IN_THE_PAST = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

# def test_1():
#     host = XpcApi()
#     host.login('15600455126', '999999')
#     host.edit_article(11296410, allow_download_flags={'team': True, 'vip': True, 'reward': False})

#     guest = XpcApi()
#     guest.login('18258259056', '999999')
#     guest.download_video_list(11296410)
def redis_del_article_cache(article_id):
    '''后端已经做了 不需要了 '''
    raise Exception('not necessary anymore')
    
    key = f'article_transform___{article_id}'
    pre_keys = f'{key}_pre_keys'
    r = testapi.get_redis(db='xpcapi', key=pre_keys)
    value = r.json()['data']['value']
    if value:
        to_be_deleted = [{'db':'xpcapi', 'key': f'{key}{v}'} for v in value.values()]
        to_be_deleted.append({'db': 'xpcapi', 'key': pre_keys})
        r = testapi.del_redis(*to_be_deleted)
        assert r.status_code == 200

def redis_del_user_cache(user_id: int):
    # prefix = 'user-center-xpc-line-test'
    key = f'user_info_{user_id}'
    r = testapi.del_redis(dict(db='usercenter', key=key))
    assert r.status_code == 200


def clear_rewards(user: Xpc, article_id: int):
    r = testapi.get_article_rewards(user_id=user.id, article_id=article_id, reward_status=1)
    assert r.status_code == 200
    results = r.json()['data']
    if results:
        params = [('id__in', r['id']) for r in results]
        # params.append(('reward_status', 1))       
        r = testapi.update_article_rewards(params=params, json={'reward_status': 0})
        assert r.status_code == 200

def reward(user: Xpc, article_id: int):
    xuser = XpcApi(sns_session=user)
    trade_no = xuser.create_reward_order(article_id=article_id, amount=660).json()['data']['trade_no']
    fix_order(trade_no, user.id)

def fix_order(trade_no, user_id):
    location = MallV2.trade_token(tradeNo=trade_no, userId=user_id).json()['data']['location']
    token = location.split('/')[-1]
    data = MallV2.trade_detail(tradeNo=trade_no, token=token, userId=user_id).json()['data']
    
    # channel = data['channelList'][random.randint(0, len(data['channelList'])-1)]
    channel = utils.get_available_channel(data['channelList'], location)
    r = MallV2.pay(**channel).json()
    PayAdmin().fix(r['data']['order'])

def test_x():
    userid = 10474253
    phone = '13609750911'
    articleid = 11295436
    cache_key = f'article_transform___{articleid}-1-1--1_2.1.3'
    
    user = Xpc(phone)
    # user.quit_team(id=articleid)
    # user.apply_team_member(articleid=articleid)
    # apid = testapi.team_applications(userid=10474253, articleid=11295436).json()['data'][0]['id']
    
    # author = Sns('15600455126')
    # # author.agree_application_for_team_member(id=apid)
    
    


    # xauthor = XpcApi(sns_session=author)
    # xauthor.edit_article(articleid, allow_download_flags={'team': False, 'vip': False, 'reward': True})
    
    # xauthor.download_video_list(articleid)

    xuser = XpcApi(sns_session=user)
    # download_token = xuser.download_video_list(articleid).json()['data']['reward_list'][0]['download_token']
    # download_url = xuser.download_by_token(download_token=download_token).json()['data']['downloadUrl']
    # r = requests.get(download_url)
    # assert r.status_code == 200

    xuser.download_video_list(articleid).json()['data']['reward_list'][0]
    clear_rewards(user, articleid)
    for _ in range(10):
        trade_no = xuser.create_reward_order(article_id=articleid, amount=660).json()['data']['trade_no']
        fix_order(trade_no, userid)

def test_y():
    # useriapi.vip_notify(user_id=10265312, end_time='20220202', type=1)
    # redis_del_article_cache(ARTICLE_ID)
    'http://192.168.3.89:4444'

@pytest.fixture
def author():
    author = Xpc('15600455126')
    author.id = 10265312
    yield author
    author.logout()

@pytest.fixture
def user():
    '''登录用户
    '''
    u = Xpc('13609750911')
    u.id = 10474253
    quit_team(u, ARTICLE_ID)
    quit_vip(u)
    clear_rewards(u, ARTICLE_ID)
    yield u
    u.logout()

@pytest.fixture
def user_logged_out():
    '''未登录用户
    '''
    u = Xpc()
    yield u


def join_team(user: Xpc, author: Xpc, article_id: int):
    user.quit_team(id=article_id)
    user.apply_team_member(articleid=article_id)
    apid = testapi.team_applications(userid=user.id, articleid=article_id).json()['data'][0]['id']
    author.agree_application_for_team_member(id=apid)

def quit_team(user: Xpc, article_id: int):
    user.quit_team(id=article_id)

def join_vip(user: Xpc, type=1, flag=1):
    '''
    svip: type=2; flag=3
    black diamond: type=2; flag=7
    '''
    useriapi.vip_notify(user_id=user.id, end_time=VIP_END_TIME_IN_THE_FUTURE, type=type, flag=flag)

def quit_vip(user: Xpc,):
    useriapi.vip_notify(user_id=user.id, end_time=VIP_END_TIME_IN_THE_PAST)

def assert_auth_exists(who: Xpc, exists: bool):
    '''断言 下载✅ 求下载❌ 
    '''
    html = who.article(ARTICLE_ID).text
    download = BeautifulSoup(html, "html.parser").select('a.download')
    assert download
    begging_button = BeautifulSoup(html, "html.parser").select('a.apply-download')
    assert not begging_button 
    auth = BeautifulSoup(html, "html.parser").select('li.download-authorization')
    auth_invisible = BeautifulSoup(html, "html.parser").select('li.download-authorization.dn')
    if exists:
        assert auth
        # assert not auth_invisible
    else:
        # try:
            assert not auth
        # except AssertionError:
        #     assert BeautifulSoup(html, "html.parser").select('li.download-authorization.dn')
        #     print('有授权信息 不展示')

def assert_begging_exists(who: Xpc):
    '''
    断言： 求下载✅  下载❌
    '''
    html = who.article(ARTICLE_ID).text
    begging_button = BeautifulSoup(html, "html.parser").select('a.apply-download')
    assert begging_button
    download = BeautifulSoup(html, "html.parser").select('a.download')
    assert not download

def edit_article(author, article_id, team=False, vip=False, reward=False):
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        article_id, 
        allow_download_flags={'team': team, 'vip': vip, 'reward': reward},
        **{'user-agent': config.DEL}
    )

def assert_response_of_download_by_token(res):
    assert res.status_code == 200
    j = res.json()
    url = j['data']['downloadUrl']
    assert '.mp4?response-content-disposition=attachment%3B+filename%2A%3DUTF-8%27%27' in url
    assert j['message'] == 'OK'
    assert j['status'] == 0

def test_2(author, user):
    '''开启赞赏
    '''
    # useriapi.vip_notify()

    xauthor = XpcApi(sns_session=author)
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': False, 'reward': True},
        **{'user-agent': config.DEL}
    )
    
    xuser = XpcApi(sns_session=user)
    data = xuser.download_video_list(ARTICLE_ID).json()['data']
    assert len(data['list']) == 0
    assert len(data['reward_list']) == 1
    download_token = data['reward_list'][0]['download_token']
    assert download_token
    assert data['reward_list'][0]['profile_code'] == '720p' 
    r = xuser.download_by_token(download_token=download_token)
    assert_response_of_download_by_token(r)

def test_3(author, user):
    '''开启赞赏 author
    '''
    # useriapi.vip_notify()

    xauthor = XpcApi(sns_session=author)
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': False, 'reward': True},
        **{'user-agent': config.DEL}
    )
    
    xuser = xauthor
    data = xuser.download_video_list(ARTICLE_ID).json()['data']
    assert len(data['list']) == 4
    assert len(data['reward_list']) == 0
    
def test_4(author, user):
    '''todo 
    '''
    # useriapi.vip_notify()

    xauthor = XpcApi(sns_session=author)
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': True, 'reward': True},
        **{'user-agent': config.DEL}
    )
    
    xuser = XpcApi(sns_session=user)
    data = xuser.download_video_list(ARTICLE_ID).json()['data']
    assert len(data['list']) == 4
    assert len(data['reward_list']) == 1
    download_token = data['reward_list'][0]['download_token']
    assert download_token
    assert data['reward_list'][0]['profile_code'] == '720p' 
    r = xuser.download_by_token(download_token=download_token)
    assert_response_of_download_by_token(r)

def test_5(author, user):
    # redis_del_user_cache(author.id)
    join_team(user, author, ARTICLE_ID)
    # join_vip(user)
    # join_vip(user, flag=3, type=2)
    # redis_del_user_cache(user.id)
    
    xauthor = XpcApi(sns_session=author)
    
    # xauthor.edit_article(
    #     ARTICLE_ID, 
    #     allow_download_flags={'team': False, 'vip': True, 'reward': False},
    #     **{'user-agent': config.DEL}
    # )
    # xauthor.edit_article(
    #     ARTICLE_ID, 
    #     allow_download_flags={'team': True, 'vip': True, 'reward': False},
    #     **{'user-agent': config.DEL}
    # )
    # xauthor.edit_article(
    #     ARTICLE_ID, 
    #     allow_download_flags={'team': False, 'vip': False, 'reward': True},
    #     **{'user-agent': config.DEL}
    # )
    # xauthor.edit_article(
    #     ARTICLE_ID, 
    #     allow_download_flags={'team': False, 'vip': False, 'reward': True},
    #     **{'user-agent': config.DEL}
    # )
    # xauthor.edit_article(
    #     ARTICLE_ID, 
    #     allow_download_flags={'team': True, 'vip': True, 'reward': False},
    #     **{'user-agent': config.DEL}
    # )
    # xauthor.edit_article(
    #     ARTICLE_ID, 
    #     allow_download_flags={'team': False, 'vip': False, 'reward': True},
    #     **{'user-agent': config.DEL}
    # )
    

    # user.quit_team(id=ARTICLE_ID)

    # user.apply_team_member(articleid=ARTICLE_ID)
    # apid = testapi.team_applications(userid=10474253, articleid=ARTICLE_ID).json()['data'][0]['id']
    # author.agree_application_for_team_member(id=apid)

'''需求：
客态展示授权方式， 主态不展示（主态：本人 + 开启团队下载的团队成员）

全靠html无法测试 一部分是需要js运行才能拿到结果 todo: 加入selenium
'''
def test_article_auth_1(author, user, user_logged_out):
    '''团队下载
    作者
    未登录
    
    非团队 非vip 
    非团队 vip
    团队 vip
    团队 非vip
    '''

    edit_article(author, ARTICLE_ID, team=True)
    assert_auth_exists(author, False)
    assert_begging_exists(user_logged_out)

    assert_begging_exists(user)
    join_vip(user)
    assert_begging_exists(user)
    # reward(user, ARTICLE_ID)
    # assert_begging_exists(user)

    join_team(user, author, ARTICLE_ID)
    assert_auth_exists(user, False)
    quit_vip(user)
    assert_auth_exists(user, False)
    # clear_rewards(user, ARTICLE_ID)
    # assert_auth_exists(user, False)

def test_article_auth_1_2(author, user):
    '''
    关闭赞赏下载后 原赞赏者？
    '''

def test_article_auth_2(author, user, user_logged_out):
    '''vip下载
    作者
    未登录

    非会员
    会员
    '''
    edit_article(author, ARTICLE_ID, vip=True)
    assert_auth_exists(author, False)
    assert_auth_exists(user_logged_out, True)
    
    assert_auth_exists(user, True)
    join_vip(user)
    assert_auth_exists(user, True)

def test_article_auth_3(author, user, user_logged_out):
    '''赞赏下载
    作者
    未登录
    
    未赞赏
    赞赏
    '''
    edit_article(author, ARTICLE_ID, reward=True)
    assert_auth_exists(author, False)
    assert_auth_exists(user_logged_out, True)

    assert_auth_exists(user, True)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, True)

def test_article_auth_4(author, user, user_logged_out):
    '''本人下载
    作者
    未登录

    团队
    vip
    '''
    edit_article(author, ARTICLE_ID)
    assert_auth_exists(author, False)
    assert_begging_exists(user_logged_out)

    assert_begging_exists(user)
    join_team(user, author, ARTICLE_ID)
    assert_begging_exists(user)
    join_vip(user)
    assert_begging_exists(user)

def test_article_auth_5(author, user, user_logged_out):
    '''团队下载 + vip
    作者
    未登录
    
    非团队 非vip 
    非团队 vip
    团队 vip
    团队 非vip
    '''

    edit_article(author, ARTICLE_ID, team=True, vip=True)
    assert_auth_exists(author, False)
    assert_auth_exists(user_logged_out, True)

    assert_auth_exists(user, True)
    join_vip(user)
    assert_auth_exists(user, True)
    # reward(user, ARTICLE_ID)
    # assert_begging_exists(user)

    join_team(user, author, ARTICLE_ID)
    assert_auth_exists(user, False)
    quit_vip(user)
    assert_auth_exists(user, False)
    # clear_rewards(user, ARTICLE_ID)
    # assert_auth_exists(user, False)    
    
def test_article_auth_6(author, user, user_logged_out):
    '''赞赏下载 + vip
    作者
    未登录
    
    非团队 非vip 
    非团队 vip
    团队 vip
    团队 非vip
    '''

    edit_article(author, ARTICLE_ID, reward=True, vip=True)
    # assert_auth_exists(author, False)
    assert_auth_exists(user_logged_out, True)

    assert_auth_exists(user, True)
    join_vip(user)
    assert_auth_exists(user, True)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, True)
    
    join_team(user, author, ARTICLE_ID)
    assert_auth_exists(user, True)
    clear_rewards(user, ARTICLE_ID)
    assert_auth_exists(user, True)   
    quit_vip(user)
    assert_auth_exists(user, True)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, True)
    quit_team(user, ARTICLE_ID)
    assert_auth_exists(user, True)
    
def test_article_auth_7(author, user, user_logged_out):
    '''赞赏下载 + 团队下载 同test_article_auth_6
    作者
    未登录
    
    非团队 非vip 
    非团队 vip
    团队 vip
    团队 非vip
    '''

    edit_article(author, ARTICLE_ID, reward=True, team=True)
    # assert_auth_exists(author, False)
    assert_auth_exists(user_logged_out, True)

    assert_auth_exists(user, True)
    join_vip(user)
    assert_auth_exists(user, True)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, True)
    
    join_team(user, author, ARTICLE_ID)
    assert_auth_exists(user, False)
    clear_rewards(user, ARTICLE_ID)
    assert_auth_exists(user, False)   
    quit_vip(user)
    assert_auth_exists(user, False)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, False)
    quit_team(user, ARTICLE_ID)
    assert_auth_exists(user, True)

def test_article_auth_8(author, user, user_logged_out):
    '''赞赏下载 + 团队下载 + vip下载 同test_article_auth_6
    作者
    未登录
    
    非团队 非vip 
    非团队 vip
    团队 vip
    团队 非vip
    '''

    edit_article(author, ARTICLE_ID, reward=True, team=True, vip=True)
    assert_auth_exists(author, False)
    assert_auth_exists(user_logged_out, True)

    assert_auth_exists(user, True)
    join_vip(user)
    assert_auth_exists(user, True)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, True)
    
    join_team(user, author, ARTICLE_ID)
    assert_auth_exists(user, False)
    clear_rewards(user, ARTICLE_ID)
    assert_auth_exists(user, False)   
    quit_vip(user)
    assert_auth_exists(user, False)
    reward(user, ARTICLE_ID)
    assert_auth_exists(user, False)
    quit_team(user, ARTICLE_ID)
    assert_auth_exists(user, True)

