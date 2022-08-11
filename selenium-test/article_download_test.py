'''
todo 目前测试分两步：
    连接浏览器 + 登录
    刷新页面 + 获取下载列表


'''
import time
from turtle import down

import pytest
from selenium.common.exceptions import NoSuchElementException
from pages.passport.login import Login 
from pages.xpc.article_new import Article
from test.download_permission_test import author, user, ARTICLE_ID, join_vip, join_team, quit_vip
from api.xpcapi import XpcApi
import config

REWARD_DATA = [{'title': '标清 720P', 'button': '赞赏下载'}]
TEAM_DATA = [{'title': '流畅 360P', 'icon': None}, {'title': '清晰 540P', 'icon': None}, {'title': '标清 720P', 'icon': None}, {'title': '高清 1080P', 'icon': None}, {'title': '超清 4K', 'icon': None}]
VIP_DATA = [{'title': '流畅 360P', 'icon': 'VIP'}, {'title': '清晰 540P', 'icon': 'VIP'}, {'title': '标清 720P', 'icon': 'VIP'}, {'title': '高清 1080P', 'icon': 'VIP'}]
SVIP_DATA = [{'title': '超清 4K', 'icon': 'SVIP'}]
VIP_TIP = {'title': '高清下载为会员专属功能'}
SVIP_TIP = {'title': '超清下载为会员专属功能'}
ORIGIN_DATA = [{'title': '原片', 'icon':'VIP'}]
ORIGIN_VIP_TIP = {'title': '下载原片为会员专属功能'}

def test_a(author):
    quit_vip(author)
    # join_vip(author, type=2, flag=3)
    # join_vip(author, type=2, flag=7)
    # join_vip(author)
    pass
def test_u(user):
    # join_team(user, author, ARTICLE_ID)
    # join_vip(user)
    pass

def test_y():
    l = Login()
    l.load()
    x = l.login('13609750911')
    # x = l.login('15232324925')
    # x = l.login('18612250014')
    # x = l.login('18160986309')
    # x = l.login('18848882411')
    x.is_loaded()
    Article().load(11297151, new_article='true')


def test_z():
    '''
    https://www-test.xinpianchang.com/a11297151?from=UserProfile
    '''
    p = Article()
    p.load(11297151, new_article='true')
    p.open_download_dialog()
    # p.get_download_list()

def download(p:Article, profile, type='team', success=True):
    '''reward/team/vip/svip'''
    p.click_download_btn(profile, type)
    time.sleep(1)
    if type in ('vip', 'svip') and not success:
        # 下载失败 弹会员提示窗
        dialog = p.get_vip_only_dialog()
        # if type == 'vip':
        #     assert dialog == VIP_TIP
        # else: #type == 'svip':
        #     assert dialog == SVIP_TIP
        p.close_vip_dialog()
        time.sleep(1)
        return dialog
    else:
        # 下载成功
        with pytest.raises(NoSuchElementException):
            p.get_vip_only_dialog()

def test_1(user, author):
    '''
    赞赏下载
    登录用户
    
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': False, 'reward': True},
        # authorized_type=1,
        **{'user-agent': config.DEL}
    )
    # join_team(user, author, ARTICLE_ID)
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    p.open_download_dialog()
    time.sleep(1)
    result = p.get_download_list()
    assert result['reward']['display'] is True
    assert result['reward']['title'] == '赞赏下载'
    assert result['reward']['data'] == REWARD_DATA
    assert result['team']['display'] is False
    assert result['vip']['display'] is False
    assert result['svip']['display'] is False
    assert result['auth']['display'] is True

def test_2(author, user):
    '''
    团队下载
    非团队
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': True, 'vip': False, 'reward': False},
        authorized_type=1,
        **{'user-agent': config.DEL}
    )
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    with pytest.raises(NoSuchElementException):
        p.open_download_dialog()
    


def test_3(user, author):
    '''
    会员下载
    非会员
    
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': True, 'reward': False},
        # authorized_type=1,
        **{'user-agent': config.DEL}
    )
    # join_team(user, author, ARTICLE_ID)
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    p.open_download_dialog()
    time.sleep(1)
    result = p.get_download_list()
    assert result['reward']['display'] is False
    assert result['team']['display'] is False
    assert result['vip']['display'] is True
    assert result['svip']['display'] is True
    assert result['vip']['data'] == VIP_DATA
    assert result['svip']['data'] == SVIP_DATA
    
    assert result['auth']['display'] is True

def test_4(user, author):
    '''
    会员下载
    会员
    
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': True, 'reward': False},
        **{'user-agent': config.DEL}
    )
    # join_team(user, author, ARTICLE_ID)
    join_vip(user)
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    p.open_download_dialog()
    time.sleep(1)
    result = p.get_download_list()
    assert result['reward']['display'] is False
    assert result['team']['display'] is False
    assert result['vip']['display'] is True
    assert result['svip']['display'] is True
    assert result['vip']['data'] == VIP_DATA
    assert result['svip']['data'] == SVIP_DATA
    assert result['auth']['display'] is True

def test_5(author, user):
    '''
    团队下载
    团队成员+非vip
    =》 主态 可以下各分辨率, 原片需要vip
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': True, 'vip': False, 'reward': False},
        authorized_type=1,
        **{'user-agent': config.DEL}
    )
    join_team(user, author, ARTICLE_ID)
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    p.open_download_dialog()
    time.sleep(2)
    result = p.get_download_list()
    assert result['reward']['display'] is False
    assert result['team']['display'] is True
    assert result['vip']['display'] is True
    assert result['svip']['display'] is False
    assert result['team']['data'] == TEAM_DATA
    assert result['auth']['display'] is True

    assert result['vip']['data'] == [{'title': '原片', 'icon':'VIP'}]
    
    p.click_download_btn('原片', 'vip')
    time.sleep(2)
    assert p.get_vip_only_dialog() == {'title': '下载原片为会员专属功能'}
    assert result['auth']['display'] is False

def test_6(author, user):
    '''
    团队下载 + 赞赏下载
    非团队
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': True, 'vip': False, 'reward': True},
        authorized_type=0,
        **{'user-agent': config.DEL}
    )
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    
    p.open_download_dialog()
    time.sleep(2)
    result = p.get_download_list()
    assert result['reward']['display'] is True
    assert result['reward']['data'] == REWARD_DATA

    assert result['team']['display'] is False
    assert result['vip']['display'] is False
    assert result['svip']['display'] is False    
    
    assert result['auth']['display'] is True

def test_7(author, user):
    '''
    会员下载 + 赞赏下载
    团队
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': True, 'reward': True},
        authorized_type=0,
        **{'user-agent': config.DEL}
    )
    join_team(user, author, ARTICLE_ID)
    time.sleep(3)
    p = Article()
    p.load(ARTICLE_ID)
    
    p.open_download_dialog()
    time.sleep(2)
    result = p.get_download_list()
    assert result['reward']['display'] is True
    assert result['reward']['data'] == REWARD_DATA

    assert result['team']['display'] is False
    assert result['vip']['display'] is True
    assert result['vip']['data'] == VIP_DATA
    assert result['svip']['display'] is True    
    assert result['svip']['data'] == SVIP_DATA
    assert result['auth']['display'] is True

    for i in VIP_DATA:
        dialog = download(p, i['title'], 'vip', False)
        assert dialog == VIP_TIP

    for i in SVIP_DATA:
        dialog = download(p, i['title'], 'svip', False)
        assert dialog == SVIP_TIP

    