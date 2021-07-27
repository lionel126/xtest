from uuid import uuid4
from aiohttp import ClientSession
import asyncio
import logging
from requests import request

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
    }
    s = set()
    for sc in storeCodes:
        s.add(merchant[sc])
    return len(s)

async def areq(concurrency_count, req_kwargs):
    '''async request
    '''
    async with ClientSession(trust_env=True) as session:
        task = [session.request(**req_kwargs) for _ in range(concurrency_count)]
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
        # log.info(f'>>>> in loop: {k}')
        for arg in args:
            if k in arg:
                arg[k] = kwargs.pop(k)
                log.info(f'+++++++++++++++++++args updated: {dk}.{varname(arg, locals())}.{k}')
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