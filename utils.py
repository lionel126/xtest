import aiohttp
import requests
# from functools import partial
from requests.sessions import session
from config import BASE_URL, USER_ID, STORE1
import config
import time
from uuid import uuid4
from requests import get, post, put, delete, patch
import ssl
import os
from aiohttp import ClientSession
import asyncio

# DEFAULT_REQ_KWARGS = {"verify": False}

# get = partial(getattr(requests, 'get'), **DEFAULT_REQ_KWARGS)
# post = partial(getattr(requests, 'post'), **DEFAULT_REQ_KWARGS)
# put = partial(getattr(requests, 'put'), **DEFAULT_REQ_KWARGS)
# delete = partial(getattr(requests, 'delete'), **DEFAULT_REQ_KWARGS)
# patch = partial(getattr(requests, 'patch'), **DEFAULT_REQ_KWARGS)


DJANGO_BASE = 'https://t.vmovier.cc'
MANAGER_HEADERS = {"x-user-id": "1", "x-user-token": "eyAiaWQiOiAiMSIsICJ1c2VybmFtZSI6ICJ6aGFuZ3NhbiIsICJuaWNrbmFtZSI6ICJ6aGFuZ3NhbiIsICJlbWFpbCI6ICJ6aGFuZ3NhbkB4aW5waWFuY2hhbmcuY29tIiB9.a3b6e825e26f5a87bc2e98a9c8126c7254f0f3d3"}
PAY_ADMIN_BASE = 'https://pay-admin-wkm.vmovier.cc'

sslcontext = ssl.create_default_context(cafile=os.path.join(os.path.dirname(__file__), './tmp/rootCA.crt'))

aiohttp_proxy = dict(proxy="http://192.168.8.27:30001", ssl=sslcontext) if config.DEBUG else {}
# aiohttp_proxy = {}

class Url():
    # cart
    cart_list = BASE_URL + '/intranet/cart/list'
    cart_add = BASE_URL + '/intranet/cart/add'
    cart_update_quantity = BASE_URL + '/intranet/cart/updateQuantity'
    cart_select = BASE_URL + '/intranet/cart/select'
    cart_remove = BASE_URL + '/intranet/cart/remove'

    manage_coupon_create = BASE_URL + '/manage/coupon/create'
    manage_coupon_update = BASE_URL + '/manage/coupon/update'
    manage_coupon_delete =  BASE_URL + '/manage/coupon/delete'
    manage_coupon_shelf = BASE_URL + '/manage/coupon/shelf'
    manage_coupon_info = BASE_URL + '/manage/coupon/info'
    manage_coupon_list = BASE_URL + '/manage/coupon/list'
    manage_coupon_offer = BASE_URL + '/manage/coupon/receive'
    manage_coupon_list = BASE_URL + '/manage/coupon/user/list'
    coupon_info = BASE_URL + '/manage/coupon/info'
    ticket_create = BASE_URL + '/manage/ticket/create'
    ticket_offer = BASE_URL + '/manage/ticket/receive'

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


class Data():
    '''storeCode 暂时没用
    todo：接了真正的商品库，每个接口都应该传storeCode
    '''

    _CREATE_PRODUCT = DJANGO_BASE + '/{storeCode}/product'
    _DELETE_SKUS = DJANGO_BASE + '/skus'
    _GET_SKUS = DJANGO_BASE + '/skus'
    _UPDATE_SKU = DJANGO_BASE + '/skus'
    _CHANGE_SKUS_STATUS = DJANGO_BASE + '/skus/status'
    _CHANGE_SKU = DJANGO_BASE + '/sku/{skuId}'
    


    @staticmethod
    def create_product(json=None, storeCode=config.STORE1):
        '''storeCode没有用：目前只有一个mock server
        '''
        r = post(Data._CREATE_PRODUCT.format(storeCode=storeCode), json=json)
        assert r.status_code == 200
        return r

    @staticmethod
    def delete_skus(json=[]):
        # r = delete(Data._DELETE_SKUS, json=json)
        r = post(Data._DELETE_SKUS, json=json)
        assert r.status_code == 200
        return r

    @staticmethod
    def get_skus(size=10, page=0, status='on_sale', storeCode=STORE1, skus=None, **kwargs):
        '''default: status = on_sale
        商品库暂时没提供商品列表接口
        预留storeCode 暂时无用。多个mock商品库 实际连接同一个mock服务：相同商品 不同storeCode
        '''
        if status:
            kwargs['status'] = status
        params = {"page": page, "size": size, **kwargs}
        if skus:
            params['skus'] = skus
        r = get(Data._GET_SKUS, params=params)
        assert r.status_code == 200
        return r

    # @staticmethod
    # def sku_status(jsn):
    #     '''deprecated: 批量获取或修改skus status
    #     [], {}
    #     '''
    #     r = post(Data._CHANGE_SKUS_STATUS, json=jsn)
    #     assert r.status_code == 200
    #     return r

    # @staticmethod
    # def update_sku(skuId, **kwargs):
    #     '''修改sku
    #     '''
    #     r = post(Data._CHANGE_SKU.format(skuId=skuId), json=kwargs)
    #     assert r.status_code == 200
    #     return r
    @staticmethod
    def update_sku(jsn):
        r = post(Data._UPDATE_SKU, json=jsn)
        assert r.status_code == 200
        return r



class MallV2DB():
    _DELETE_USER_COUPONS = DJANGO_BASE + '/user/{userId}/coupons'
    _DELETE_USER_TICKETS = DJANGO_BASE + '/user/{userId}/tickets'

    @staticmethod
    def delete_coupons(userId=USER_ID):
        r = delete(MallV2DB._DELETE_USER_COUPONS.format(userId=userId))
        assert r.status_code == 200
        return r

    @staticmethod
    def delete_tickets(userId=USER_ID):
        r = delete(MallV2DB._DELETE_USER_TICKETS.format(userId=userId))
        assert r.status_code == 200
        return r

class MallV2():

    @staticmethod
    def get_cart(userId=USER_ID):

        r = get(Url.cart_list, params={"userId": userId})
        # assert r.status_code == 200
        return r

    @staticmethod
    def add_to_cart(sku, userId=USER_ID, store=config.STORE1, quantity=1):

        r = post(Url.cart_add, params={"userId": userId}, json={
            "skuId": sku,
            "quantity": quantity,
            "storeCode": store
        })
        # assert r.status_code == 200
        return r

    @staticmethod
    def remove_cart_item(items_to_remove, userId=USER_ID):

        r = post(Url.cart_remove, params={"userId": userId}, json={
            'cartItemIds': items_to_remove,
            # 'isRemoveAllInvalid': True
        })
        # assert r.status_code == 200
        return r

    @staticmethod
    def remove_invalid(userId=USER_ID):
        '''
        '''

        r = post(Url.cart_remove, params={"userId": userId}, json={
            # 'cartItemIds': items_to_remove,
            'isRemoveAllInvalid': True
        })
        # assert r.status_code == 200
        return r

    @staticmethod
    def update_cart_item_quantity(cartItemId, quantity, userId=USER_ID):

        return post(Url.cart_update_quantity, params={"userId": userId}, json={
            "cartItemId": cartItemId,
            "quantity": quantity
        })

    @staticmethod
    def select_cart_item(cartItemIds, selected=True, userId=USER_ID):

        return post(Url.cart_select, params={"userId": userId}, json={
            "cartItemIds": cartItemIds,
            "selected": selected,
        })

    @staticmethod
    def create_coupon(coupon={}, mode='update'):
        '''
        Parameters:
        -----------
        couponType:str
            money_off | percent_off
        couponValue:int
        rangeType:
            0 SPU;1: SKU;2:promotion_tag
        rangeStoreCode:
            商品库code 当range_type 为spu sku时需要传，promotion_tag 可不传
        rangeValue:

        effectiveAt:int    expiredAt:int
            默认当时生效 有效期一天
        quantity:int
            default: -1 不限制
        maxReceived:int
            default: -1 不限制
        sentType	int	O	优惠券发放形式 0:可发放可领取;1:仅发放;2:仅领取
        receiveType
        userTag
        returnable
        rangeType
        rangeStoreCode
        rangeValue
        '''
        if mode == 'update':

            coupon = {
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
            } | coupon
            # 对此接口 null  等同于 没有？ 先删了确保“不传rangeStoreCode”
            # if coupon['rangeStoreCode'] is None:
            #     del coupon['rangeStoreCode']
            # coupon = {k: v for k, v in coupon.items() if v is not None}
        return post(Url.manage_coupon_create, headers=MANAGER_HEADERS, json=coupon)

    @staticmethod
    def coupon_shelf(coupon_code, action):
        '''
        '''
        r = post(Url.manage_coupon_shelf, json={
            "code": coupon_code,
            "action": action
        }, headers=MANAGER_HEADERS)
        return r

    @staticmethod
    def offer_coupon(code, receives=[{"userId": USER_ID, "count": 1}], source="test"):
        return post(Url.manage_coupon_offer,
                    headers=MANAGER_HEADERS,
                    json={
                        "source": source,
                        "code": code,
                        "receives": receives
                    })

    @staticmethod
    def update_coupon(**kwargs):
        # kwargs.update({"code": code})
        r = post(Url.manage_coupon_update,
                 headers=MANAGER_HEADERS,
                 json=kwargs
                 )
        return r

    @staticmethod
    def coupon_list(userId=USER_ID, page=1, size=20, status=None):
        '''
        '''
        params = {
            "userId": userId,
            "page": page,
            "size": size,
        }
        if status:
            params = params | {"status": status}
        return get(Url.coupon_list, params=params)

    @staticmethod
    def coupon_info(coupon_id, userId=USER_ID):
        '''
        '''
        return get(Url.coupon_info.format(id=coupon_id), params={"userId": userId})

    @staticmethod
    def receive_coupon(code, userId=USER_ID):
        return post(Url.coupon_receive, params={"userId": userId}, json={
            "code": code
        })

    @staticmethod
    def create_ticket(**kwargs):
        ticket = {
            "name": "test ticket name",
            "brief": "test ticket brief",
            "storeCode": STORE1,
            "promotionTag": "test-ticket-tag",
            "ticketType": "package",
            "ticketValue": 100,
            "duration": 3600 * 24 * 30 * 1000
        }
        return post(
            Url.ticket_create,
            headers=MANAGER_HEADERS,
            json=ticket | kwargs
        )

    @staticmethod
    def offer_ticket(ticketId, receives=[{"userId": USER_ID, "count": 1}]):
        r = post(
            Url.ticket_offer,
            headers=MANAGER_HEADERS,
            json={
                "ticketId": ticketId,
                "receives": receives
            }
        )
        return r

    @staticmethod
    def ticket_list(userId=USER_ID):
        return get(Url.ticket_list, params={"userId": userId})

    @staticmethod
    def ticket_info():
        pass

    @staticmethod
    def trade_confirmation(skus, userId=USER_ID, coupons=[], disableCoupons=[], disableAllCoupons=False, disableTicket=False, promotions=[], storeCode=STORE1):
        # 默认storeCode
        for sku in skus:
            if "storeCode" not in sku and storeCode:
                sku["storeCode"] = storeCode

        return post(Url.trade_confirmation, params={"userId": userId}, json={
            "skus": skus,
            "coupons": coupons,
            "disableCoupons": disableCoupons,
            "disableAllCoupons": disableAllCoupons,
            "disableTicket": disableTicket,
            "promotions": promotions
        })

    @staticmethod
    def trade_submit(skus, totalPriceViewed, userId=USER_ID, coupons=[], disableCoupons=[], disableAllCoupons=False, promotions=[]):

        return post(Url.trade_submit, params={"userId": userId}, json={
            "skus": skus,
            "coupons": coupons,
            "disableCoupons": disableCoupons,
            "disableAllCoupons": disableAllCoupons,
            "promotions": promotions,
            "totalPriceViewed": totalPriceViewed
        })

    @staticmethod
    def trade_token(tradeNo, userId=USER_ID):
        return post(
            Url.trade_token,
            params={"userId": userId},
            json={"tradeNo": tradeNo}
        )

    @staticmethod
    def trade_detail(tradeNO, token, userId=USER_ID):
        return get(Url.trade_detail.format(tradeNO=tradeNO), params={"userId": userId, "token": token})

    @staticmethod
    def trade_list(userId=USER_ID, pageSize=20, page=1):
        return get(Url.trade_list, params=dict(userId=USER_ID, page=page, pageSize=pageSize))

    @staticmethod
    def trade_cancel(tradeNo, userId=USER_ID):
        return post(Url.trade_cancel.format(tradeNo=tradeNo), params={"userId": userId})


    @staticmethod
    def pay(**kwargs):
        return post(Url.pay, json=kwargs)

session_pay_admin = requests.Session()
class PayAdmin():
    

    def __init__(self):
        if self._get_user().status_code == 403:
            self._login()


    def _get_user(self):
        return session_pay_admin.get(f'{PAY_ADMIN_BASE}/api/current/user')
    def _login(self):
        session_pay_admin.post(f'{PAY_ADMIN_BASE}/login', {"email": "chenshengguo@xinpianchang.com", "password": "123456"})

    
    def fix(self, order_no):
        '''补单
        '''
        session_pay_admin.get(f'{PAY_ADMIN_BASE}/api/trade/fix?order_no={order_no}')

    def refund(self, order_no):
        '''退款
        '''
        session_pay_admin.get(f'{PAY_ADMIN_BASE}/api/trade/refund?order_no={order_no}&amount_refund=1')
        



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
    async with ClientSession() as session:
        task = [session.request(**req_kwargs | aiohttp_proxy) for _ in range(concurrency_count)]
        res = await asyncio.gather(*task)
        return res