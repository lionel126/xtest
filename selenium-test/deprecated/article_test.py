'''
todo 目前测试分两步：
    连接浏览器 + 登录
    刷新页面 + 获取下载列表


'''
import time
from pages.passport.login import Login 
from pages.xpc.article import Article
from test.download_permission_test import author, user, ARTICLE_ID, join_vip, join_team
from api.xpcapi import XpcApi
import config



def test_1():
    l = Login()
    l.load()
    x = l.login('13609750911')
    x.is_loaded()


def test_2():
    '''
    https://www-test.xinpianchang.com/a11297151?from=UserProfile
    '''
    p = Article()
    p.load(11297151)
    p.open_download_dialog()
    # p.get_download_list()

def test_3(user, author):
    '''
    会员下载
    非会员
    
    '''
    xauthor = XpcApi(sns_session=author)
    
    xauthor.edit_article(
        ARTICLE_ID, 
        allow_download_flags={'team': False, 'vip': True, 'reward': False},
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
    assert result['non-vip']['display'] is False
    assert result['vip']['display'] is True
    assert result['svip']['display'] is True
    vip_data = result['vip']['data']
    assert len(vip_data) == 4
    assert {d['title'] for d in vip_data} == {'360P', '540P', '720P', '1080P'}
    assert {d['icon'] for d in vip_data} == {'vip'}
    svip_data = result['svip']['data']
    assert len(svip_data) == 1
    assert svip_data[0]['title'] == '4K'
    assert svip_data[0]['icon'] == 'svip'
    assert result['auth']['display'] is True
