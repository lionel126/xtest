import resource
import time, collections, copy
from urllib import request
from uuid import uuid4
import pytest
from api import XpcApi, XpcBackend, PayAdmin, Mall
from api.xpcapi import XpcServerApi
from utils.utils import areq
# from utils.utils import areq, get_available_channel

# article_id = 11297727
# goods = [{"sku_id":f"{article_id}#2900","platform":12,"count":1}]

def x_goods(article_id=11297260, price=2900):
    return [{"sku_id":f"{article_id}#{price}","platform":12,"count":1}]
    article_ids = [i['resource']['id'] for i in XpcApi().article_list(10265312, page=2).json()['data']['list']]
    return [{"sku_id":f"{a}#2900","platform":12,"count":1} for a in article_ids]

user_id = 10265312

@pytest.fixture(scope="session")
def pay(): 
    return PayAdmin()

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

def test_order(pay):
    '''zpt下单 & 补单
    '''
    # user.zpt_trade_confirm(article_id=11297732)
    order_no = Mall.create_order(user_id=user_id, goods=x_goods()).json()['data']['order_no']
     
    # Mall.order_details(order_no)
    order = Mall.pay(order_no).json()['data']['pay']['order']
    pay.fix(order)

def test_review(pay):
    '''zpt下单 & 补单 & 审核通过
    '''
    start = 11297758
    for i in range(start, start+1):
        order_no = Mall.create_order(user_id=user_id, goods=x_goods(article_id=i)).json()['data']['order_no']
        order = Mall.pay(order_no).json()['data']['pay']['order']
        pay.fix(order)
    time.sleep(3)
    xb = XpcBackend()
    zpt_ids = [zpt['id'] for zpt in xb.zpt_list(user_ids=user_id).json()['data']['data']]
    for i in zpt_ids:
        xb.zpt_review(i)

def test_recommend():
    '''推荐消耗次数
    todo: 并发 & 不同用户(不登录&不传devied-id 认作不同用户) 
    '''
    # article_ids = [11297730, 11297729]
    zpt_ids = [2683,2684,2685,2686,2689]
    loop = 0
    count = collections.defaultdict(int)
    s = XpcApi()
    while loop < 100:        
        for page in range(1, 10):
            res = s.home_recommend(page=page)
            # accept_version < 2.1.7
            # aids = [article['data']['resource']['id'] for article in res.json()['data']['list'] if article['resource_type']==1]
            # accept_version >= 2.1.7
            zpts, aids = [], []
            for resource in res.json()['data']['children']: 
                for r in resource['children']: 
                    if 'attributes' in r['model'] and 'tags' in r['model']['attributes']:
                        for tag in r['model']['attributes'].get('tags'): 
                            if tag['type']=='zpt':
                                # zpts.append({
                                #     'article_id': r['model']['resource']['id'],
                                #     'zpt_id': tag['resource_id'] 
                                # })
                                zpts.append(tag['resource_id'])
                                aids.append(r['model']['resource']['id'])

            # print([aid in aids for aid in article_ids], zpts)
            # if article_id in aids: count += 1
            result = []
            for z in zpt_ids:
                result.append(z in zpts)
                if z in zpts: 
                    count[z] += 1
            print(result, zpts)
        loop += 1
        print(f'{loop=}: count: {dict(count)}')
    print(f'<<<<< count: {dict(count)}')

def test_log_display():
    '''展示消耗次数
    todo: 并发 & 不同用户
    '''
    zpt_ids = range(2717,2730)
    new = [2717, 2721, 2727, 2728]
    print('>>>>>>>>>>>')
    count = collections.defaultdict(int)

    loop = 0
    s = XpcApi()
    while loop < 1:
        for page in range(1, 10):
            res = s.home_recommend(page=page)
            request_id = res.headers['X-Request-Id']
            zpts = []
            for resource in res.json()['data']['children']: 
                for r in resource['children']: 
                    if 'attributes' in r['model'] and 'tags' in r['model']['attributes']:
                        for tag in r['model']['attributes'].get('tags'): 
                            if tag['type']=='zpt':
                                resource_id = tag['resource_id']
                                print(resource_id, resource_id in zpt_ids, resource_id in new if resource_id in zpt_ids else 'NA')
                                # if resource_id in zpt_ids:
                                # zpts.append(tag['resource_id'])
                                # aids.append(r['model']['resource']['id'])
                                s.log(resource_id=resource_id, request_id=request_id)
                                count[resource_id] += 1
            print(f'{count=}', flush=True)            
        loop += 1
    print(f'<<<<<<<<<{count=}')

def test_log_dislike():
    '''不感兴趣
    todo
    '''

@pytest.mark.asyncio
async def test_log_clicked():
    '''clicked
    todo
    '''
    json = {
        "event_extend": {
            "from": "首页-推荐",
            "number": "0",
            "request_id": "xpctest",
            "type": "作品通大卡片（播放器居中）"
        },
        "event_source": None,
        "event_type": "click",
        "event_value": None,
        "resource_id": "2681",
        "resource_type": "zpt"
    }
    headers = {
        'user-agent': 'NewStudios/2.0.8 (com.xinpianchang.newstudios.enterprise; build:938; Android 7.1.2)',
        'accept-version': '2.1.7'
    }
    args = [{
        'method': 'POST',
        'url': XpcApi.URL_LOG,
        'json': json,
        'headers': headers
    } for i in range(10)]
    await areq(args)
    

def test_finish_zpt():
    '''todo
    '''
    l4 = ['2708','2707','2706','2705','2703','2702','2701','2700','2699','2697','2696','2695','2693']
    ['2692','2691','2690','2688','2687','2680','2643','2566','2342','2341','2337','2332','2331','2330','2327','2326','2325','2324','2323','2322','2321','2320','2319','2318','2316','2315','2314','2313','2312','2303','2300','2295',]
    l4 = [2692,2691,2690,2688,2687,2314,]
    l4 = [2643,2566,2342,2341,2332,2327,2323,2300,2295]
    l4 = [2331, 2330, 2326, 2324, 2322, 2321, 2319, ]
    for zpt_id in l4:
        XpcServerApi.zpt_status(zpt_id, status='working', display_count='$DEL')
        XpcServerApi.zpt_status(zpt_id, status='completed')

# def test_weight():
#     '''
#     '''
#     from collections import defaultdict
#     r2 = defaultdict(int)
#     l = [{"ZptId":2676,"Weight":10},{"ZptId":2616,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2618,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2619,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2676,"Weight":10},{"ZptId":2615,"Weight":10},{"ZptId":2616,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2618,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2619,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2676,"Weight":10},{"ZptId":2615,"Weight":10},{"ZptId":2616,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2618,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2619,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2676,"Weight":10},{"ZptId":2615,"Weight":10},{"ZptId":2616,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2618,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2619,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2566,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2643,"Weight":10},{"ZptId":2676,"Weight":10},{"ZptId":2615,"Weight":10},{"ZptId":2616,"Weight":10},{"ZptId":2643,"Weight":10}]
#     r = {}
#     for i in l:
#         if i["ZptId"] in r:
#             r[i["ZptId"]] = r[i["ZptId"]] + i["Weight"]
#         else:
#             r[i["ZptId"]] = i["Weight"]

#         # if i["ZptId"] not in r2:
#         #     r2[i["ZptId"]] = 0
#         r2[i["ZptId"]] = r2[i["ZptId"]] + i["Weight"]
#     print(r)
#     print(r2)

