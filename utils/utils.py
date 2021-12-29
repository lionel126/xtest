from uuid import uuid4
from aiohttp import ClientSession
import asyncio
import logging
import logging.handlers
from requests import request
import faker
import random
from datetime import datetime, timedelta
from . import const

fake: faker.Faker = faker.Faker(['zh_CN', 'en_US'])


def get_logger(name='root', level=logging.INFO):
    log_handler = logging.handlers.TimedRotatingFileHandler(
        'logs/mallv2-test.log', when='midnight')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(message)s',
        '%b %d %H:%M:%S')
    # formatter.converter = time.gmtime  # if you want UTC time
    log_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(log_handler)
    logger.setLevel(level)
    return logger


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

# not working for list
# def varname(v, namespace):
#     for name in namespace:
#         if v is namespace[name]:
#             return name

# def replace(kwargs, *args, dk='$', s=None, flag1=True):
#     if s is None:
#         s = set()
#     for k in list(kwargs):
#         # log.info(f'>>>> in loop: kwargs.{k}: {kwargs}')
#         for idx, arg in enumerate(args):
#             if k in arg:
#                 # log.info(f'{arg}, {kwargs}')
#                 # arg[k] = kwargs.pop(k)
#                 arg[k] = kwargs[k]
#                 # log.info(f'<<<<<<<<<<args updated: {dk}.{varname(arg, locals())}.{k}')
#                 s.add(k)
#                 # 不加break 如果有重复的参数 eg: a=1, json={"a":2}, 更新完json后会再更新json内部
#                 # break
#                 if isinstance(arg[k], dict):
#                     replace(kwargs, arg, dk=f'{dk}[{idx}].{k}', s=s, flag1=False)
#     # if flag1:
#     #     log.info(f'args ignored: {set(kwargs.keys()) - s}')


def replace(kwargs, *args):
    for arg in args:
        for k in arg:
            if k in kwargs:
                arg[k] = kwargs[k]
            elif isinstance(arg[k], dict):
                replace(kwargs, arg[k])
            elif isinstance(arg[k], list):
                for ar in arg[k]:
                    replace(kwargs, ar)


def append(kwargs, d: dict, keys):
    for k, v in kwargs.items():
        if k in keys:
            # d.update({k: v})
            d[k] = v


def get_available_channel(channels: list, location: str):
    '''返回开发环境能用的channel'''
    channels = [c for c in channels if c['channelCode'] not in (
        'WX_INNER_005',
    #     # 'ZFB_WEB_005',
    #     # 'ZFB_WAP_005',
        'JD_QR_005',
    #     # 'JD_H5_005',
    #     # 'JD_WEB_005'
    )]

    channel = channels[fake.random_int(0, len(channels)-1)]

    # channel = [c for c in channels if c["channelCode"] == "JD_QR_005"][0]
    
    if channel['channelCode'] in ('ZFB_WEB_005', 'ZFB_WAP_005', 'JD_WEB_005', 'JD_H5_005'):
        channel['returnUrl'] = location
    channel['token'] = location.split('/')[-1]
    channel = {k if k != "channelCode" else "channel": v for k, v in channel.items() if k in ("token", "appId", "returnUrl", "channelCode")}
    return channel


def boss_gateway_token():
    '''参考mallv2的admin中间件'''
    import base64
    from hashlib import sha1

    userInfo = '{ "id": "1", "username": "zhangsan", "nickname": "zhangsan", "email": "zhangsan@xinpianchang.com" }'
    userInfo = 'chenshengguo'
    appSecret = 'ef34b98f9e94dbb57469491148bdeacf7fd5bd59'  # dev
    appSecret = '6732ac43a7f5ddf07135ffb579008b9947cc8a5c'  # test
    xUserToken = str(base64.b64encode(bytes(userInfo, 'utf-8')), 'utf-8') + \
        '.' + sha1(bytes(userInfo + '.' + appSecret, 'utf-8')).hexdigest()
    return xUserToken

def get_check_digit(id_number):
    """通过身份证号获取校验码"""
    check_sum = 0
    for i in range(0, 17):
        check_sum += ((1 << (17 - i)) % 11) * int(id_number[i])
    check_digit = (12 - (check_sum % 11)) % 11
    return str(check_digit) if check_digit < 10 else 'X'

def generate_id():
    """ 随机生成身份证号，sex = 0表示女性，sex = 1表示男性 """

    # 随机生成一个区域码(6位数)
    id_number = str(random.choice(list(const.AREA_INFO.keys())))
    # 限定出生日期范围(8位数)
    start, end = datetime.strptime("1960-01-01", "%Y-%m-%d"), datetime.strptime("2020-12-31", "%Y-%m-%d")
    birth_days = datetime.strftime(start + timedelta(random.randint(0, (end - start).days)), "%Y%m%d")
    id_number += str(birth_days)
    # 顺序码(2位数)
    id_number += '{:02}'.format(random.randint(1, 99))
    # 性别码(1位数)
    # id_number += str(random.randrange(sex, 10, step=2))
    id_number += str(random.randint(0, 9))
    # 校验码(1位数)
    return id_number + get_check_digit(id_number)