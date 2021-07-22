import inspect
import pytest
from utils import Data, MallV2, MallV2DB, PayAdmin, new_tag, trade_count, Url, areq
from config import STORE2, STORE3, STORE2, STORE_NOT_EXIST, USER_ID, USER_ID2, STORE1
import time, math, random
from datetime import datetime, timedelta
import logging
from collections import defaultdict
from itertools import combinations

log = logging.getLogger(__file__)

class TestTradeConfirm():
    '''订单确认
    todo: 
    选择优惠券 多选
    ticket
    3个以上sku 使用满减券
    '''
    
    def setup_method(self):
        '''清空默认用户的优惠券和兑换券
        '''
        MallV2DB.delete_user_coupons()
        MallV2DB.delete_user_tickets()

    def test_confirm_without_coupon(self):
        '''确认订单: 单sku+money_off优惠券 不选优惠券
        '''
        
        # 新建sku
        sku = Data.create_product(
            {"skus": [{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon(**{
            "thresholdPrice": 9900,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": STORE1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(code=coupon_code, action='on')
        MallV2.receive_coupon(code=coupon_code)
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(skus=[s])
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900 - 1000

        coupon = [c for c in data['coupons'] if c['selected'] is True][0]
        assert coupon['code'] == coupon_code
        assert coupon['referOrders'][0] == skus[0]['orderNo']

        result = data['result']
        assert result['totalPrice'] == 9900 - 1000
        assert result['couponDiscount'] == 1000
        self.data = data
        
        
    def test_threshhold_too_greater(self):
        '''确认订单: sku threshhold太大 不能使用优惠券
        '''
        
        # 新建sku
        sku = Data.create_product(
            {"skus": [{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon(**{
            "thresholdPrice": 9901,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": STORE1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(code=coupon_code, action='on')
        MallV2.receive_coupon(code=coupon_code)
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']
        
        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900

        coupons = [c for c in data['coupons'] if c['selected'] is True]
        assert len(coupons) == 0

        result = data['result']
        assert result['totalPrice'] == 9900
        assert result['couponDiscount'] == 0
        self.data = data
        # return r

    def test_2_coupon(self):
        '''确认订单: 单sku+2 * money_off优惠券 自动选取大额优惠
        '''
        
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": 9900, "originalPrice": 10000}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon(**{
            "thresholdPrice": 5000,
            "couponValue": 3000,
            "rangeType": 1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']
        MallV2.coupon_shelf(code=coupon_code, action='on')
        coupon_code2 = MallV2.create_coupon(**{
            "thresholdPrice": 2000,
            "couponValue": 2000,
            "rangeType": 1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']
        MallV2.coupon_shelf(code=coupon_code2, action='on')
        
        MallV2.receive_coupon(code=coupon_code)
        MallV2.receive_coupon(code=coupon_code2)
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}

        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900 - 3000

        coupons = data['coupons']
        assert [c for c in coupons if c['selected'] is True][0]['code'] == coupon_code

        result = data['result']
        assert result['totalPrice'] == 9900 - 3000
        assert result['couponDiscount'] == 3000
        self.data = data
        # return r

    def test_select_coupon(self):
        '''确认订单: 单sku+money_off优惠券 选择小额优惠券
        '''
        self.test_2_coupon()
        
        coupon = [c for c in self.data['coupons'] if c['selected'] is False][0]
        sku = self.data['skus'][0]
        s = {k: v for k,v in sku.items() if k in ('skuId', 'quantity', 'storeCode')}
        self.kwargs = {"skus": [s], "coupons": [coupon['userCouponId']]}
        r = MallV2.trade_confirmation(**self.kwargs)
        
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']
        
        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900 - coupon['couponValue']

        coupons = data['coupons']
        assert [c for c in coupons if c['selected'] is True][0]['code'] == coupon['code']

        result = data['result']
        
        assert result['totalPrice'] == 9900 - coupon['couponValue']
        assert result['couponDiscount'] == coupon['couponValue']

        self.data = data

    def test_select_others_coupon(self):
        '''订单确认：使用他人的优惠券 没有优惠
        '''
        sku = Data.create_product({"skus": [{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]
        coupon_code = MallV2.create_coupon(**{
            "thresholdPrice": 1000,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": STORE1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(code=coupon_code, action='on')
        MallV2DB.delete_user_coupons(USER_ID2)
        MallV2.receive_coupon(code=coupon_code, userId=USER_ID2)
        MallV2.receive_coupon(code=coupon_code)
        coupon_id = MallV2.user_coupon_list(userId=USER_ID2).json()['data']['list'][0]['id']
        s = {'skuId': sku['skuId'], 'quantity': 1, "storeCode": STORE1}
        self.kwargs = dict(skus=[s], coupons=[coupon_id])
        r = MallV2.trade_confirmation(**self.kwargs)
        data = r.json()['data']
        self.data=data
        assert data['result']['couponDiscount'] == 0
        for c in data['coupons']:
            assert c['selected'] is False
            if c['rangeValue'] == sku['skuId']:
                assert c['isAvailable'] is True

    def test_disable_all_coupons(self):
        '''不使用优惠券
        '''
        self.test_confirm_without_coupon()
        # sku = r.json()['data']['skus'][0]
        # s = {"skuId": sku["skuId"], "quantity": sku["quantity"]}

        self.kwargs = self.kwargs | dict(disableAllCoupons=True)
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900

        for c in [c for c in data['coupons']]:
            assert c['selected'] is False
            assert c['isAvailable'] is False
            assert 'referOrders' not in c or c['referOrders'] is None

        result = data['result']
        assert result['totalPrice'] == 9900
        assert result['couponDiscount'] == 0   
        self.data = data


    def test_promotion_tag(self):
        '''订单确认：promotionTag优惠券 两个money_off 使用优惠大的
        '''
        tag = new_tag()
        price = 9900
        coupon1_price = 1000
        coupon2_price = 4000

        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon1 = MallV2.create_coupon(**{
            "thresholdPrice": 5000,
            "couponValue": coupon1_price,
            "rangeType": 1,
            "rangeValue": sku['skuId'],
        }).json()['data']
        MallV2.coupon_shelf(code=coupon1['code'], action='on')
        MallV2.receive_coupon(code=coupon1['code'])
        # storeCode = '', 全平台 coupon
        coupon2 = MallV2.create_coupon(**{
            "thresholdPrice": 2000,
            "couponValue": coupon2_price,
            "rangeType": 2,
            "rangeValue": tag,
            "rangeStoreCode": ''
        }).json()['data']
        MallV2.coupon_shelf(code=coupon2['code'], action='on')
        MallV2.receive_coupon(code=coupon2['code'])
    
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']
        
        skus = data['skus']
        assert skus[0]['price'] == price
        assert skus[0]['totalPrice'] == price - max(coupon1_price, coupon2_price)

        coupon = [c for c in data['coupons'] if c['selected'] is True][0]
        assert coupon['code'] == max((coupon1, coupon2), key=lambda x:x['couponValue'])['code']

        result = data['result']
        assert result['totalPrice'] == price - max(coupon1_price, coupon2_price)
        assert result['couponDiscount'] == max(coupon1_price, coupon2_price)
        self.data = data

    # def test_1_coupon_x_promotion_tags(self):
    #     '''订单确认：组合promotionTag 。 改方案
    #     '''
    #     tag = new_tag()[:10]
    #     tag2 = new_tag()[:10]
    #     price = 9900
    #     coupon1_price = 1000
    #     # coupon2_price = 4000

    #     # 新建sku
    #     sku = Data.create_product({"skus": [
    #         {"price": price, "promotionTags": [tag]}
    #     ]}).json()['data']['skus'][0]

    #     # 创建优惠券 上架 用户领取优惠券
    #     coupon1 = MallV2.create_coupon(**{
    #         "thresholdPrice": 5000,
    #         "couponValue": coupon1_price,
    #         "rangeType": 2,
    #         "rangeValue": f'{tag}&{tag2}',
    #     }).json()['data']
    #     MallV2.coupon_shelf(code=coupon1['code'], action='on')
    #     MallV2.receive_coupon(code=coupon1['code'])
    #     # storeCode = '', 全平台 coupon
        
    
    #     s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
    #     self.kwargs = dict(skus=[s])
    #     r = MallV2.trade_confirmation(**self.kwargs)
    #     assert r.status_code == 200
    #     jsn = r.json()
    #     assert jsn['status'] == 0

    #     data = jsn['data']
        
    #     skus = data['skus']
    #     assert skus[0]['price'] == price
    #     # assert skus[0]['totalPrice'] == price - max(coupon1_price, coupon2_price)

    #     coupon = [c for c in data['coupons'] if c['selected'] is True][0]
    #     # assert coupon['code'] == max((coupon1, coupon2), key=lambda x:x['couponValue'])['code']

    #     result = data['result']
    #     # assert result['totalPrice'] == price - max(coupon1_price, coupon2_price)
    #     # assert result['couponDiscount'] == max(coupon1_price, coupon2_price)
    #     self.data = data
    
    def test_sku_coupon_of_another_store(self):
        '''storeCode不一致的coupon不能用
        '''
        sku = Data.create_product(
            {"skus": [{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon(**{
            "thresholdPrice": 9900,
            "couponValue": 1000,
            "rangeType": 1,
            "rangeStoreCode": STORE2,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(code=coupon_code, action='on')
        MallV2.receive_coupon(code=coupon_code)
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900 

        coupons = [c for c in data['coupons'] if c['isAvailable'] is True]
        assert len(coupons) == 0

        result = data['result']
        assert result['totalPrice'] == 9900
        assert result['couponDiscount'] == 0
        self.data=data


    def test_promotion_tag_of_another_store(self):
        '''优惠券跟sku storeCode对不上
        '''
        tag = new_tag()

        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": 9900, "originalPrice": 10000, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        
        coupon_code2 = MallV2.create_coupon(**{
            "thresholdPrice": 2000,
            "couponValue": 4000,
            "rangeType": 2,
            "rangeValue": tag,
            "rangeStoreCode": STORE2
        }).json()['data']['code']
        MallV2.coupon_shelf(code=coupon_code2, action='on')
        MallV2.receive_coupon(code=coupon_code2)
        
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        skus = data['skus']
        assert skus[0]['price'] == 9900
        assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        assert coupons[0]['selected'] is False

        result = data['result']
        assert result['totalPrice'] == 9900
        assert result['couponDiscount'] == 0
        self.data = data

    def test_1_sku_2_coupons(self):
        '''price_off/percent_off 各类型使用1优惠大的
        '''
        tag = new_tag()
        price = 99800
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "originalPrice": 100000, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        template_available = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 2,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponValue": 4,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponType": "percent_off",
                "couponValue": 80,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 90,
                "rangeType": 0,
                "rangeValue": sku["productId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 85,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponType": "percent_off",
                "couponValue": 79,
                "rangeType": 2,
                "rangeValue": tag
            },
        ]
        template_unavailable = [
            

            # 过期 expiredAt
            {
                "couponType": "percent_off",
                "couponValue": 1000,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "expiredAt": int((datetime.now() - timedelta(seconds=3600*10)).timestamp() * 1000)
            },
            # 过期 duration
            {
                "couponType": "percent_off",
                "couponValue": 70,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "duration": 1
            },
            # bug storeCode 对不上
            # {
            #     "couponValue": 1000,
            #     "rangeType": 1,
            #     "rangeValue": sku["skuId"],
            #     "storeCode": STORE_NOT_EXIST
            # },
        ]
        templates = template_available + template_unavailable
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])

        
        
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        # time.sleep(10)
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        # coupons = data['coupons']
        # assert coupons[0]['selected'] is True

        result = data['result']
        assert result['totalPrice'] == math.ceil(price * 79 / 100) - 4
        assert result['couponDiscount'] == price - result['totalPrice']
        self.data = data

    def test_2_skus_2_coupons_1(self):
        '''两个sku 使用两个money_off券
        '''
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "name": "cc1",
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
        ]
        
        for c in templates:
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])

        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        total = price + price2
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == total - 6 - 1
        assert result['couponDiscount'] == total - result['totalPrice']
        self.data = data

    def test_2_skus_2_coupons_2(self):
        '''两个sku 使用两个money_off券：sku + promotion_tag
        '''
        price = 99800
        price2 = 99900
        tag = new_tag()
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 1,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        total = price + price2
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == total - 6 - 1
        assert result['couponDiscount'] == total - result['totalPrice']
        self.data = data

    def test_2_skus_2_of_3_coupons(self):
        '''两个sku 使用两个money_off券：sku + promotion_tag
        '''
        price = 99800
        price2 = 99900
        tag = new_tag()
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 1,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponValue": 6,
                "rangeType": 2,
                "rangeValue": tag
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        total = price + price2
        # time.sleep(10)
        self.kwargs = {"skus": [s, s2]}
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == total - 6 - 1
        assert result['couponDiscount'] == total - result['totalPrice']
        self.data = data

    def test_2_skus_1_coupon(self):
        ''' 2 sku 使用一个满减券 
        '''
        tag = new_tag()
        tag2 = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "thresholdPrice": price + price2,
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == price + price2 - 3
        assert result['couponDiscount'] == price + price2 - result['totalPrice']
        self.data = data

    def test_2_skus_1_coupon_2(self):
        ''' 2 sku 不满足满减券的threshhold 
        '''
        tag = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "thresholdPrice": price + price2 + 1,
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        total  = price + price2
        # time.sleep(10)
        kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == total
        assert result['couponDiscount'] == total - result['totalPrice']

        # 增加一个数量 满足threshhold
        s2 = {"skuId": sku2['skuId'], "quantity": 2, "storeCode": STORE1}
        total  = price + price2 * 2 
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == total - 3
        assert result['couponDiscount'] == total - result['totalPrice']
        self.data =data


    def test_2_skus_4_coupons(self):
        ''' 2 个sku 各叠加使用money_off和percent_off 
        '''
        tag = new_tag()
        tag2 = new_tag()
        price = 99800
        price2 = 99998
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag2]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        template_available = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponValue": 4,
                "rangeType": 2,
                "rangeValue": tag2
            },
            {
                "couponValue": 5,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
            {
                "couponType": "percent_off",
                "couponValue": 80,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 81,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 90,
                "rangeType": 0,
                "rangeValue": sku["productId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 89,
                "rangeType": 0,
                "rangeValue": sku2["productId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 85,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponType": "percent_off",
                "couponValue": 79,
                "rangeType": 2,
                "rangeValue": tag2
            },
            {
                "couponType": "percent_off",
                "couponValue": 82,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
        ]
        template_unavailable = [
            # 过期 expiredAt
            {
                "couponType": "percent_off",
                "couponValue": 1000,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "expiredAt": int((datetime.now() - timedelta(seconds=3600*10)).timestamp() * 1000)
            },
            # 过期 duration
            {
                "couponType": "percent_off",
                "couponValue": 70,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "duration": 1
            },
            # bug storeCode 对不上
            # {
            #     "couponValue": 1000,
            #     "rangeType": 1,
            #     "rangeValue": sku["skuId"],
            #     "storeCode": STORE_NOT_EXIST
            # },
        ]
        templates = template_available + template_unavailable
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2, "storeCode": STORE1}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        # 不指定coupons
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']
        self.data = data
        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == math.ceil(price2 * 2 * 79 / 100) - 6 + math.ceil(price * 80 /100) - 5
        assert result['couponDiscount'] == price + price2 * 2 - result['totalPrice']

        # 指定coupons
        userCouponIds = [c['userCouponId'] for c in data['coupons'] if c['selected'] is True]
        r = MallV2.trade_confirmation(** self.kwargs | {"coupons": userCouponIds})


    def test_2_skus_3_coupons(self):
        '''优先优惠大的券，优先应用在price高的sku上
        不能保证优惠最大 
        '''
        tag = new_tag()
        tag2 = new_tag()
        price = 99800
        price2 = 99998
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag2]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        template_available = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                # "thresholdPrice": price + 1,
                "couponValue": 15,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
        ]
        template_unavailable = [
            
        ]
        templates = template_available + template_unavailable
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == price2 - 15 + price - 1
        assert result['couponDiscount'] == price + price2 - result['totalPrice']
        self.data = data

    def test_2_skus_3_coupons_2(self):
        '''用户选择优惠券
        相当于排除了其他可用的优惠券，只从用户选择的券里边按固定逻辑选择使用
        '''
        tag = new_tag()
        tag2 = new_tag()
        price = 99800
        price2 = 99998
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag2]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        template_available = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                # "thresholdPrice": price + 1,
                "couponValue": 15,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
        ]
        template_unavailable = [
            
        ]
        templates = template_available + template_unavailable
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
        coupons = MallV2.user_coupon_list().json()['data']['list']
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        # 默认会使用-15和-1的券， -6的券因为使用了-15而不可用。 选择-15和-6后 只有-15可用
        self.kwargs = dict(skus=[s, s2]) | {"coupons": [c['id'] for c in coupons if c['couponValue'] != 1]}
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == price2 - 15 + price
        assert result['couponDiscount'] == price + price2 - result['totalPrice']
        self.data = data


    def x_skus_x_coupons(self):
        ''' for testcase 
        '''
        tag = new_tag()
        tag2 = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag2]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        template_available = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponValue": 4,
                "rangeType": 2,
                "rangeValue": tag2
            },
            {
                "couponValue": 5,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
            {
                "couponType": "percent_off",
                "couponValue": 80,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 81,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 90,
                "rangeType": 0,
                "rangeValue": sku["productId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 89,
                "rangeType": 0,
                "rangeValue": sku2["productId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 85,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponType": "percent_off",
                "couponValue": 79,
                "rangeType": 2,
                "rangeValue": tag2
            },
            {
                "couponType": "percent_off",
                "couponValue": 82,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
        ]
        template_unavailable = [
            # 过期 expiredAt
            {
                "couponType": "percent_off",
                "couponValue": 1000,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "expiredAt": int((datetime.now() - timedelta(seconds=3600*10)).timestamp() * 1000)
            },
            # 过期 duration
            {
                "couponType": "percent_off",
                "couponValue": 70,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "duration": 1
            },
            # bug storeCode 对不上
            # {
            #     "couponValue": 1000,
            #     "rangeType": 1,
            #     "rangeValue": sku["skuId"],
            #     "storeCode": STORE_NOT_EXIST
            # },
        ]
        templates = template_available + template_unavailable
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2, "storeCode": STORE1}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == math.ceil((price + price2 * 2) * 79 / 100) - 4
        assert result['couponDiscount'] == price - result['totalPrice']
        self.data = data

    def test_x_store(self):
        '''两个sku各使用折扣后，叠加组合满减
        '''
        tag = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}, storeCode=STORE2).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        template_available = [
            {
                "couponValue": 1,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 2,
                "rangeType": 1,
                "rangeValue": sku2["skuId"],
                "rangeStoreCode": STORE2
            },
            {
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag,
                "rangeStoreCode": STORE2
            },
            # 打85折后，sku2子单不足
            {
                "thresholdPrice": price2 * 2,
                "couponValue": 5,
                "rangeType": 2,
                "rangeValue": tag,
                "rangeStoreCode": ""
            },
            # {
            #     "couponType": "percent_off",
            #     "couponValue": 80,
            #     "rangeType": 1,
            #     "rangeValue": sku["skuId"]
            # },
            # {
            #     "couponType": "percent_off",
            #     "couponValue": 90,
            #     "rangeType": 0,
            #     "rangeValue": sku["productId"]
            # },
            {
                "couponType": "percent_off",
                "couponValue": 85,
                "rangeType": 2,
                "rangeValue": tag,
                "rangeStoreCode": STORE2
            },
            {
                "couponType": "percent_off",
                "couponValue": 79,
                "rangeType": 2,
                "rangeValue": tag
            },
        ]
        template_unavailable = [
            # 过期 expiredAt
            {
                "couponType": "percent_off",
                "couponValue": 1000,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "expiredAt": int((datetime.now() - timedelta(seconds=3600*10)).timestamp() * 1000)
            },
            # 过期 duration
            {
                "couponType": "percent_off",
                "couponValue": 70,
                "rangeType": 1,
                "rangeValue": sku["skuId"],
                "duration": 1
            },
            # bug storeCode 对不上
            # {
            #     "couponValue": 1000,
            #     "rangeType": 1,
            #     "rangeValue": sku["skuId"],
            #     "storeCode": STORE_NOT_EXIST
            # },
        ]
        templates = template_available + template_unavailable
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2, "storeCode": STORE2}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        log.info(len([c for c in coupons if c['selected'] is True]))

        result = data['result']
        assert result['totalPrice'] == math.ceil(price * 79 / 100) + math.ceil(price2 * 2 * 85 / 100) - 5
        assert result['couponDiscount'] == price + price2 * 2 - result['totalPrice']
        self.data = data

    def test_x_skus_1_ticket(self):
        tag = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        ticket = MallV2.manage_create_ticket(promotionTag=tag).json()['data']
        MallV2.offer_ticket(ticketId=ticket['id'])
        MallV2.ticket_list()

        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2, "storeCode": STORE1}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        result = data['result']
        assert result['totalPrice'] == 0
        assert result['ticketDiscount'] == price + price2 * 2
        self.data = data


class TestTradeSubmit():
    '''提交订单
    todo:
    取消订单
    退款 优惠券返还
    组合券 部分退款
    trade价格0
    部分trade价格0
    '''
    def setup_method(self):
        MallV2DB.delete_user_coupons()
        MallV2DB.delete_user_tickets()

    @pytest.mark.parametrize('count', [
        3,
        4,
        5
    ])
    def test_trade_submit(self, count):
        '''多sku(随机storeCode) 多优惠券组合 下单
        验证拆trade单数量 购买数量限制
        '''
        # count: sku 数量
        tags, prices, skus = [], [], []
        sku_tags = {}
        tag_skus = defaultdict(list)
        
        
        skus_idx = list(range(count))
        
        combines = []
        for i in range(count)[1:]:
            combines = combines + list(combinations(skus_idx, i + 1))
        log.info(combines)
        for _ in range(len(combines)):
            tags.append(new_tag())   
        for _ in range(count):
            prices.append(random.randint(1, 10000)) 
        for i in range(count):
            tags_idx = [combines.index(c) for c in combines if i in c]
            sku_tags[i] = tags_idx
            skus.append(Data.create_product({"skus": [
                {"price": prices[i], "promotionTags": [tags[i] for i in tags_idx]}
            ]}).json()['data']['skus'][0])
            for j in tags_idx:
                tag_skus[j].append(i)     
        log.info(f'sku_tags: {sku_tags}')
        log.info(f'tag_skus: {tag_skus}')
        for i in range(len(tags)):
            s = sum([skus[i]['price'] for i in tag_skus[i]])
            c = MallV2.create_coupon(**{
                "thresholdPrice": s,
                "couponValue": random.randint(1, s),
                "rangeType": 2,
                "rangeValue": tags[i]
            }).json()['data']
            MallV2.coupon_shelf(code=c['code'], action='on')
            MallV2.receive_coupon(code=c['code'])
        for sku in skus:
            t = random.randint(0, 1)
            v = sku['productId'] if t == 0 else sku['skuId']
            c = MallV2.create_coupon(**{
                "threshold": sku['price'],
                "couponValue": random.randint(1, sku['price']),
                "rangeType": t,
                "rangeValue": v
            }).json()['data']
            MallV2.coupon_shelf(code=c['code'], action='on')
            MallV2.receive_coupon(code=c['code'])
        cart = []
        for sku in skus:
            cart.append(MallV2.add_to_cart(skuId=sku['skuId'], storeCode=random.choice([STORE1, STORE2, STORE3, STORE2])).json()['data']['id'])
        
        MallV2.select_cart_item(cartItemIds=cart)
        
        data = MallV2.trade_confirmation(skus=[]).json()['data']
        trade = MallV2.trade_submit(skus=[], totalPriceViewed=data['result']['totalPrice']).json()['data']['trade']
        # 拆单数量
        log.info(f"storeCodes: {[s['storeCode'] for s in data['skus']]}, 支付单数量: {len(trade)}")
        assert len(trade) == trade_count([s['storeCode'] for s in data['skus']])
        for t in trade:
            location = MallV2.trade_token(tradeNo=t).json()['data']['location']
            token = location.split('/')[-1]
            channels = MallV2.trade_detail(tradeNo=t, token=token).json()['data']['channelList']
            channel = channels[random.randint(0, len(channels)-1)]
            payload = {
                "channel": channel['channelCode'],
                "token": token,
                "appId": channel['appId'],
                # "openid": "",
                # "tradeNo": "20210608200447000114",
                # "totalPrice": 6900
            }
            MallV2.pay(**payload)
        ss = [{"skuId": sku["skuId"], "quantity": sku["quantity"], "storeCode": sku["storeCode"]} for sku in data['skus']]
        
        d = MallV2.trade_confirmation(skus=ss).json()['data']
        r = MallV2.trade_submit(
            skus=ss,
            totalPriceViewed=d['result']['totalPrice']
        )
        assert r.json()['status'] == 0
        log.info(r.json()['data']['trade'])
        assert len(r.json()['data']['trade']) == trade_count([sku['storeCode'] for sku in data['skus']])
        
        # 商品库mock server购买次数2限制：无法下单 无法添加购物车
        d = MallV2.trade_confirmation(skus=ss).json()['data']
        r = MallV2.trade_submit(
            skus=ss,
            totalPriceViewed=d['result']['totalPrice']
        )
        assert r.json()['status'] == 6202
        r = MallV2.add_to_cart(skuId=ss[0]["skuId"], storeCode=ss[0]["storeCode"])
        assert r.json()['status'] == 5104

    @pytest.mark.parametrize('confirm_case_name', [
        m[0] for m in inspect.getmembers(TestTradeConfirm, predicate=inspect.isfunction) if m[0].startswith('test_') and m[0]!='test_select_others_coupon'
    ])
    def test_all_confirmation(self, confirm_case_name):
        '''使用价格计算器返回的优惠提交订单
        '''
        # test_methods = [m[0] for m in inspect.getmembers(TestTradeConfirm, predicate=inspect.isfunction) if m[0].startswith('test_')]
        # for m in test_methods:
            
            # ignore illegal choice
            # 导致价格计算器没有任何优惠券选中，submit(coupons=[])导致自动选取优惠券生效 价格不一致提交订单失败
            # if m in ('test_select_others_coupon'):
            #     continue

            # for single case debug
            # if m != 'test_x_skus_x_coupons':
            #     continue

        log.info(f'>>>>>>>>> call {confirm_case_name} >>>>>>>>>')
        tc = TestTradeConfirm()
        tc.setup_method()
        getattr(tc, confirm_case_name)()
        # 使用服务端返回的数据来提交订单
        coupons = [c['userCouponId'] for c in tc.data['coupons'] if c['selected'] is True] if 'coupons' in tc.data else []
        # tickets = [t['ticketId'] for t in tc.data['tickets']]  if 'tickets' in tc.data else []
        ka = {"totalPriceViewed": tc.data['result']['totalPrice']} | {"coupons": coupons}
        r = MallV2.trade_submit(**tc.kwargs | ka)
        assert r.status_code == 200
        b = r.json()
        assert b['status'] == 0
        if confirm_case_name != 'test_x_store':
            assert len(b['data']['trade']) == 1

    @pytest.mark.parametrize('confirm_case', [
        m[0] for m in inspect.getmembers(TestTradeConfirm, predicate=inspect.isfunction) if m[0].startswith('test_')
    ])
    def test_all_confirmation_2(self, confirm_case):
        '''使用trade_confirmation相同的请求参数来提交订单
        '''
        # test_methods = [m[0] for m in inspect.getmembers(TestTradeConfirm, predicate=inspect.isfunction) if m[0].startswith('test_')]
        # for m in test_methods:
            
            # for debug
            # if m != 'test_x_skus_x_coupons':
            #     continue

        log.info(f'>>>>>>>>> call {confirm_case} >>>>>>>>>')
        tc = TestTradeConfirm()
        tc.setup_method()
        getattr(tc, confirm_case)()
        
        # 添加totalPrice后下单
        r = MallV2.trade_submit(**tc.kwargs | {"totalPriceViewed": tc.data['result']['totalPrice']} )
        assert r.status_code == 200
        b = r.json()
        assert b['status'] == 0
        if confirm_case != 'test_x_store':
            assert len(b['data']['trade']) == 1
    

    def test_cancel_with_wrong_userId(self):
        '''取消订单，使用他人的userId：404 或者 取消他人的订单
        '''
        tc = TestTradeConfirm()
        tc.test_2_skus_2_of_3_coupons()
        trade = MallV2.trade_submit(**tc.kwargs | {"totalPriceViewed": tc.data['result']['totalPrice']}).json()['data']['trade']
        r = MallV2.trade_cancel(tradeNo=trade[0], userId=USER_ID2)
        assert r.status_code == 404

    def test_cancel_without_userId(self):
        '''取消订单，不传userId：401
        '''
        tc = TestTradeConfirm()
        tc.test_2_skus_2_of_3_coupons()
        trade = MallV2.trade_submit(**tc.kwargs | {"totalPriceViewed": tc.data['result']['totalPrice']}).json()['data']['trade']
        r = MallV2.trade_cancel(tradeNo=trade[0], params=None)
        assert r.status_code == 401
        assert r.json()['status'] == 2401

    def test_cancel_with_wrong_tradeNo(self):
        '''取消订单，使用不存在的tradeNo
        '''
        r = MallV2.trade_cancel(tradeNo='1')
        assert r.status_code == 404

    def test_cancel(self):
        '''取消订单，returnable=False的优惠券不返还
        bug
        '''
        tc = TestTradeConfirm()
        tc.test_2_skus_2_of_3_coupons()
        a = MallV2.user_coupon_list().json()['data']['list']
        trade = MallV2.trade_submit(**tc.kwargs | {"totalPriceViewed": tc.data['result']['totalPrice']}).json()['data']['trade']
        b = MallV2.user_coupon_list().json()['data']['list']
        r = MallV2.trade_cancel(tradeNo=trade[0])
        c = MallV2.user_coupon_list().json()['data']['list']
        # 
        assert {i['id'] for i in a if i['status']=='available'} == {i['id'] for i in c if i['status']=='available'} | {i['userCouponId'] for i in tc.data['coupons'] if i['selected'] is True}
        # 取消订单前后 不会修改优惠券
        assert b == c

    def test_returnable_coupon(self):
        '''取消订单，返还优惠券
        '''
        price = 99800
        price2 = 99900
        tag = new_tag()
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 1,
                "rangeType": 2,
                "rangeValue": tag,
                "returnable": True
            },
            {
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"],
                "returnable": True
            },
            {
                "couponValue": 6,
                "rangeType": 2,
                "rangeValue": tag,
                "returnable": True
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        total = price + price2
        # time.sleep(10)
        self.kwargs = {"skus": [s, s2]}
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == total - 6 - 1
        assert result['couponDiscount'] == total - result['totalPrice']
        self.data = data
        
        # 以上复制自 TestTradeConfirm.test_2_skus_2_of_3_coupons 增加了优惠券returnable: True

        coupons_before_submit = MallV2.user_coupon_list().json()['data']['list']
        MallV2.trade_submit(**self.kwargs | {"totalPriceViewed": self.data['result']['totalPrice']})
        coupons_after_submit = MallV2.user_coupon_list().json()['data']['list']
        

        consumed = {c['id'] for c in coupons_after_submit if c['status'] == 'consumed'}
        assert consumed == {c['userCouponId'] for c in self.data['coupons'] if c['selected'] is True}
        assert {c['id'] for c in coupons_after_submit if c['status'] == 'available'} | consumed == {c['id'] for c in coupons_before_submit if c['status'] == 'available'}
        # assert {c['id'] for c in coupons_after_cancel} == {c['id'] for c in coupons_before_submit}


    def test_trade_price_0(self):
        '''提交总价0的订单，状态是'succeed'
        '''
        price = 99800
        price2 = 99900
        tag = new_tag()
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 99900,
                "rangeType": 2,
                "rangeValue": tag,
                "returnable": True
            },
            {
                "couponValue": 99800,
                "rangeType": 2,
                "rangeValue": tag,
                "returnable": True
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        total = price + price2
        self.kwargs = {"skus": [s, s2]}
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        data = r.json()['data']
        assert data['result']['totalPrice'] == 0
        assert data['result']['couponDiscount'] == total - data['result']['totalPrice']
    
        coupons = [c['userCouponId'] for c in data['coupons']]
        r = MallV2.trade_submit(**self.kwargs | {"coupons": coupons, "totalPriceViewed": data['result']['totalPrice']})
        trades = r.json()['data']['trade']
        assert len(trades) == 1
        self.trades = trades
        location = MallV2.trade_token(tradeNo=trades[0]).json()['data']['location']
        token = location.split('/')[-1]
        r = MallV2.trade_detail(tradeNo=trades[0], token=token)
        assert r.json()['data']['status'] == 'succeed'

    def test_multiple_trade(self):
        '''不同结算商户，生成多个支付单
        '''
        # 
        tag = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}, storeCode=STORE2).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 99800,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 2,
                "rangeType": 1,
                "rangeValue": sku2["skuId"],
                "rangeStoreCode": STORE2
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE2}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        log.info(f"使用的优惠券数：{len([c for c in coupons if c['selected'] is True])}")

        result = data['result']
        assert result['totalPrice'] == price2 - 2
        assert result['couponDiscount'] == price + price2 - result['totalPrice']
        # self.data = data

        r = MallV2.trade_submit(**self.kwargs | {"totalPriceViewed": data['result']['totalPrice'], "coupons": [c["userCouponId"] for c in data["coupons"]]})
        trades = r.json()['data']['trade']
        self.trades = trades
        assert len(trades) == 2
        for tradeNo in trades:
            location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
            token = location.split('/')[-1]
            r = MallV2.trade_detail(tradeNo=tradeNo, token=token)
            assert r.json()['data']['price'] in (0, price2 - 2)

    @pytest.mark.asyncio
    async def test_async_submit(self):
        
        tag = new_tag()
        price = 99800
        price2 = 99900
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag]}
        ]}, storeCode=STORE2).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 99800,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 2,
                "rangeType": 1,
                "rangeValue": sku2["skuId"],
                "rangeStoreCode": STORE2
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            for _ in range(1):
                MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE2}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        log.info(f"使用的优惠券数：{len([c for c in coupons if c['selected'] is True])}")

        result = data['result']
        assert result['totalPrice'] == price2 - 2
        assert result['couponDiscount'] == price + price2 - result['totalPrice']
        
        
        kwargs = {
            "url": Url.trade_submit, 
            "method": "POST", 
            "params": {"userId": USER_ID}, 
            "json": self.kwargs | {"totalPriceViewed": data['result']['totalPrice'], "coupons": [c["userCouponId"] for c in data["coupons"]]}
        }

        # 并发数
        concurrency_count = 30
        
        rst = await areq(concurrency_count, kwargs)            
        assert {result.status for result in rst} == {200}
        res_status = [(await result.json())['status'] for result in rst]
        assert res_status.count(0) == 1
        # 6501 获取redis锁失败; 6200 优惠不可用导致价格对不上 下单失败
        assert res_status.count(6200) + res_status.count(6501) == concurrency_count - 1

class TestPay():
    '''pay
    todo: refund
    支付他人订单
    '''

    def setup_method(self):
        MallV2DB.delete_user_coupons()
        MallV2DB.delete_user_tickets()

    # @pytest.mark.parametrize('orderNo',[
    #     "20210617205750000683","20210617205750000686"
    # ])
    # def test_xyz(self, orderNo):
    #     # location = MallV2.trade_token(orderNo).json()['data']['location']
    #     # token = location.split('/')[-1]
    #     # channels = MallV2.trade_detail(orderNo, token).json()['data']['channelList']
    #     # channel = channels[random.randint(0, len(channels)-1)]
    #     # payload = {
    #     #     "channel": channel['channelCode'],
    #     #     "token": token,
    #     #     "appId": channel['appId'],
    #     #     # "openid": "",
    #     #     # "tradeNo": "20210608200447000114",
    #     #     # "totalPrice": 6900
    #     # }
    #     # MallV2.pay(**payload)
    #     PayAdmin().fix('20210621164415000104')
    #     MallV2.trade_list()

    def test_pay(self):
        '''下单生成2个trade，金额为0的trade状态是成功 不可支付; 金额不为0的trade可支付
        '''
        ts = TestTradeSubmit()
        ts.test_multiple_trade()
        l1 = [t['status'] for t in MallV2.trade_list().json()['data']['list']] 
        
        # 1单succeed，1单pay_waiting 
        assert set(l1[:2]) == {'succeed', 'pay_waiting'}
        for tradeNo in ts.trades:
            location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
            token = location.split('/')[-1]
            data = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']
            
            channel = data['channelList'][random.randint(0, len(data['channelList'])-1)]
            price = data['price']
            payload = {
                "channel": channel['channelCode'],
                "token": token,
                "appId": channel['appId'],
            }
            
            r = MallV2.pay(**payload).json()
            if price == 0:
                assert r['status'] == 6104
            else:
                assert r['status'] == 0
                PayAdmin().fix(r['data']['order'])
        # pay admin 后台通知有可能配置延迟通知
        time.sleep(1)
        trade_list = MallV2.trade_list().json()['data']['list']
        l2 = [t['status'] for t in trade_list] 
        log.info(l2)
        assert l2[:2] == ['succeed'] * 2
        assert l2[2:] == l1[2:]
        assert [t['orders'][0]['status'] for t in trade_list[:2]] == ['succeed'] * 2
        
    def test_multiple_order(self):
        '''支付单包含2个子订单
        '''
        tag = new_tag()
        tag2 = new_tag()
        price = 99800
        price2 = 99900
        price3 = 122000
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": price, "promotionTags": [tag]}
        ]}).json()['data']['skus'][0]
        sku2 = Data.create_product({"skus": [
            {"price": price2, "promotionTags": [tag,tag2]}
        ]}).json()['data']['skus'][0]
        sku3 = Data.create_product({"skus": [
            {"price": price3, "promotionTags": [tag2]}
        ]}, storeCode=STORE2).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        templates = [
            {
                "couponValue": 600,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponValue": 650,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponValue": 800,
                "rangeType": 2,
                "rangeValue": tag,
                "thresholdPrice": 80000
            },
            {
                "couponValue": 620,
                "rangeType": 2,
                "rangeValue": tag,
                "thresholdPrice": 50000,
                # "rangeStoreCode": STORE1,
            },
            {
                "couponValue": 610,
                "rangeType": 2,
                "rangeValue": tag2,
                "thresholdPrice": 50000,
                "rangeStoreCode": STORE2,
            },
            {
                "couponValue": 900,
                "rangeType": 2,
                "rangeValue": tag,
                "thresholdPrice": 130000,
                "rangeStoreCode": "",
            },
            {
                "couponValue": 1000,
                "rangeType": 2,
                "rangeValue": tag2,
                "thresholdPrice": 130000,
                "rangeStoreCode": "",
            },
            {
                "couponValue": 5,
                "rangeType": 2,
                "rangeValue": "_mock_data"
            },
            {
                "couponType": "percent_off",
                "couponValue": 80,
                "rangeType": 1,
                "rangeValue": sku["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 81,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 77,
                "rangeType": 0,
                "rangeValue": sku["productId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 78,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
            {
                "couponType": "percent_off",
                "couponValue": 85,
                "rangeType": 2,
                "rangeValue": tag
            },
            {
                "couponType": "percent_off",
                "couponValue": 79,
                "rangeType": 2,
                "rangeValue": tag2,
                "rangeStoreCode": "",
            },
            {
                "couponType": "percent_off",
                "couponValue": 80,
                "rangeType": 1,
                "rangeValue": sku3["skuId"]
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(**c).json()['data']
            MallV2.coupon_shelf(code=coupon['code'], action='on')
            MallV2.receive_coupon(code=coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1, "storeCode": STORE1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1, "storeCode": STORE1}
        s3 = {"skuId": sku3['skuId'], "quantity": 1, "storeCode": STORE2}
        # time.sleep(10)
        self.kwargs = dict(skus=[s, s2, s3])
        r = MallV2.trade_confirmation(**self.kwargs)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

        data = jsn['data']

        # skus = data['skus']
        # assert skus[0]['price'] == 9900
        # assert skus[0]['totalPrice'] == 9900

        coupons = data['coupons']
        # assert len([c for c in coupons if c['selected'] is True]) == 2
        log.info('coupons selected: {}'.format(len([c for c in coupons if c['selected'] is True])))
        log.info('selected : {}'.format({i: coupons[i]['selected'] for i in range(len(coupons))}))
        log.info('available: {}'.format({i: coupons[i]['isAvailable'] for i in range(len(coupons))}))

        result = data['result']
        assert result['totalPrice'] == math.ceil(price * 77/100) - 620 + math.ceil(price2 * 78/100) + math.ceil(price3 * 79/100) - 1000
        assert result['couponDiscount'] == price + price2 + price3 - result['totalPrice']
        self.data = data
        
        r = MallV2.trade_submit(** self.kwargs | {"totalPriceViewed": result["totalPrice"], "coupons": [c['userCouponId'] for c in coupons if c["selected"] is True]})
        trade = r.json()['data']['trade']
        assert len(trade) == 2
        details = []
        for tradeNo in trade:
            location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
            token = location.split('/')[-1]
            detail = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']
            details.append(detail)
            channel = detail['channelList'][random.randint(0, len(detail['channelList'])-1)]
            payload = {
                "channel": channel['channelCode'],
                "token": token,
                "appId": channel['appId'],
            }
            r = MallV2.pay(**payload).json()
            assert r['status'] == 0
        
        if (details[0]['orderCount']) == 1:
            details = details[::-1]
        assert len(details[0]['orders']) == 2
        assert details[0]['orderCount'] == 2
        assert details[0]['status'] == 'pay_waiting'
        for o in details[0]['orders']:
            assert o['status'] == 'init'
            assert o['storeCode'] == STORE1
        assert details[0]['price'] == sum([o['totalPrice'] for o in details[0]['orders']])

        assert len(details[1]['orders']) == 1
        assert details[1]['orderCount'] == 1
        assert details[1]['status'] == 'pay_waiting'
        for o in details[1]['orders']:
            assert o['status'] == 'init'
            assert o['storeCode'] == STORE2
        assert details[1]['price'] == sum([o['totalPrice'] for o in details[1]['orders']])

        assert result['totalPrice'] == sum([d['price'] for d in details])
                

    def test_pay_succeeded(self):
        '''支付已成功的订单 status=6104
        '''
        ts = TestTradeSubmit()
        ts.test_trade_price_0()
        tradeNo = ts.trades[0]
        location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
        token = location.split('/')[-1]
        channels = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']['channelList']
        channel = channels[random.randint(0, len(channels)-1)]
        payload = {
            "channel": channel['channelCode'],
            "token": token,
            "appId": channel['appId'],
        }
        assert MallV2.pay(**payload).json()['status'] == 6104

    @pytest.mark.asyncio
    async def test_async_pay(self):
        '''并发支付：生成第三方支付二维码/
        目前的产品逻辑 不需要限制；允许多笔支付成功 长款交易；
        '''
        ts = TestTradeSubmit()
        ts.test_multiple_trade()
        trade = [t for t in MallV2.trade_list().json()['data']['list'] if t['status']=='pay_waiting'][0]
        
        
        location = MallV2.trade_token(tradeNo=trade['tradeNo']).json()['data']['location']
        token = location.split('/')[-1]
        data = MallV2.trade_detail(tradeNo=trade['tradeNo'], token=token).json()['data']
        assert data['status'] == 'pay_waiting'
        
        channel = data['channelList'][random.randint(0, len(data['channelList'])-1)]
        price = data['price']
        payload = {
            "channel": channel['channelCode'],
            "token": token,
            "appId": channel['appId'],
        }
        # 10个并发不会导致6500（redis lock）
        concurrency_count = 30
        
        res = await areq(concurrency_count, {
            "method": "POST",
            "url": Url.pay,
            "json": payload,
            "params": {"userId": USER_ID}
        })

        assert {r.status for r in res} == {200}
        res = [await r.json() for r in res]
        s = [r['status'] for r in res]
        assert s.count(0) >= 1
        assert s.count(6501) <= concurrency_count - 1
        orders = [r['data']['order'] for r in res if r['status'] == 0]
        for o in orders:
            PayAdmin().fix(o)
        r = MallV2.trade_detail(tradeNo=trade['tradeNo'], token=token)
        assert r.status_code == 200
        assert r.json()['data']['status'] == 'succeed'

        assert MallV2.pay(**payload).json()['status'] == 6104