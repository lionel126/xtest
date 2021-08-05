'''很多接口没写
优惠券删除/下架后
'''
import math
import pytest
from utils import Data, MallV2
from config import USER_ID, USER_ID2, STORE1
import time, random

class TestCoupon():
    @pytest.mark.parametrize('coupon', [
        {
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
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        }
    ])
    def test_create_coupon(self, coupon):
        # 获取可用sku 价格
        # sku = Data.create_product({"skus":[{"price": 9900, "originalPrice": 10000}]}).json()['data']['skus'][0]
        # available_keys = ('storeCode', 'skuId', 'quantity',
        #                   'ticketCode', 'disablePromotion')

        # tmp = {"cartItemId": sku["id"]}
        # tmp = {k:v for k, v in sku.items() if k in available_keys}
        r = MallV2.create_coupon(**coupon)
        assert r.status_code == 200
        assert r.json()['status'] == 0
        return r

    @pytest.mark.parametrize('coupon', [
        {
            # "name": "coupon_from_test",
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
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        },
        {
            "name": "coupon_from_test",
            "brief": "test brief",
            # "couponType": "money_off",
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
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        },
        {
            "name": "coupon_from_test",
            "brief": "test brief",
            "couponType": "money_off",
            # "couponValue": 5,
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
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        },
        {
            "name": "coupon_from_test",
            "brief": "test brief",
            "couponType": "money_off",
            "couponValue": 5,
            # "effectiveAt": int((time.time() - 3600) * 1000),
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
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        },
        {
            "name": "coupon_from_test",
            "brief": "test brief",
            "couponType": "money_off",
            "couponValue": 5,
            "effectiveAt": int((time.time() - 3600) * 1000),
            # "expiredAt": int((time.time() + 3600 * 24) * 1000),
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
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        },
        {
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
            # "thresholdPrice": 100,
            "sentType": 0,
            "receiveType": 0,
            "userTag": "tag1,tag2",
            "returnable": False,
            "rangeType": 1,
            "rangeStoreCode": STORE1,
            "rangeValue": "value",
        },
        # {
        #     "name": "coupon_from_test",
        #     "brief": "test brief",
        #     "couponType": "money_off",
        #     "couponValue": 5,
        #     "effectiveAt": int((time.time() - 3600) * 1000),
        #     "expiredAt": int((time.time() + 3600 * 24) * 1000),
        #     "duration": 0,
        #     "quantity": -1,
        #     "maxReceived": -1,
        #     "unusedLimit": -1,
        #     "thresholdPrice": 100,
        #     "sentType": 0,
        #     "receiveType": 0,
        #     "userTag": "tag1,tag2",
        #     "returnable": False,
        #     # "rangeType": 1, # 0
        #     "rangeStoreCode": STORE1,
        #     "rangeValue": "value",
        # },
        {
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
            "rangeStoreCode": STORE1,
            # "rangeValue": "value",
        },
    ])
    def test_missing_required_params(self, coupon):
        r = MallV2.create_coupon(json=coupon)
        assert r.status_code == 400
        assert r.json()['status'] == 400


    def test_create_coupon_with_code(self):
        '''todo
        '''
        pass


    def test_duplicate_coupon_code(self):
        '''todo
        '''
        pass


    def test_update_coupon(self):
        '''下架优惠券后才能更新
        '''
        # 获取可用sku 价格
        # sku = MallV2.get_cart().json()['data']['skus'][100]
        # Data.update_sku([{"skuId": sku['skuId'], "price": 9900, "originalPrice": 10000}])
        sku = Data.get_skus()[0]
        available_keys = ('storeCode', 'skuId', 'quantity',
                        'ticketCode', 'disablePromotion')

        # tmp = {"cartItemId": sku["id"]}
        tmp = {k: v for k, v in sku.items() if k in available_keys}
        coupon = MallV2.create_coupon(**{
            "thresholdPrice": 1000,
            "couponValue": 1000,
            "rangeType": 1,
            # "rangeStoreCode": tmp["storeCode"],
            "rangeValue": tmp["skuId"],
        }).json()['data']
        MallV2.coupon_shelf(code=coupon['code'], action='on')
        coupon2 = {k: v for k, v in coupon.items() if k in ("id", "code", "name",
                                                            "couponType", "effectiveAt", "expiredAt", "thresholdPrice", "rangeValue")}
        coupon2.update({"couponValue": 2000})
        r = MallV2.update_coupon(**coupon2)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 3004

        MallV2.coupon_shelf(code=coupon['code'], action='off')
        coupon2.update({"couponValue": 2000})
        r = MallV2.update_coupon(**coupon2)
        assert r.status_code == 200
        jsn = r.json()
        assert jsn['status'] == 0

    def test_receive_coupon_off_shelf(self):
        code = MallV2.create_coupon().json()['data']['code']
        r = MallV2.receive_coupon(code=code)
        assert r.status_code == 200
        assert r.json()['status'] == 3004


    def test_offer_coupon_off_shelf(self):
        code = MallV2.create_coupon().json()['data']['code']
        r = MallV2.offer_coupon(code=code)
        assert r.status_code == 200
        assert r.json()['status'] == 3004


    def test_coupon_max_quantity(self):
        '''优惠券：超过最大数量无法领取
        '''
        code = MallV2.create_coupon(**{"quantity": 2}).json()['data']['code']
        MallV2.coupon_shelf(code=code, action='on')
        r = MallV2.receive_coupon(code=code)
        assert r.status_code == 200
        assert r.json()['status'] == 0
        r = MallV2.receive_coupon(code=code, userId=USER_ID2)
        assert r.status_code == 200
        assert r.json()['status'] == 0

        r = MallV2.receive_coupon(code=code)
        assert r.status_code == 200
        assert r.json()['status'] == 3005
        r = MallV2.receive_coupon(code=code, userId=USER_ID2)
        assert r.status_code == 200
        assert r.json()['status'] == 3005


    def test_coupon_max_received(self):
        '''优惠券: 单人领取数限制为1的券，两个人都只能领取1张
        '''
        code = MallV2.create_coupon(**{"maxReceived": 1}).json()['data']['code']
        MallV2.coupon_shelf(code=code, action='on')
        r = MallV2.receive_coupon(code=code)
        assert r.status_code == 200
        assert r.json()['status'] == 0
        r = MallV2.receive_coupon(code=code)
        assert r.status_code == 200
        assert r.json()['status'] == 3006

        r = MallV2.receive_coupon(code=code, userId=USER_ID2)
        assert r.status_code == 200
        assert r.json()['status'] == 0
        r = MallV2.receive_coupon(code=code, userId=USER_ID2)
        assert r.status_code == 200
        assert r.json()['status'] == 3006


    def test_coupon_list(self):
        '''优惠券：获取优惠券列表
        '''
        total = MallV2.user_coupon_list(userId=USER_ID).json()['data']['pagination']['total']
        if total < 10:
            self.test_offer_coupon(USER_ID, 10)
            total += 10
        pageSize = random.randint(1, 5)
        page = math.ceil(total / pageSize)
        r = MallV2.user_coupon_list(userId=USER_ID, pageSize=pageSize, page=page)
        assert r.status_code == 200
        assert len(r.json()['data']['list']) == total - pageSize * (page - 1)
        r = MallV2.user_coupon_list(userId=USER_ID, pageSize=pageSize, page=page+1)
        assert r.status_code == 200
        assert len(r.json()['data']['list']) == 0


    def test_coupon_info(self):
        '''todo
        '''
        r = MallV2.manage_coupon_info(code='7e68c6343de441b6a96dc131056f9a06', allVersion=True)
        assert r.status_code == 404


    @pytest.mark.parametrize('userId, count', [
        (USER_ID, 1)
    ])
    def test_offer_coupon(self, userId, count):
        '''
        '''
        code = MallV2.create_coupon().json()['data']['code']
        MallV2.coupon_shelf(code=code)
        r = MallV2.offer_coupon(code=code, receives=[{"userId": userId, "count": count}])
        assert r.status_code == 200

class TestCouponUpdate():

    def test_update_archived(self):
        '''todo 重复更新同一个coupon id'''
        c = MallV2.create_coupon(brief='v0').json()['data']
        MallV2.coupon_shelf(code=c['code'])
        MallV2.coupon_shelf(code=c['code'], action='off')
        MallV2.update_coupon(id=c['id'], brief='v1')
        r = MallV2.update_coupon(id=c['id'], brief='v2')
        assert r.status_code == 200
        assert r.json()['status'] == 3004
        MallV2.manage_coupon_list(couponCode=c['code'])
        