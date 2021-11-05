from utils.mallv2_data import MallV2DB
import pytest
import random
import math
from config import STORE1, STORE3, STORE4, STORE_NOT_EXIST, SKU_ID_NOT_EXIST, USER_ID, USER_ID2, USER_ID3, STORE2
from utils import Data, MallV2, mallv2
from utils.utils import get_logger
import time

log = get_logger(__name__)

# 购物车上限200
CART_MAXIMUM = 200


class TestCartList():
    '''购物车列表
    '''
    def test_cart_list(self):
        '''购物车：查询用户购物车列表
        '''
        r = MallV2.get_cart()
        assert r.status_code == 200
        return r

    def test_cart_list_status(self):
        '''购物车：sku状态跟数据库一致
        '''
        if len(MallV2.get_cart().json()['data']['skus']) < CART_MAXIMUM:
            TestCartAdd().test_full()
        a = {sku['skuId']: sku['status'] for sku in MallV2.get_cart().json()['data']['skus']}
        # b = [(sku['skuId'],sku['status']) for sku in MallV2.get_cart().json()['data']['skus']]
        # assert a == b
        skuIds =  [sku for sku in a]
        # b = Data.sku_status(skus).json()['data']
        b = {sku['skuId']: sku['status'] for sku in Data.get_skus(limit=200, status=None, skus=skuIds)}
        assert b == a

    def test_cart_list_empty(self):
        '''购物车：查询空购物车
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) != 0:
            r = MallV2.remove_cart_item(cartItemIds=[s['id'] for s in skus])
            assert r.status_code == 200
            skus = MallV2.get_cart().json()['data']['skus'] 
        assert skus == [] or skus is None

    
    def test_cart_list_full(self):
        '''购物车: 查询满的购物车
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) < CART_MAXIMUM:
            TestCartAdd().test_full()
            skus = MallV2.get_cart().json()['data']['skus']
        assert len(skus) == CART_MAXIMUM

    def test_post_cart_list(self):
        '''购物车：post请求 404?
        '''
        # r = post(Url.cart_list)
        r = MallV2.get_cart(method='post')
        assert r.status_code == 404

    def test_cart_list_without_user(self):
        '''购物车：不传userId查询购物车列表
        '''
        # r = get(Url.cart_list)
        r = MallV2.get_cart(params={})
        assert r.status_code == 401
        assert r.json()['status'] == 2401

    # def test_sku_in_cart(self):
    #     pass


class TestCartAdd():
    '''
    购物车添加商品
    '''
    @pytest.mark.parametrize('userId', [USER_ID])
    def test_add_some(self, userId):
        '''添加购物车：连续添加20个商品到购物车
        '''
        count = 20
        skus = MallV2.get_cart(userId=userId).json()['data']['skus'] or []
        # 购物车剩余容量不足 删掉一部分
        if CART_MAXIMUM - len(skus) < count:
            to_remove = [s['id'] for s in skus][CART_MAXIMUM - len(skus) - count:]
            MallV2.remove_cart_item(userId=userId, cartItemIds=to_remove)
            skus = MallV2.get_cart(userId=userId).json()['data']['skus']
        # to_add = Data.create_product().json()['data']['skus']
        skus300 = [i['skuId'] for i in Data.get_skus(limit=300)]
        to_add = list(set(skus300) - set([s['skuId']
                      for s in skus]))[:count]
        assert len(to_add) == count
        for sku in to_add:
            r = MallV2.add_to_cart(userId=userId, skuId=sku)
            assert r.status_code == 200
            assert r.json()['status'] == 0
        skus2 = MallV2.get_cart(userId=userId).json()['data']['skus']
        log.info(
            f'add to cart: {len(to_add)}, before: {len(skus)}, after: {len(skus2)}')

    def test_quantity_3(self):
        '''购物车：quantity=3。
        '''
        skus = MallV2.get_cart().json()['data']['skus']
        if len(skus) >= CART_MAXIMUM:
            MallV2.remove_cart_item(cartItemIds=[skus[0]["id"]])
            skuId = skus[0]["skuId"]
        else:
            ss = Data.get_skus(offset=300, status="on_sale")
            skuId = list({i['skuId'] for i in ss} - {i['skuId'] for i in skus})[0]
        r = MallV2.add_to_cart(skuId=skuId, quantity=3)
        assert r.status_code == 200
        # {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        assert r.json()['status'] == 5104


    def test_quantity_0(self):
        '''添加购物车：quantity=0（走默认1）
        '''
        skus_400 = {s['skuId'] for s in Data.get_skus(CART_MAXIMUM * 2)}
        cart = MallV2.get_cart().json()['data']['skus']
        if len(cart) >= CART_MAXIMUM:
            ids = [s['id'] for s in random.sample(cart, k=len(cart) - CART_MAXIMUM + 1)]
            MallV2.remove_cart_item(cartItemIds=ids)
        skus_cart = {s['skuId'] for s in cart}
        skuId = random.choice(list(skus_400 - skus_cart))
        r = MallV2.add_to_cart(skuId=skuId, quantity=0)
        assert r.status_code == 200
        assert r.json()['status'] == 0

    
    def test_quantity_minus_1(self):
        '''添加购物车：quantity=-1。
        '''
        # {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        sku = Data.get_skus()[0]
        r = MallV2.add_to_cart(quantity=-1)
        assert r.status_code == 400
        assert r.json()['status'] == 400

    def test_invalid_store(self):
        '''	添加购物车，不存在的storeCode
        '''
        # {"status":1000,"message":"商品库不存在。"}
        if len(skus := MallV2.get_cart().json()['data']['skus']) >= CART_MAXIMUM:
            MallV2.remove_cart_item(cartItemIds=[skus[1]['id']])
        r = MallV2.add_to_cart(skuId=SKU_ID_NOT_EXIST, storeCode=STORE_NOT_EXIST)
        assert r.status_code == 200
        assert r.json()['status'] == 1000

    
    def test_invalid_skuId(self):
        '''
        添加购物车，不存在的skuId
        '''
        # {“status”:404,”message”:”sku not found”}
        if len(skus := MallV2.get_cart().json()['data']['skus']) >= CART_MAXIMUM:
            MallV2.remove_cart_item(cartItemIds=[skus[1]['id']])
        r = MallV2.add_to_cart(skuId=SKU_ID_NOT_EXIST)
        assert r.status_code == 200
        assert r.json()['status'] == 404
    
    
    @pytest.mark.parametrize('json', [
        {"storeCode": STORE1, "quantity": 1},
        {"quantity": 1, "skuId": "123456"},
    ])
    def test_no_required_param(self, json):
        '''
        添加购物车，不传skuId/storeCode
        '''
        # {“status”:404,”message”:”sku not found”}
        r = MallV2.add_to_cart(json=json)
        assert r.status_code == 400
        assert r.json()['status'] == 400


    def test_no_userId(self):
        '''
        添加购物车，不传userId
        '''
        # {"message": "不合法的请求用户。","status": 2401}
        r = MallV2.add_to_cart(params={})
        assert r.status_code == 401
        assert r.json()['status'] == 2401

    def test_no_quantity(self):
        '''
        添加购物车，不传quantity(默认0)
        '''
        # {“status”:404,”message”:”sku not found”}
        skus = MallV2.get_cart().json()['data']['skus']
        if len(skus) >= CART_MAXIMUM:
            ids = [s['id'] for s in random.sample(skus, k=len(skus) - CART_MAXIMUM + 1)]
            MallV2.remove_cart_item(cartItemIds=ids)
        skus_200 = {s['skuId'] for s in Data.get_skus(limit=200)}
        cart = {s['skuId'] for s in MallV2.get_cart().json()['data']['skus']}
        skuId = (skus_200 - cart).pop()
        r = MallV2.add_to_cart(json={
            "skuId": skuId,
            "storeCode": STORE1
        })
        assert r.status_code == 200
        assert r.json()['status'] == 0

    def test_add_twice(self):
        '''相同sku添加2次，等同于添加两个
        '''

        cart = MallV2.get_cart().json()['data']['skus'] or []
        # 测试10个
        if len(cart) > CART_MAXIMUM - 10:
            to_remove = [s['id'] for s in cart][:10]
            MallV2.remove_cart_item(cartItemIds=to_remove)
            cart = MallV2.get_cart().json()['data']['skus']
        # r = Data.create_product({"skus": [{}]})
        skus = list(set([s['skuId'] for s in Data.get_skus(limit=CART_MAXIMUM)]) - set([it['skuId'] for it in cart]))[:10]

        ids = []
        for sku in skus:
            r = MallV2.add_to_cart(skuId=sku)
            assert r.status_code == 200
            ids.append(r.json()['data']['id'])
        # time.sleep(10)

        for sku in skus:
            r = MallV2.add_to_cart(skuId=sku)
            assert r.status_code == 200
            assert r.json()['data']['id'] == ids.pop(0)

        for sku in skus:
            r = MallV2.add_to_cart(skuId=sku)
            assert r.status_code == 200
            assert r.json()['status'] == 5104
        cart2 = MallV2.get_cart().json()['data']['skus']
        assert len(cart2) == len(skus) + len(cart)

    
    def test_full(self):
        '''添加购物车：如果购物车不满 添加到满
        '''
        # TestCartRemove().test_clear_invalid_cart_item(userId)
        skus = MallV2.get_cart().json()['data']['skus'] or []
        # if len(skus) >= CART_MAXIMUM:
        #     # 清空
        #     log.info(f'cart 满了, 清空')
        #     MallV2.remove_cart_item(cartItemIds=[s['id'] for s in skus])
        #     skus = MallV2.get_cart().json()['data']['skus']
        #     assert len(skus) == 0
        if len(skus) < CART_MAXIMUM:
            skus2 = Data.get_skus(300)
            for skuId in list(set([s['skuId'] for s in skus2]) - set([s['skuId'] for s in skus]))[:CART_MAXIMUM - len(skus)]:
                r = MallV2.add_to_cart(skuId=skuId)
                assert r.status_code == 200
                assert r.json()['status'] == 0

            # log.info(f'before: {len(skus)}, loops: {v}, skus2.length: {len(skus)}, set: {len(set([s["skuId"] for s in skus2]))}')

            skus = MallV2.get_cart().json()['data']['skus']
        assert len(skus) == CART_MAXIMUM
        self.skus = skus

    
    def test_more_than_full(self):
        '''购物车：满了后再添加
        '''
        self.test_full()

        skus2 = Data.get_skus(210, 300)
        skuIds2 = {s['skuId'] for s in skus2}
        skuIds = {s['skuId'] for s in self.skus}
        log.info(f'{len(skuIds2)}, {len(skuIds)}, 差：{len(skuIds2 - skuIds)}')
        # 确保有
        assert len(skuIds2 - skuIds) > 1
        for skuId in list(skuIds2 - skuIds)[:10]:
            r = MallV2.add_to_cart(skuId=skuId)
            assert r.status_code == 200
            # {"status":5106,"message":"购物车已满，最多200个"}
            assert r.json()['status'] == 5106

        res = MallV2.get_cart()
        assert len(res.json()['data']['skus']) == CART_MAXIMUM


class TestCartUpdate():
    '''更新购物车单个商品的数量'''

    def test_update_cart_item_quantity(self):
        '''购物车更新: 购物车item数量。可用值1/2；0/3 报错'''

        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            for sku in Data.get_skus():
                MallV2.add_to_cart(skuId=sku['skuId'])
            skus = MallV2.get_cart().json()['data']['skus']

        # 移除无效商品
        MallV2.remove_cart_item(isRemoveAllInvalid=True)

        before = [(sku['id'], sku['quantity']) for sku in skus]
        expectation = [(it[0], math.floor(random.random() * 4))
                       for it in before]
        res = []
        for cart_id, amount in expectation:
            res.append(MallV2.update_cart_item_quantity(cartItemId=cart_id, quantity=amount))
        r = MallV2.get_cart()
        after = [(sku['id'], sku['quantity'])
                 for sku in r.json()['data']['skus']]

        log.info(
            f'\n{"before":<15}: {before}\n{"expectation":<15}: {expectation}\n{"after":<15}: {after}')
        for i in range(len(after)):
            if expectation[i][1] in (1, 2):
                assert after[i] == expectation[i]
                assert res[i].json()['status'] == 0, f'{expectation[i][0]}'
                # result['success'].append(expectation[i])
            else:
                assert after[i] == before[i]
                # >2: {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
                # 0: {"status":400,"message":"quantity is required and not empty"}
                if expectation[i][1] > 2:
                    assert res[i].json()[
                        'status'] == 5104, f'{expectation[i][0]}'
                    # result['>2'].append(expectation[i])
                else:
                    # set quantity = 0
                    assert res[i].json()['status'] == 400
                    # result['0'].append(expectation[i])
        # log.debug(result)

    def test_update_quantity_more_than_2(self):
        '''购物车更新：购物车item数量 >2
        '''
        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            for sku in Data.get_skus():
                MallV2.add_to_cart(skuId=sku['skuId'])
            skus = MallV2.get_cart().json()['data']['skus']

        # 移除无效商品
        MallV2.remove_cart_item(isRemoveAllInvalid=True)

        before = [(sku['id'], sku['quantity']) for sku in skus]
        expectation = [(it[0], random.randint(3, 100))
                       for it in before]
        res = []
        for cart_id, amount in expectation:
            res.append(MallV2.update_cart_item_quantity(cartItemId=cart_id, quantity=amount))
        r = MallV2.get_cart()
        after = [(sku['id'], sku['quantity'])
                 for sku in r.json()['data']['skus']]

        log.info(
            f'\n{"before":<15}: {before}\n{"expectation":<15}: {expectation}\n{"after":<15}: {after}')
        for i in range(len(after)):
            assert after[i] == before[i]
            assert res[i].json()['status'] == 5104
            # >2: {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
                


    def test_missing_required_params(self):
        '''
        购物车更新，缺少参数quantity/cartItemId/userId
        '''
        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']

        cart_item1 = skus[0]

        r = MallV2.update_cart_item_quantity(json={
                "cartItemId": cart_item1['id'], 
                # "quantity": 1
            })
        # {"status":400,"message":"quantity is required and not empty"}
        assert r.status_code == 400
        assert r.json()['status'] == 400

        r = MallV2.update_cart_item_quantity(json={
                # "cartItemId": cart_item1['id'], 
                "quantity": 1
            })
        # {"status":400,"message":"quantity is required and not empty"}
        assert r.status_code == 400
        assert r.json()['status'] == 400

        r = MallV2.update_cart_item_quantity(params={}, json={
                "cartItemId": cart_item1['id'], 
                "quantity": 1
            })
        # {"status":2401,"message":"不合法的请求用户。"}
        assert r.status_code == 401
        assert r.json()['status'] == 2401
        
        cart_item2 = MallV2.get_cart().json()['data']['skus'][0]
        assert cart_item2["quantity"] == cart_item1["quantity"]

    def test_update_others_cart(self):
        '''
        购物车更新，他人的cartItemId
        '''
        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']

        cart_item1 = skus[0]

        r = MallV2.update_cart_item_quantity(userId=USER_ID2, json={
                "cartItemId": cart_item1['id'], 
                "quantity": 2 if cart_item1['quantity'] == 1 else 1
            })
        
        assert r.status_code == 404
        assert r.json()['status'] == 404

        cart_item2 = MallV2.get_cart().json()['data']['skus'][0]
        assert cart_item2['quantity'] == cart_item1['quantity']
        assert cart_item2['id'] == cart_item1['id']

    def test_update_deleted_cart(self):
        '''
        购物车更新，不存在的cartItemId
        '''
        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']

        cart_item1 = skus[0]
        MallV2.remove_cart_item(cartItemIds=[cart_item1['id']])
        r = MallV2.update_cart_item_quantity(json={
                "cartItemId": cart_item1['id'], 
                "quantity": 2 if cart_item1['quantity'] == 1 else 1
            })
        
        assert r.status_code == 404
        assert r.json()['status'] == 404

class TestCartSelect():
    '''购物车item选中
    用户的操作：单个选/单个不选/全选/全不选/反选
    #不存在的id
    '''

    @pytest.mark.parametrize('selected',[
        'random',
        'reverse',
        True, 
        False,
    ])
    def test_select_cart_item(self, selected):
        '''购物车：随机单个购物车商品选中或者取消选中
        '''
        # cart前多少个
        test = -1

        r1 = MallV2.get_cart()
        # time.sleep(10)
        skus = r1.json()['data']['skus'][:test]
        # before = [(s['id'], s['selected']) for s in skus]
        # log.info(f'{[b[0] for b in before]},{set([b[0] for b in before])}')
        # assert len([b[0] for b in before]) == len(set([b[0] for b in before]))
        if selected == 'random':
            expectations = [(s['id'], random.choice((True, False))) for s in skus]
        elif selected == 'reverse':
            expectations = [(s['id'], False if s['selected'] else True) for s in skus]
        else:
            expectations = [(s['id'], selected) for s in skus]
        
        for i in expectations:
            r2 = MallV2.select_cart_item(cartItemIds=[i[0]], selected=i[1])
            assert r2.status_code == 200
        # time.sleep(30)
        r3 = MallV2.get_cart()
        after = [(s['id'], s['selected'])
                 for s in r3.json()['data']['skus'][:test]]
        # log.info(f'before selected: {before}')
        # log.info(f'expectation    : {expectations}')
        # log.info(f'after  selected: {after}')
        assert after == expectations


    def test_select_others(self):
        '''购物车：选中他人购物车商品
        '''
        # cart超过一半，随机选中/未选状态
        skus = MallV2.get_cart().json()['data']['skus']
        if len(skus) < 20:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']
        tmp = {s['id']:random.choice([True, False]) for s in skus}
        to_select = [k for k, v in tmp.items() if v is True]
        to_deselect = [k for k, v in tmp.items() if v is False]
        MallV2.select_cart_item(cartItemIds=to_select, selected=True)
        MallV2.select_cart_item(cartItemIds=to_deselect, selected=False)
        skus = MallV2.get_cart().json()['data']['skus']
        
        ss = [(s['id'],s['selected']) for s in skus]
        selected = [s[0] for s in ss if s[1] is True]
        unselected = [s[0] for s in ss if s[1] is False]
        skus3 = MallV2.get_cart(userId=USER_ID2).json()['data']['skus']
        r1 = MallV2.select_cart_item(userId=USER_ID2, cartItemIds=unselected, selected=True)
        assert r1.status_code == 200
        assert r1.json()['status'] == 400
        r2 = MallV2.select_cart_item(userId=USER_ID2, cartItemIds=selected, selected=False)
        assert r1.status_code == 200
        assert r1.json()['status'] == 400

        skus2 = MallV2.get_cart().json()['data']['skus']
        # skus2 = [(s['id'],s['selected']) for s in cart]
        skus4 = MallV2.get_cart(userId=USER_ID2).json()['data']['skus']
        for c in (skus, skus2, skus3, skus4):
            for s in c:
                s.pop('updatedAt')
                s.pop('validateAt')
        assert skus2 == skus
        assert skus4 == skus3

    @pytest.mark.parametrize('selected', [
        'random',
        'reverse',
        True, 
        False
    ])
    def test_batch_select_cart_item(self, selected):
        '''购物车：如果购物车有，批量反选
        selected str: random|reverse|on_sale|True/False 
        '''

        skus = MallV2.get_cart().json()['data']['skus'] or []
        
        expectations = {True:[], False:[]}
        if selected == 'random':
            for s in skus:
                expectations[random.choice((True, False))].append(s['id'])
        elif selected == 'reverse':
            for s in skus:
                expectations[False if s['selected'] else True].append(s['id'])
        elif selected == 'on_sale':
            for s in skus:
                expectations[True].append(s['id']) if s['status'] == 'on_sale' else expectations[False].append(s['id'])
        else:
            for s in skus:
                expectations[selected].append(s['id'])


        for k, v in expectations.items():
            if v:
                r2 = MallV2.select_cart_item(cartItemIds=v, selected=k)
                assert r2.status_code == 200
                assert r2.json()['status'] == 0

        r3 = MallV2.get_cart()
        after = {True:[], False:[]}
        for s in r3.json()['data']['skus']:
            after[s['selected']].append(s['id'])
        
        # 顺序一样？？
        assert after == expectations


    def test_full_cart_select(self):
        TestCartAdd().test_full()
        for selected in ("random", "reverse", True, False):
            self.test_batch_select_cart_item(selected)


    def test_storeCode_after_bulk_select(self):
        '''购物车：批量反选 
        批量选中 导致storeCode被改
        '''
        skus = MallV2.get_cart().json()['data']['skus']
        if skus:
            MallV2.remove_cart_item(cartItemIds=[s['id'] for s in skus])
        
        skus = Data.get_skus(200)
        cart = {}
        for s in skus:
            storeCode = random.choice([STORE1, STORE2, STORE3, STORE4])
            cartId = MallV2.add_to_cart(skuId=s['skuId'], storeCode=storeCode).json()['data']['id']
            cart[cartId] = storeCode
        # skus = MallV2.get_cart().json()['data']['skus']
        for store in (STORE1, STORE2, STORE3, STORE4):
            s = [k for k, v in cart.items() if v == store]
            r = MallV2.select_cart_item(cartItemIds=s)
        
            assert r.status_code == 200
            assert r.json()['status'] == 0

        skus = MallV2.get_cart().json()['data']['skus']
        real = {s['id']: s['storeCode'] for s in skus}
        assert len(real) == 200
        assert real == cart

        selected = [s for s in skus if s['selected'] is True]
        assert len(selected) == 200
        

    def test_select_deleted(self):
        '''购物车: 选中不存在的购物车id
        '''
        skus = MallV2.get_cart().json()['data']['skus']
        if len(skus) < 10:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']
        sid = skus[0]['id']
        r = MallV2.select_cart_item(cartItemIds=[sid])
        assert r.status_code == 200
        assert r.json()['status'] == 0
        MallV2.remove_cart_item(cartItemIds=[sid])
        r = MallV2.select_cart_item(cartItemIds=[sid])
        # {"status":400,"message":"参数有误：CartItemIds 不合法。"}
        assert r.status_code == 200
        assert r.json()['status'] == 400
    
    def test_illegal_cart_id(self):
        '''cartItemIds里有他人的cartItemId'''
        skus = MallV2.get_cart().json()['data']['skus']
        if len(skus) < 20:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']
        tmp = {s['id']:random.choice([True, False]) for s in skus}
        to_select = [k for k, v in tmp.items() if v is True]
        to_deselect = [k for k, v in tmp.items() if v is False]
        MallV2.select_cart_item(cartItemIds=to_select, selected=True)
        MallV2.select_cart_item(cartItemIds=to_deselect, selected=False)
        skus = MallV2.get_cart().json()['data']['skus']
        
        ss = [(s['id'],s['selected']) for s in skus]
        selected = [s[0] for s in ss if s[1] is True]
        unselected = [s[0] for s in ss if s[1] is False]
        skus3 = MallV2.get_cart(userId=USER_ID2).json()['data']['skus']
        if len(skus3) < 20:
            TestCartAdd().test_add_some(USER_ID2)
            skus3 = MallV2.get_cart(userId=USER_ID2).json()['data']['skus']
        
        r1 = MallV2.select_cart_item(userId=USER_ID, cartItemIds=[skus3[0]['id']] + unselected, selected=True)
        assert r1.status_code == 200
        assert r1.json()['status'] == 400
        r2 = MallV2.select_cart_item(userId=USER_ID, cartItemIds=[skus3[0]['id']] + selected, selected=False)
        assert r1.status_code == 200
        assert r1.json()['status'] == 400

        skus2 = MallV2.get_cart().json()['data']['skus']
        # skus2 = [(s['id'],s['selected']) for s in cart]
        skus4 = MallV2.get_cart(userId=USER_ID2).json()['data']['skus']
        for c in (skus, skus2, skus3, skus4):
            for s in c:
                s.pop('updatedAt')
                s.pop('validateAt')
        assert skus2 == skus
        assert skus4 == skus3

    def test_re_select(self):
        '''购物车: 重复选中
        '''
        skus = MallV2.get_cart().json()['data']['skus']
        if len(skus) < 10:
            TestCartAdd().test_add_some(USER_ID)
            skus = MallV2.get_cart().json()['data']['skus']
        exp = []
        for i in range(len(skus)):
            sid = skus[i]['id']
            for _ in range(2):
                selected = random.choice([True, False])
                r = MallV2.select_cart_item(cartItemIds=[sid], selected=selected)
                assert r.status_code == 200
                assert r.json()['status'] == 0
            exp.append({sid: selected})
        assert [{s['id']: s['selected']} for s in MallV2.get_cart().json()['data']['skus']] == exp
        


class TestCartRemove():
    '''todo 购物车item移除
    #不存在的id
    '''

    def test_remove_cart_item(self):
        '''购物车： 随机移除cart_item
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) < 100:
            for skuId in set([s['skuId'] for s in Data.get_skus(50)]):
                MallV2.add_to_cart(skuId=skuId)
            skus = MallV2.get_cart().json()['data']['skus']

        cart_items = [sku['id'] for sku in skus]
        to_remove = random.sample(cart_items, k=math.ceil(
            random.random() * len(cart_items)))

        MallV2.remove_cart_item(cartItemIds=to_remove)

        cart_items2 = [sku['id'] for sku in MallV2.get_cart().json()[
            'data']['skus']]
        log.info(
            f'to remove {len(to_remove)} cart items from {USER_ID} \'s {len(skus)}; after: {len(cart_items2)} ')
        assert set(cart_items2) == set(cart_items) - set(to_remove)
        assert set(to_remove) & set(cart_items2) == set()

    def test_remove_single_cart_item(self):
        ''' 购物车：移除单个cart item 
        '''

        skus = MallV2.get_cart().json()['data']['skus']
        if not skus:
            for sku in Data.get_skus():
                MallV2.add_to_cart(skuId=sku['skuId'])
            skus = MallV2.get_cart().json()['data']['skus']
        cart_items = [sku['id'] for sku in skus]

        to_remove = random.sample(cart_items, k=math.ceil(
            random.random() * len(cart_items)))

        MallV2.remove_cart_item(cartItemIds=to_remove)

        cart_items2 = [sku['id'] for sku in MallV2.get_cart().json()[
            'data']['skus']]
        log.info(
            f'remove from cart: {len(to_remove)}, before: {len(cart_items)}, after: {len(cart_items2)}')
        assert set(cart_items2) == set(cart_items) - set(to_remove)
        assert set(to_remove) & set(cart_items2) == set()

    
    def test_clear_cart(self):
        ''' 购物车：清空cart item。如果cart是空的 先添加
        '''

        skus = MallV2.get_cart().json()['data']['skus'] or []
        if not skus:
            for sku in Data.get_skus():
                MallV2.add_to_cart(skuId=sku['skuId'])
            skus = MallV2.get_cart().json()['data']['skus'] or []
        cart_items = [sku['id'] for sku in skus]

        MallV2.remove_cart_item(cartItemIds=cart_items)

        skus2 = MallV2.get_cart().json()['data']['skus'] or []
        log.info(
            f'remove all from cart, before: {len(skus)}, after: {len(skus2)}')
        assert len(skus2) == 0

    
    def test_remove_others_cart(self):
        '''购物车：移除别人的cart item id
        '''
        carts2 = MallV2.get_cart(userId=USER_ID2).json()['data']['skus']
        if not carts2:
            for sku in Data.get_skus():
                MallV2.add_to_cart(skuId=sku['skuId'], userId=USER_ID2)
            carts2 = MallV2.get_cart().json()['data']['skus']

        r = MallV2.remove_cart_item(cartItemIds=[carts2[0]['id']])
        assert r.status_code == 200
        assert r.json()['status'] == 400


    def test_clear_invalid_cart_item(self):
        '''
        购物车：移除无效商品
        on_sale/insufficent
        off_shelf/out_of_stock/404/store_failed
        '''

        cart = MallV2.get_cart().json()['data']['skus'] or []
        if len(cart) > 0:
            MallV2.remove_cart_item(cartItemIds=[s['id'] for s in cart])

        pskus = Data.get_skus(100, offset=2)
        for sku in pskus: MallV2.add_to_cart(skuId=sku['skuId'])
        
        skus = MallV2.get_cart().json()['data']['skus'] or []
        cart_items_ids = [s['id'] for s in skus]

        
        status = ('off_shelf', '404', 'store_failed', 'out_of_stock', 'on_sale', 'insufficent', 'store_vip_only')
        for i in range(len(skus)):
            skus[i]['status'] = status[i % len(status)]
            
        arr = [{"skuId": sku['skuId'], "status": sku['status']} for sku in skus if sku["status"] != "on_sale"]
        Data.update_sku(arr)

        to_delete_ids = [sku["id"] for sku in skus if sku["status"] != "on_sale"]

        MallV2.remove_cart_item(isRemoveAllInvalid=True)
        
        cart_items_ids3 = [sku['id'] for sku in MallV2.get_cart().json()['data']['skus']]
        log.info(f'before: {cart_items_ids}, removed: {to_delete_ids}, after: {cart_items_ids3}')

        assert set(cart_items_ids3) == set(cart_items_ids) - set(to_delete_ids)

    def test_remove_non_existed(self):
        '''购物车：重复移除 移除不存在的id
        '''
        carts = MallV2.get_cart().json()['data']['skus']
        if not carts:
            TestCartAdd().test_add_some(USER_ID)
            carts = MallV2.get_cart().json()['data']['skus']

        r = MallV2.remove_cart_item(cartItemIds=[carts[0]['id']])
        assert r.status_code == 200
        assert r.json()['status'] == 0
        r = MallV2.remove_cart_item(cartItemIds=[carts[0]['id']])
        assert r.status_code == 200
        assert r.json()['status'] == 400