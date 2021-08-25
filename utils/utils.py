from uuid import uuid4
from aiohttp import ClientSession
import asyncio
import logging
from requests import request
import faker

fake = faker.Faker(['zh_CN', 'en_US'])
log = logging.getLogger(__file__)


def new_tag():
    return f'tag-{uuid4()}'

def trade_count(storeCodes):
    '''根据 storeCode list 计算trade单的数量
    '''
    # 数据库里商户对应的结算账号
    merchant = {
        "mock1": "北京新片场",
        "mock2": "北京新片场",
        "mock3": "杭州新片场",
        "mock4": "曹县新片场",
        "mock5": "北京新片场",
        "resource": "北京新片场"
    }
    s = set()
    for sc in storeCodes:
        s.add(merchant[sc])
    return len(s)

async def areq(req_kwargs_list):
    '''async request
    '''
    async with ClientSession(trust_env=True) as session:
        task = [session.request(**ka) for ka in req_kwargs_list]
        res = await asyncio.gather(*task)
        return res


def varname(v, namespace):
    for name in namespace:
        if v is namespace[name]:
            return name

def replace(kwargs, *args, dk='$', s=None, flag1=True):
    if s is None:
        s = set()
    for k in list(kwargs):
        log.info(f'>>>> in loop: {k} of kwargs: {kwargs}')
        for arg in args:
            log.info(f'^^^^^^^to update: {dk}.{varname(arg, locals())}.{k}')
            if k in arg:
                log.info(f'{arg}, {kwargs}')
                arg[k] = kwargs.pop(k)
                log.info(f'<<<<<<<<<<args updated: {dk}.{varname(arg, locals())}.{k}')
                s.add(k)
                # 不加break 如果有重复的参数 eg: a=1, json={"a":2}, 更新完json后会再更新json内部
                # break
                if isinstance(arg[k], dict):
                    replace(kwargs, arg, dk=f'{dk}.{k}', s=s, flag1=False)
    if flag1:
        log.info(
            f'args ignored: {set(kwargs.keys()) - s}')

def append(kwargs, d:dict, keys):
    for k, v in kwargs.items():
        if k in keys:
            d.update({k: v})

def get_available_channel(channels:list):
    '''返回开发环境能用的channel'''
    channels = [c for c in channels if c['channelCode'] not in ('WX_INNER_005', 'ZFB_WEB_005', 'ZFB_WAP_005', 'JD_H5_005', 'JD_WEB_005')]
    
    return channels[fake.random_int(0, len(channels)-1)]

def boss_gateway_token():
    '''参考mallv2的admin中间件'''
    import base64
    from hashlib import sha1

    userInfo = '{ "id": "1", "username": "zhangsan", "nickname": "zhangsan", "email": "zhangsan@xinpianchang.com" }'
    appSecret = 'ef34b98f9e94dbb57469491148bdeacf7fd5bd59'
    xUserToken = str(base64.b64encode(bytes(userInfo, 'utf-8')), 'utf-8') + '.' + sha1(bytes(userInfo + '.' + appSecret, 'utf-8')).hexdigest()
    return xUserToken
