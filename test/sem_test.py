import copy
from datetime import datetime, timedelta
import pytest
from api import XpcApi, XpcBackend, MallV2, PayAdmin
from utils.utils import areq, get_available_channel, replace



def date(delta=0):
    d = timedelta(hours=1+delta) if int(datetime.now().strftime('%M')) < 45 else timedelta(hours=2+delta)
    return datetime.strftime(datetime.now() + d, "%Y-%m-%d %H:00:00")
    
# 可用时间段 整点前15分钟内不可买
# delta = timedelta(hours=1) if int(datetime.now().strftime('%M')) < 45 else timedelta(hours=2)
# d = datetime.strftime(datetime.now() + delta, "%Y-%m-%d %H:00:00")

def modify(d, **kwargs):
    '''两层替换 
    todo: 递归？
    '''
    rst = copy.deepcopy(d)
    # if kwargs:
    #     for k, v in d.items():
    #         if k in kwargs:
    #             rst[k] = kwargs[k]
    #         if isinstance(v, dict):
    #             for kk in v:
    #                 if kk in kwargs:
    #                     rst[k][kk] = kwargs[kk]
    replace(kwargs, rst)
    return rst

def pay(location):
    tradeNo, token = location.split('/')[-2:]
    data = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']
            
    # channel = data['channelList'][random.randint(0, len(data['channelList'])-1)]
    channel = get_available_channel(data['channelList'], location)
    price = data['price']
    
    r = MallV2.pay(**channel).json()
    if price == 0:
        assert r['status'] == 6104
    else:
        assert r['status'] == 0
        PayAdmin().fix(r['data']['order'])

@pytest.fixture
def user():
    app = XpcApi('15600455126')
    yield app
    app.logout()

@pytest.fixture
def user2():
    app = XpcApi('18514591425')
    yield app
    app.logout()

def test_sem_keywords(user:XpcApi):
    user.sem_keywords(10626720)

def test_sem_order_list(user:XpcApi):
    user.sem_order_list()

def test_submit_with_lots_time(user:XpcApi):
    '''多时间段下单'''
    date_list = [datetime.strftime(datetime.now() + timedelta(hours=2+i), "%Y-%m-%d %H:00:00") for i in range(30 * 24)]
    res = user.sem_submit(article_id=11297733, keyword_id=2, position=11, date_list=date_list)
    
def test_submit_by_team_member(user:XpcApi):
    '''团队成员下单sem'''    
    res = user.sem_submit(article_id=10653543, keyword_id=3, position=15, date_list=[date()])
    assert res.status_code == 200
    j = res.json()
    assert j['message'] == 'OK'
    assert j['status'] == 0

def test_submit_with_others_article(user:XpcApi):
    '''不能购买他人作品sem'''    
    res = user.sem_submit(article_id=10657850, keyword_id=2, position=11, date_list=[date()])
    assert res.status_code == 400
    j = res.json()
    assert j['message'] == '不能推广别人的作品'
    assert j['status'] == -1    

def test_submit_2(user:XpcApi):
    '''用户列表多个作品 串行下单并支付
    '''
    articles = []
    page, keyword_id = 3, 3
    positions = [11, 15, 19]
    while temp:= user.article_list(user.user_id, page=page).json()['data']['list']:
        articles.extend(temp)
        page += 1
        # 只提交首页数据
        break
    for i, a in enumerate(articles):
        res = user.sem_submit(article_id=a['resource']['id'], keyword_id=keyword_id+i//3, position=positions[i%3], date_list=[date(60)])
        if res.status_code == 200:
            location = res.json()['data']['trade_cashier_link']
            pay(location)

@pytest.mark.asyncio
async def test_async_submit(user:XpcApi, user2:XpcApi):
    '''并发下单
    '''    
    template = {
        'method': 'POST',
        'url': XpcApi.URL_SEM_SUBMIT,
        'json': {
            "article_id": 11297162, 
            "keyword_id": 594, 
            "position": 11,
            "date_list": [date()]
        },
        'headers': user.headers
    }
    
    args = [
        template,
        modify(template, position=15),
        modify(template, keyword_id=595),
        modify(template, date_list=[date(1)]),
        modify(template, article_id=11296302, headers=user2.headers),
        modify(template, article_id=11296302, headers=user2.headers, date_list=[date(2)]),
        modify(template, article_id=11296302, headers=user2.headers, position=19),
        modify(template, article_id=11296302, headers=user2.headers, keyword_id=596),
    ]
    res = await areq(args)
    

def test_sem_orders():
    xb = XpcBackend()
    xb.sem_order_list()