import inspect
from typing import NewType
from _pytest.recwarn import T
import pytest
from utils import Data, MallV2, MallV2DB, new_tag, trade_count
from config import STORE4, STORE3, STORE4, STORE_NOT_EXIST, USER_ID, USER_ID2, STORE1, USER_ID_TANGYE, USER_ID_WANGCHANG
import time, math, random
from datetime import date, datetime, timedelta
import logging
from collections import defaultdict
from itertools import combinations


log = logging.getLogger(__file__)

class TestTradeConfirmation():
    '''订单确认
    '''
    
    def setup_method(self):
        '''清空默认用户的优惠券和兑换券
        '''
        MallV2DB.delete_coupons()
        MallV2DB.delete_tickets()

    def test_confirm_without_coupon(self):
        '''确认订单: 单sku+money_off优惠券 不选优惠券
        '''
        
        # 新建sku
        sku = Data.create_product(
            {"skus": [{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon({
            "thresholdPrice": 9900,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": STORE1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(coupon_code, 'on')
        MallV2.receive_coupon(coupon_code)
        s = {"skuId": sku['skuId'], "quantity": 1}
        self.kwargs = dict(skus=[s])
        r = MallV2.trade_confirmation([s])
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
        coupon_code = MallV2.create_coupon({
            "thresholdPrice": 9901,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": STORE1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(coupon_code, 'on')
        MallV2.receive_coupon(coupon_code)
        s = {"skuId": sku['skuId'], "quantity": 1}
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
        return r

    def test_2_coupon(self):
        '''确认订单: 单sku+2 * money_off优惠券 自动选取大额优惠
        '''
        
        # 新建sku
        sku = Data.create_product({"skus": [
            {"price": 9900, "originalPrice": 10000}
        ]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon({
            "thresholdPrice": 5000,
            "couponValue": 3000,
            "rangeType": 1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']
        MallV2.coupon_shelf(coupon_code, 'on')
        coupon_code2 = MallV2.create_coupon({
            "thresholdPrice": 2000,
            "couponValue": 2000,
            "rangeType": 1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']
        MallV2.coupon_shelf(coupon_code2, 'on')
        
        MallV2.receive_coupon(coupon_code)
        MallV2.receive_coupon(coupon_code2)
        s = {"skuId": sku['skuId'], "quantity": 1}

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
        return r

    def test_select_coupon(self):
        '''确认订单: 单sku+money_off优惠券 选择小额优惠券
        '''
        data = self.test_2_coupon().json()['data']
        
        coupon = [c for c in data['coupons'] if c['selected'] is False][0]
        sku = data['skus'][0]
        s = {k: v for k,v in sku.items() if k in ('skuId', 'quantity')}
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
        coupon_code = MallV2.create_coupon({
            "thresholdPrice": 1000,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": STORE1,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(coupon_code, 'on')
        MallV2DB.delete_coupons(USER_ID2)
        MallV2.receive_coupon(coupon_code, USER_ID2)
        MallV2.receive_coupon(coupon_code)
        coupon_id = MallV2.coupon_list(USER_ID2).json()['data']['list'][0]['id']
        s = {'skuId': sku['skuId'], 'quantity': 1}
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
        coupon1 = MallV2.create_coupon({
            "thresholdPrice": 5000,
            "couponValue": coupon1_price,
            "rangeType": 1,
            "rangeValue": sku['skuId'],
        }).json()['data']
        MallV2.coupon_shelf(coupon1['code'], 'on')
        MallV2.receive_coupon(coupon1['code'])
        # storeCode = '', 全平台 coupon
        coupon2 = MallV2.create_coupon({
            "thresholdPrice": 2000,
            "couponValue": coupon2_price,
            "rangeType": 2,
            "rangeValue": tag,
            "rangeStoreCode": ''
        }).json()['data']
        MallV2.coupon_shelf(coupon2['code'], 'on')
        MallV2.receive_coupon(coupon2['code'])
    
        s = {"skuId": sku['skuId'], "quantity": 1}
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
    
    def test_sku_coupon_of_another_store(self):
        '''storeCode不一致的coupon不能用
        '''
        sku = Data.create_product(
            {"skus": [{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]

        # 创建优惠券 上架 用户领取优惠券
        coupon_code = MallV2.create_coupon({
            "thresholdPrice": 9900,
            "couponValue": 1000,
            "rangeType": 1,
            "rangeStoreCode": STORE4,
            "rangeValue": sku["skuId"],
        }).json()['data']['code']

        MallV2.coupon_shelf(coupon_code, 'on')
        MallV2.receive_coupon(coupon_code)
        s = {"skuId": sku['skuId'], "quantity": 1}
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
        
        coupon_code2 = MallV2.create_coupon({
            "thresholdPrice": 2000,
            "couponValue": 4000,
            "rangeType": 2,
            "rangeValue": tag,
            "rangeStoreCode": STORE4
        }).json()['data']['code']
        MallV2.coupon_shelf(coupon_code2, 'on')
        MallV2.receive_coupon(coupon_code2)
        
        s = {"skuId": sku['skuId'], "quantity": 1}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])

        
        
        s = {"skuId": sku['skuId'], "quantity": 1}
        time.sleep(10)
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
                "couponValue": 6,
                "rangeType": 1,
                "rangeValue": sku2["skuId"]
            },
        ]
        
        for c in templates:    
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
        s2 = {"skuId": sku2['skuId'], "quantity": 2}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
        coupons = MallV2.coupon_list().json()['data']['list']
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 1}
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
        ''' doing 
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2}
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
                "rangeValue": sku2["skuId"],
                "rangeStoreCode": STORE4
            },
            {
                "couponValue": 3,
                "rangeType": 2,
                "rangeValue": tag,
                "rangeStoreCode": STORE4

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
                "rangeStoreCode": STORE4
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
            coupon = MallV2.create_coupon(c).json()['data']
            MallV2.coupon_shelf(coupon['code'], 'on')
            MallV2.receive_coupon(coupon['code'])
      
        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2, "storeCode": STORE4}
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

        ticket = MallV2.create_ticket(promotionTag=tag).json()['data']
        MallV2.offer_ticket(ticket['id'])
        MallV2.ticket_list()

        s = {"skuId": sku['skuId'], "quantity": 1}
        s2 = {"skuId": sku2['skuId'], "quantity": 2}
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
    '''
    def test_trade_submit(self):
        '''多sku 多优惠券组合 下单
        验证拆trade单数量 购买数量限制
        '''
        MallV2DB.delete_coupons()
        MallV2DB.delete_tickets()
        
        tags, prices, skus = [], [], []
        sku_tags = {}
        tag_skus = defaultdict(list)

        # 新建sku
        # for i in range(3):
        #     skus.append(Data.create_product({"skus": [
        #         {"price": prices[0], "promotionTags": [tags[0], tags[3], tags[5], tags[6]]}
        #     ]}).json()['data']['skus'][0])
        
        # sku2 = Data.create_product({"skus": [
        #     {"price": price2, "promotionTags": [tag[]]}
        # ]}).json()['data']['skus'][0]
        # sku3 = Data.create_product({"skus": [
        #     {"price": price3, "promotionTags": [tag3]}
        # ]}).json()['data']['skus'][0]
        
        count = 3
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
            c = MallV2.create_coupon({
                "thresholdPrice": s,
                "couponValue": random.randint(1, s),
                "rangeType": 2,
                "rangeValue": tags[i]
            }).json()['data']
            MallV2.coupon_shelf(c['code'], 'on')
            MallV2.receive_coupon(c['code'])
        for sku in skus:
            t = random.randint(0, 1)
            v = sku['productId'] if t == 0 else sku['skuId']
            c = MallV2.create_coupon({
                "threshold": sku['price'],
                "couponValue": random.randint(1, sku['price']),
                "rangeType": t,
                "rangeValue": v
            }).json()['data']
            MallV2.coupon_shelf(c['code'], 'on')
            MallV2.receive_coupon(c['code'])
        cart = []
        for sku in skus:
            cart.append(MallV2.add_to_cart(sku['skuId'], store=random.choice([STORE1, STORE4, STORE3, STORE4])).json()['data']['id'])
        
        MallV2.select_cart_item(cart)
        
        data = MallV2.trade_confirmation([]).json()['data']
        trade = MallV2.trade_submit([], data['result']['totalPrice']).json()['data']['trade']
        # 拆单数量
        assert len(trade) == trade_count([s['storeCode'] for s in data['skus']])
        for t in trade:
            location = MallV2.trade_token(t).json()['data']['location']
            token = location.split('/')[-1]
            channels = MallV2.trade_detail(t, token).json()['data']['channelList']
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
        
        d = MallV2.trade_confirmation(ss).json()['data']
        r = MallV2.trade_submit(
            ss,
            d['result']['totalPrice']
        )
        assert r.json()['status'] == 0
        
        # 商品库mock server购买次数2限制： 无法添加购物车 无法下单
        d = MallV2.trade_confirmation(ss).json()['data']
        r = MallV2.trade_submit(
            ss,
            d['result']['totalPrice']
        )
        assert r.json()['status'] == 6202
        r = MallV2.add_to_cart(ss[0]["skuId"], store=ss[0]["storeCode"])
        assert r.json()['status'] == 5104
         
        


    def test_all_confirmation(self):
        '''根据trade_confirmation的响应来提交订单
        忽略了几个有bug的case
        todo: 没做ticket 
        '''
        test_methods = [m[0] for m in inspect.getmembers(TestTradeConfirmation, predicate=inspect.isfunction) if m[0].startswith('test_')]
        for m in test_methods:
            
            # ignore illegal selection
            # 导致没有任何优惠券选中，submit空coupons导致自动选取优惠券生效 价格不一致提交订单失败
            if m not in ('test_select_others_coupon'):
                continue

            # for debug
            # if m != 'test_x_skus_x_coupons':
            #     continue

            log.info(f'>>>>>>>>> call {m} >>>>>>>>>')
            tc = TestTradeConfirmation()
            tc.setup_method()
            getattr(tc, m)()
            # 使用服务端返回的数据来提交订单
            coupons = [c['userCouponId'] for c in tc.data['coupons'] if c['selected'] is True] if 'coupons' in tc.data else []
            # tickets = [t['ticketId'] for t in tc.data['tickets']]  if 'tickets' in tc.data else []
            ka = {"totalPriceViewed": tc.data['result']['totalPrice']} | {"coupons": coupons}
            r = MallV2.trade_submit(**tc.kwargs | ka)
            assert r.status_code == 200
            b = r.json()
            assert b['status'] == 0
            assert len(b['data']['trade']) == 1

    def test_all_confirmation_2(self):
        '''使用trade_confirmation相同的请求参数来提交订单
        '''
        test_methods = [m[0] for m in inspect.getmembers(TestTradeConfirmation, predicate=inspect.isfunction) if m[0].startswith('test_')]
        for m in test_methods:
            
            # for debug
            # if m != 'test_x_skus_x_coupons':
            #     continue

            log.info(f'>>>>>>>>> call {m} >>>>>>>>>')
            tc = TestTradeConfirmation()
            tc.setup_method()
            getattr(tc, m)()
            
            # 添加totalPrice后下单
            r = MallV2.trade_submit(**tc.kwargs | {"totalPriceViewed": tc.data['result']['totalPrice']} )
            assert r.status_code == 200
            b = r.json()
            assert b['status'] == 0
            assert len(b['data']['trade']) == 1
            

    def test_trade_price_0(self):
        '''
        '''
    def test_trade_total_price_0(self):
        '''
        '''



    
class TestPay():
    '''pay
    '''

    @pytest.mark.parametrize('orderNo',[
        "20210617205750000683","20210617205750000686"
    ])
    def test_xyz(self, orderNo):
        location = MallV2.trade_token(orderNo).json()['data']['location']
        token = location.split('/')[-1]
        channels = MallV2.trade_detail(orderNo, token).json()['data']['channelList']
        channel = channels[random.randint(0, len(channels))]
        payload = {
            "channel": channel['channelCode'],
            "token": token,
            "appId": channel['appId'],
            # "openid": "",
            # "tradeNo": "20210608200447000114",
            # "totalPrice": 6900
        }
        MallV2.pay(**payload)
