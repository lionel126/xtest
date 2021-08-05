# from .utils import req
import time
import sys
import config
from config import USER_ID, STORE1, BASE_URL
import logging
from requests import request
from utils.utils import replace, append
from functools import wraps, update_wrapper
import random
from utils.utils import fake

log = logging.getLogger(__file__)
MANAGER_HEADERS = {"x-user-id": "1", "x-user-token": "eyAiaWQiOiAiMSIsICJ1c2VybmFtZSI6ICJ6aGFuZ3NhbiIsICJuaWNrbmFtZSI6ICJ6aGFuZ3NhbiIsICJlbWFpbCI6ICJ6aGFuZ3NhbkB4aW5waWFuY2hhbmcuY29tIiB9.a3b6e825e26f5a87bc2e98a9c8126c7254f0f3d3"}


class Url():
    product_detail = BASE_URL + '/api/product/detail'

    # cart
    cart_list = BASE_URL + '/intranet/cart/list'
    cart_add = BASE_URL + '/intranet/cart/add'
    cart_update_quantity = BASE_URL + '/intranet/cart/updateQuantity'
    cart_select = BASE_URL + '/intranet/cart/select'
    cart_remove = BASE_URL + '/intranet/cart/remove'

    manage_coupon_create = BASE_URL + '/manage/coupon/create'
    manage_coupon_update = BASE_URL + '/manage/coupon/update'
    manage_coupon_delete = BASE_URL + '/manage/coupon/delete'
    manage_coupon_shelf = BASE_URL + '/manage/coupon/shelf'
    manage_coupon_info = BASE_URL + '/manage/coupon/info'
    manage_coupon_list = BASE_URL + '/manage/coupon/list'
    manage_coupon_offer = BASE_URL + '/manage/coupon/receive'
    manage_user_coupon_list = BASE_URL + '/manage/coupon/user/list'
    manage_coupon_info = BASE_URL + '/manage/coupon/info'
    namage_ticket_create = BASE_URL + '/manage/ticket/create'
    manage_ticket_offer = BASE_URL + '/manage/ticket/receive'

    coupon_receive = BASE_URL + '/intranet/coupon/receive'
    coupon_list = BASE_URL + '/intranet/coupon/list'
    ticket_list = BASE_URL + '/intranet/userTicket'
    ticket_info = BASE_URL + '/intranet/userTicket/{id}/info'

    trade_confirmation = BASE_URL + '/intranet/trade/confirmation'
    trade_submit = BASE_URL + '/intranet/trade/submit'
    trade_detail = BASE_URL + '/intranet/trade/detail/{tradeNO}'
    trade_token = BASE_URL + '/intranet/trade/link'
    trade_cancel = BASE_URL + '/intranet/trade/cancel/{tradeNo}'
    trade_list = BASE_URL + '/intranet/trade/list'

    pay = BASE_URL + '/intranet/trade/pay'

    #
    # order

# def req(default_req_kwargs, kwargs):
#     # log.info(kwargs)
#     if default:=kwargs.pop('default', None) is None:
#         default=default_req_kwargs
#     _kwargs = kwargs.pop('kwargs')
#     _kwargs.update(kwargs)
#     req_kwargs = update(default, _kwargs)
#     return request(**req_kwargs)

def update(dft, kwargs, dk='$', s=None, flag1=True):
    # log.info(f'flag: {flag1}, dft: {dft}, _kwargs: {kwargs}')
    if s is None:
        s = set()
    for k in dft:
        # log.info(f'>>>> in loop: {k}')
        if k in kwargs:
            dft[k] = kwargs[k]
            log.info(f'+++++++++++++++++++args updated: {dk}.{k}')
            s.add(k)
            # 不加break 如果有重复的参数 eg: a=1, json={"a":2}, 更新完json后会再更新json内部
            # break
        if isinstance(dft[k], dict):
            update(dft[k], kwargs, dk=f'{dk}.{k}', s=s, flag1=False)
    if flag1:
        log.info(
            f'---{s}--{set(kwargs.keys())}-----------args ignored: {set(kwargs.keys()) - s}')
    return dft

# class api_wrapper(object):
#     '''deprecated'''
#     def __init__(self, func):
#         self._locals = {}
#         self.func = func
#         update_wrapper(self, func) # not working??

#     def __call__(self, *args, **kwargs):
#         def tracer(frame, event, arg):
#             if event == 'return':
#                 self._locals = frame.f_locals.copy()

#         # tracer is activated on next call, return or exception
#         sys.setprofile(tracer)
#         try:
#             # trace the function call
#             self.func(*args, **kwargs)
#             res = request(
#                 **update(self._locals['__default__'], self._locals['kwargs']))
#         finally:
#             # disable tracer and replace with old one
#             sys.setprofile(None)
#         return res

    # def clear_locals(self):
    #     self._locals = {}

    # @property
    # def locals(self):
    #     return self._locals

def api_wrapper(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        _locals = {}
        def tracer(frame, event, arg):
            if event == 'return':
                _locals.update(frame.f_locals.copy())
        sys.setprofile(tracer)
        try:
            func(*args, **kwargs)
            # print(f'{_locals=}')
        finally:
            sys.setprofile(None)
        res = request(**update(_locals["__default__"], _locals['kwargs']))
        return res
    return wrap



def product_detail(method='POST', json=None):
    '''product detail
    
    :param json: [{
        'storeCode': STORE1,
        'productId': '123456'
    }]
    '''
    # if json is None:
    #     json = [{
    #         'storeCode': STORE1,
    #         'productId': '1'
    #     }]
    # replace(kwargs, json)

    return request(method=method, url=Url.product_detail, json=json)

def get_cart(method="GET", params=None, **kwargs):
    '''获取购物车列表
    :param params: Defaults to {"userId": USER_ID}
    '''
    
    if params is None:
        params = {"userId": USER_ID}
    replace(kwargs, params)
    return request(method=method, url=Url.cart_list, params=params)

def add_to_cart(method="POST", params=None, json=None, **kwargs):
    '''add sku to cart
    
    :param params: {"userId": USER_ID},
    :param json: {
            "skuId": "",
            "quantity": 1,
            "storeCode": STORE1
        }
    '''
    if params is None:
        params={"userId": USER_ID}
    if json is None:
        json = {
            "skuId": "",
            "quantity": 1,
            "storeCode": STORE1
        }
    replace(kwargs, json, params)
    return request(method=method, url=Url.cart_add, params=params, json=json)


def remove_cart_item(method="POST", params=None, json=None, **kwargs):
    '''remove item from cart
    
    :param params: {"userId": userId}, 
    :param json: {
            'cartItemIds': [],
            'isRemoveAllInvalid': False
        }
    '''
    if params is None:
        params = {"userId": USER_ID}
    if json is None:
        json = {
            'cartItemIds': [],
            'isRemoveAllInvalid': False
        }
    
    replace(kwargs, json, params)
    return request(method=method, url=Url.cart_remove, params=params, json=json)


def update_cart_item_quantity(method="POST", params=None, json=None, **kwargs):
    '''
       
    :param params: {"userId": USER_ID}, 
    :param json: {
            "cartItemId": 0,
            "quantity": 1
        }
    '''
    if params is None:
        params = {"userId": USER_ID}
    if json is None:
        json = {
            "cartItemId": 0,
            "quantity": 1
        }
    replace(kwargs, json, params)
    return request(method=method, url=Url.cart_update_quantity, params=params, json=json)


def select_cart_item(method="POST", params=None, json=None, **kwargs):
    '''{
        "method": "post",
        "url": Url.cart_select, 
        "params": {"userId": USER_ID}, 
        "json": {
            "cartItemIds": [],
            "selected": True,
        }
    }'''
    if params is None:
        params = {'userId': USER_ID}
    if json is None:
        json = {
            "cartItemIds": [],
            "selected": True,
        }
    replace(kwargs, json, params)
    return request(method=method, url=Url.cart_select, params=params, json=json)


def create_coupon(method="POST", headers=None, json=None, **kwargs):
    """create coupon
    :param json: Defaults to {
            "name": "coupon_from_test",
            "brief": "test brief",
            "couponType": "money_off" / "percent_off",
            "couponValue": 5,
            "effectiveAt": int((time.time() - 3600) * 1000),
            "expiredAt": int((time.time() + 3600 * 24) * 1000),
            "duration": 0,
            "quantity": -1,
            "maxReceived": -1,
            "unusedLimit": -1,
            "thresholdPrice": 100,
            "sentType": 0,
            "receiveType": 0,
            "userTag": "tag1,tag2",
            "returnable": False,
            "rangeType": 1,
            "rangeStoreCode": config.STORE1,
            "rangeValue": "value",
        }
    """
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    if json is None:
        json = {
            "name": fake.text(max_nb_chars=30),
            "brief": fake.sentence(nb_words=10),
            "couponType": "money_off",
            "couponValue": 5,
            "effectiveAt": int((time.time() - 3600) * 1000),
            "expiredAt": int((time.time() + 600 + 3600 * 24 * random.randint(0, 7)) * 1000),
            "duration": 0,
            "quantity": -1,
            "maxReceived": -1,
            "unusedLimit": -1,
            "thresholdPrice": 100,
            "sentType": 0,
            "receiveType": 0,
            "userTag": "tag1,tag2",
            "returnable": False,
            "rangeType": 1,
            "rangeStoreCode": config.STORE1,
            "rangeValue": "value",
        }
    replace(kwargs, json, headers)
    return request(method=method, url=Url.manage_coupon_create, headers=headers, json=json)


def coupon_shelf(method="POST", headers=None, json=None, **kwargs):
    '''{
        "method": "post",
        "url": Url.manage_coupon_shelf, 
        "json":{
            "code": "",
            "action": "on"
        }, 
        "headers": MANAGER_HEADERS.copy()
    }'''
    if json is None:
        json = {
            "code": "",
            "action": "on"
        }
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    replace(kwargs, json, headers)
    return request(method=method, url=Url.manage_coupon_shelf, headers=headers, json=json)


def offer_coupon(method="POST", headers=None, json=None, **kwargs):
    '''
    :param headers: MANAGER_HEADERS.copy()
    :param json: {
            "source": "test",
            "code": "coupon-code",
            "receives": [
                {"userId": USER_ID, "count": 1}
            ]
        }
    '''
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    if json is None:
        json = {
            "source": "test",
            "code": "coupon-code",
            "receives": [
                {"userId": USER_ID, "count": 1}
            ]
        }
    replace(kwargs, json, headers)
    return request(method=method, url=Url.manage_coupon_offer, headers=headers, json=json)


def update_coupon(method="POST", headers=None, json=None, **kwargs):
    '''
    :param headers: MANAGER_HEADERS.copy()
    :param json: {
            "id": 0,
            "name": "coupon_from_test",
            "brief": "test brief",
            "couponType": "money_off",
            "couponValue": 5,
            "effectiveAt": int((time.time() - 3600) * 1000),
            "expiredAt": int((time.time() + 3600 * 24) * 1000),
            "duration": 0,
            "quantity": -1,
            "maxReceived": -1,
            "unusedLimit": -1,
            "thresholdPrice": 100,
            "sentType": 0,
            "receiveType": 0,
            "userTag": "tag1,tag2",
            "returnable": False,
            "rangeType": 1,
            "rangeStoreCode": config.STORE1,
            "rangeValue": "value",
        }
    '''
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    if json is None:
        json = {
            "id": 0,
            "name": "coupon_from_test",
            "brief": "test brief",
            "couponType": "money_off",
            "couponValue": 5,
            "effectiveAt": int((time.time() - 3600) * 1000),
            "expiredAt": int((time.time() + 3600 * 24) * 1000),
            "duration": 0,
            "quantity": -1,
            "maxReceived": -1,
            "unusedLimit": -1,
            "thresholdPrice": 100,
            "sentType": 0,
            "receiveType": 0,
            "userTag": "tag1,tag2",
            "returnable": False,
            "rangeType": 1,
            "rangeStoreCode": config.STORE1,
            "rangeValue": "value",
        }
    replace(kwargs, json, headers)
    return request(method=method, url=Url.manage_coupon_update, headers=headers, json=json)



def coupon_list(method="GET", headers=None, params=None, **kwargs):
    '''get coupon list

    :param method: get
    :param url: Url.manage_coupon_list
    :param params: {
            "page": 1,
            "size": 20,
            "name": "",
            "couponType": "",
            "status": ""
        }
    '''
    url = Url.manage_coupon_list
    if params is None:
        params = {}
    if headers is None:
        headers = MANAGER_HEADERS.copy()
        
    replace(kwargs, params, headers)
    append(kwargs, params, ('page', 'pageSize', 'name', 'couponType', 'status'))
    return request(method=method, url=url, headers=headers, params=params)


def manage_coupon_list(method='GET', headers=None, params=None, **kwargs):
    '''
    :param params: {
            "page": 1,
            "pageSize": 20,
            "sourceType": "",
            "userId": "",
            "couponCode": ""
            "status": ""
        }, Defaults to {}
    }'''

    if params is None:
        params = {}
    if headers is None:
        headers = MANAGER_HEADERS.copy()

    append(kwargs, params, ('page', 'pageSize', 'sourceType', 'userId', 'couponCode', 'status'))
    
    return request(method=method, url=Url.manage_user_coupon_list, headers=headers, params=params)



def user_coupon_list(method="GET", params=None, **kwargs):
    '''
        "method": "get",
        "url": Url.coupon_list, 
        "params": {
            "userId": USER_ID,
            "page": 1,
            "size": 20,
            "status": ""
        }
    }'''
    if params is None:
        params = {"userId": USER_ID}
    # __default__ = {
    #     "method": "get",
    #     "url": Url.coupon_list,
    #     "params": {
    #         "userId": USER_ID,
    #     }
    # }
    replace(kwargs, params)
    append(kwargs, params, ('page', 'pageSize', 'status'))
    return request(method=method, url=Url.coupon_list, params=params)
    

def manage_coupon_info(method="GET", params=None, headers=None, **kwargs):
    '''
    :param params: {
            "code": "",
            "version": 0,
            "allVersion": False
        },
    :param headers: MANAGER_HEADERS
    '''
    if params is None:
        params = {
            "code": "",
            "version": 0,
            "allVersion": False
        }
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    replace(kwargs, params, headers)
    return request(method=method, url=Url.manage_coupon_info, headers=headers, params=params)


def receive_coupon(method="POST", params=None, json=None, **kwargs):
    """领取优惠券
    :param params: {"userId": USER_ID}
    :param json: {"code": ""}
    """
    if params is None:
        params = {"userId": USER_ID}

    if json is None:
        json = {"code": ""}

    replace(kwargs, json, params)
    return request(
        method=method,
        url=Url.coupon_receive,
        params=params,
        json=json
    )


# @api_wrapper
# def manage_create_ticket(**kwargs):
#     """create ticket

#     :param json: dict. Defaults to {
#             "name": "test ticket name",
#             "brief": "test ticket brief",
#             "storeCode": STORE1,
#             "promotionTag": "test-ticket-tag",
#             "ticketType": "package",
#             "ticketValue": 100,
#             "duration": 3600 * 24 * 30 * 1000
#         }
#     :return: :class:`Response <Response>` object
#     :rtype: requests.Response
#     """
#     '''{
#         "method": "post",
#         "url": Url.ticket_create,
#         "headers": MANAGER_HEADERS.copy()
#         "json": {
#             "name": "test ticket name",
#             "brief": "test ticket brief",
#             "storeCode": STORE1,
#             "promotionTag": "test-ticket-tag",
#             "ticketType": "package",
#             "ticketValue": 100,
#             "duration": 3600 * 24 * 30 * 1000
#         }
#     }'''
#     __default__ = {
#         "method": "post",
#         "url": Url.namage_ticket_create,
#         "headers": MANAGER_HEADERS.copy()
#         "json": {
#             "name": "test ticket name",
#             "brief": "test ticket brief",
#             "storeCode": STORE1,
#             "promotionTag": "test-ticket-tag",
#             "ticketType": "package",
#             "ticketValue": 100,
#             "duration": 3600 * 24 * 30 * 1000
#         }
#     }

def manage_create_ticket(method='POST', headers=None, json=None, **kwargs):
    """create ticket template

    :param method: str
    :param headers: dict|None
    :param json: dict|None default {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        }
    """
    url = Url.namage_ticket_create
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    if json is None:
        json = {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        }
    replace(kwargs, json, headers)
    return request(method=method, url=url, headers=headers, json=json)
    

def offer_ticket(method="POST", headers=None, json=None, **kwargs):
    """offer ticket
    :param json: {
            "ticketId": 0,
            "receives": [
                {"userId": USER_ID, "count": 1}
            ]
        }
    """
    if headers is None:
        headers = MANAGER_HEADERS.copy()
    if json is None:
        json = {
            "ticketId": 0,
            "receives": [
                {"userId": USER_ID, "count": 1}
            ]
        }
    replace(kwargs, json, headers)
    return request(method=method, url=Url.manage_ticket_offer, headers=headers, json=json)


def ticket_list(method="GET", params=None, **kwargs):
    '''{
        "method": "get",
        "url": Url.ticket_list,
        "params": {
            "userId": USER_ID,
            "page": 1,
            "pageSize": 20
        }
    }'''
    if params is None:
        params = {
            "userId": USER_ID,
        }
    replace(kwargs, params)
    append(kwargs, params, ("page", "pageSize"))
    return request(method=method, url=Url.ticket_list, params=params)


def ticket_info():
    pass

def trade_confirmation(method="POST", params=None, json=None, **kwargs):
    '''trade confirm

    :param url: Url.trade_confirmation, 
    :param params: {"userId": USER_ID}, 
    :param json: {
            "skus": [],
            "coupons": [],
            "disableCoupons": [],
            "disableAllCoupons": False,
            "disableTicket": False,
            "promotions": [],
            "dry": False
        }
    '''
    
    params = {"userId": USER_ID}
    json = {
            "skus": [],
            "coupons": [],
            "disableCoupons": [],
            "disableAllCoupons": False,
            "disableTicket": False,
            "promotions": [],
            "dry": False
        }
    replace(kwargs, json, params)
    return request(method=method, url=Url.trade_confirmation, params=params, json=json)



def trade_submit(method="POST", params=None, json=None, **kwargs):
    '''trade submit 
    :param params: {"userId": USER_ID}, 
    :param json: {
            "skus": [],
            "coupons": [],
            "disableCoupons": [],
            "disableAllCoupons": False,
            "disableTicket": False,
            "promotions": [],
            "totalPriceViewed": 0
        }
    '''
    if params is None:
        params = {"userId": USER_ID}
    if json is None:
        json ={
            "skus": [],
            "coupons": [],
            "disableCoupons": [],
            "disableAllCoupons": False,
            "disableTicket": False,
            "promotions": [],
            "totalPriceViewed": 0
        }
    replace(kwargs, json, params)
    return request(method=method, url=Url.trade_submit, params=params, json=json)


def trade_token(method='POST', params=None, json=None, **kwargs):
    '''obtain trade token
    :param method: "post",
    :param url: Url.trade_token,
    :param params: {"userId": USER_ID},
    :param json: {"tradeNo": '1'}
    '''
    if params is None:
        params = {"userId": USER_ID}
    if json is None:
        json = {"tradeNo": '1'}
    replace(kwargs, json, params)
    return request(method=method, url=Url.trade_token, params=params, json=json)


def trade_detail(method="GET", tradeNo="", params=None, **kwargs):
    '''
    :param url: Url.trade_detail.format(tradeNO=""), 
    :param params: {
            "userId": USER_ID, 
            "token": ""
        }
    }'''
    # tradeNo = kwargs.get('tradeNo', "")
    url = Url.trade_detail.format(tradeNO=tradeNo)
    
    if params is None:
        params = {"userId": USER_ID}
    replace(kwargs, params)
    append(kwargs, params, ("token"))
    return request(method=method, url=url, params=params)


def trade_list(method="GET", params=None, **kwargs):
    '''trade list of one
    :param params: Defaults to {"userId": USER_ID}
    '''
    if params is None:
        params = {"userId": USER_ID,}
    
    replace(kwargs, params)
    append(kwargs, params, ("page", "pageSize"))
    return request(method=method, url=Url.trade_list, params=params)


def trade_cancel(method="POST", tradeNo="", params=None, **kwargs):
    '''cancel trade
    :param url: Url.trade_cancel.format(tradeNo=""), 
    :param params: {"userId": USER_ID}
    '''
    # tradeNo = kwargs.get("tradeNo", "")
    url = Url.trade_cancel.format(tradeNo=tradeNo)
    if params is None:
        params = {"userId": USER_ID}
    replace(kwargs, params)
    return request(method=method, url=url, params=params)


def pay(method="POST", json=None, **kwargs):
    """
    :param json: dict {"channel", "token", "appId"}
    """
    if json is None:
        json = {}
    append(kwargs, json, ("channel", "token", "appId"))
    return request(method=method, url=Url.pay, json=json)
