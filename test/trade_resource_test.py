from utils.utils import get_available_channel, get_logger
from api import MallV2, MallV2DB, Search, PayAdmin, Url
from utils.utils import areq
from config import STORE_RESOURCE
import random
import pytest
import copy
import math
import time

log = get_logger(__name__)

class TestResourceTrade():
    """
    
    
    """
    
    @pytest.mark.parametrize('vendor', [
        "pond5", "vfine", "xpc", None
    ])
    def test_price_gt_0(self, vendor):
        for i in range(1, 10):
            # 如果没有 价格>0 的结果，翻页查询
            r = Search.query(vendor=vendor, page=i).json()['list'] if vendor else Search.query(page=i).json()['list']
            pids = [{"productId": p['productId'], "storeCode": STORE_RESOURCE} for p in r]
            products = MallV2.product_detail(json=pids[:]).json()['data']

            skus = [{
                "skuId": sku['skuId'],
                "quantity": 1,
                "storeCode": STORE_RESOURCE
            } for p in products for _, sku in p['data']['productSkuMap'].items() if sku['price']>0]
            if skus: break
        skus=[random.choice(skus)]
        totalPrice = MallV2.trade_confirmation(skus=skus).json()['data']['result']['totalPrice']
        tradeNo = MallV2.trade_submit(skus=skus, totalPriceViewed=totalPrice).json()['data']['trade'][0]
        location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
        token = location.split('/')[-1]
        channels = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']['channelList']
        # channel = channels[random.randint(0, len(channels)-1)]
        channel = get_available_channel(channels, location)
        # payload = {
        #     "channel": channel['channelCode'],
        #     "token": token,
        #     "appId": channel['appId'],
        # }
        r = MallV2.pay(**channel)
        PayAdmin().fix(r.json()['data']['order'])

    # def test_price_0(self):
    #     """now 没有price=0的商品？？"""
    #     for i in range(1, 100):
    #         pids = [{"productId": p['productId'], "storeCode": STORE_RESOURCE}
    #                 for p in Search.query(page=i).json()['list']]
    #         products = MallV2.product_detail(json=pids[:]).json()['data']
    #         #todo: not sure if it's empty
    #         skus = [{
    #             "skuId": sku['skuId'],
    #             "quantity": 1,
    #             "storeCode": STORE_RESOURCE
    #         } for p in products for _, sku in p['data']['productSkuMap'].items() if sku['price'] == 0]
    #         if skus: break    
    #     # 价格为0
    #     skus=[skus[0]]
    #     totalPrice = MallV2.trade_confirmation(skus=skus).json()['data']['result']['totalPrice']
    #     tradeNo = MallV2.trade_submit(skus=skus, totalPriceViewed=totalPrice).json()['data']['trade'][0]
    #     location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
    #     token = location.split('/')[-1]
    #     status = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']['status']
    #     assert status == 'succeed'

    @pytest.mark.asyncio
    async def test_x(self):
        """开发环境是这个期望 
        测试环境不同 """
        userId = 10007000
        total_reqs = 100
        reqs_per_user = 3
        
        # clear user coupons & tickets
        for i in range(math.ceil(total_reqs/reqs_per_user)):
            u = userId + i
            MallV2DB.delete_user_coupons(u)
            MallV2DB.delete_user_tickets(u)
        # 发优惠券
        coupons = [
            {
                "name": "coupon_from_test",
                "brief": "test brief",
                "couponType": "money_off",
                "couponValue": 1,
                "effectiveAt": int((time.time() - 3600) * 1000),
                "expiredAt": int((time.time() + 3600 * 24) * 1000),
                "duration": 0,
                "quantity": -1,
                "maxReceived": -1,
                "unusedLimit": -1,
                "thresholdPrice": 1,
                "sentType": 0,
                "receiveType": 0,
                "userTag": "tag1,tag2",
                "returnable": False,
                "rangeType": 2,
                "rangeStoreCode": "",
                "rangeValue": "_resource",
            },
        ] * 3
        for c in coupons:
            code = MallV2.create_coupon(json=c).json()['data']['code']
            MallV2.coupon_shelf(code=code, action="on")            
            MallV2.offer_coupon(code=code, receives=[{"userId": userId + i, "count": 1} for i in range(math.ceil(total_reqs/reqs_per_user))])
        
        # skus for trade：one sku each vendor
        tmp, skus = [], []
        #todo: +vfine
        for vendor in ('pond5', 'xpc'):
            pids = [{"productId": p['productId'], "storeCode": STORE_RESOURCE}
                    for p in Search.query(vendor=vendor).json()['list']]
            products = MallV2.product_detail(json=pids).json()['data']

            tmp.append([{
                "skuId": sku['skuId'],
                "quantity": 2,
                "storeCode": STORE_RESOURCE
            } for p in products for _, sku in p['data']['productSkuMap'].items() if sku['price'] > 0])
        
        for li in tmp:
            skus.append(li[0])
        
        ka = {
            "skus": skus, 
            "coupons": []
        }
        totalPrice = MallV2.trade_confirmation(userId=userId, **ka).json()['data']['result']['totalPrice']
        # MallV2.trade_submit(skus=skus, totalPriceViewed=totalPrice)
        
        kwargs = {
            "method": "POST",
            "url": Url.trade_submit,
            "params": {"userId": userId},
            "json": {
                **ka,
                "totalPriceViewed": totalPrice,
            }
        }
        
        kwargs_list = []
        for i in range(total_reqs):
            a = copy.deepcopy(kwargs)
            a['params']['userId'] = userId + math.floor(i/reqs_per_user)
            kwargs_list.append(a)
        res = await areq(kwargs_list)
        status_list = [(await r.json())['status'] for r in res]

        log.info({s: status_list.count(s) for s in set(status_list)})
        assert status_list.count(0) == math.ceil(total_reqs/reqs_per_user)