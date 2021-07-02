import pytest
import random
import math
import logging
from utils import post, get
from config import STORE1, STORE3, STORE4, STORE_NOT_EXIST, SKU_ID_NOT_EXIST, USER_ID, USER_ID2, USER_ID3, USER_ID_TANGYE, STORE2
from utils import Data, MallV2, Url
from collections import defaultdict
import time

log = logging.getLogger('cart_test')

# 购物车上限200
CART_MAXIMUM = 200


class TestCartList():

    def test_cart_list(self):
        '''购物车：查询用户购物车列表
        '''
        r = MallV2.get_cart()
        assert r.status_code == 200
        return r

    def test_cart_list_status(self):
        '''tangy 购物车状态不对
        '''
        a = {sku['skuId']: sku['status'] for sku in MallV2.get_cart().json()['data']['skus']}
        # b = [(sku['skuId'],sku['status']) for sku in MallV2.get_cart().json()['data']['skus']]
        # assert a == b
        skuIds =  [sku for sku in a]
        # b = Data.sku_status(skus).json()['data']
        b = {sku['skuId']: sku['status'] for sku in Data.get_skus(size=200, status=None, skus=','.join(skuIds)).json()['data']}
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
            TestCartAdd().test_add_cart_until_full()
            skus = MallV2.get_cart().json()['data']['skus']
        assert len(skus) == CART_MAXIMUM

    def test_post_cart_list(self):
        '''购物车：post请求 404?
        '''
        r = post(Url.cart_list)
        assert r.status_code == 404

    def test_cart_list_without_user(self):
        '''购物车：不传userId查询购物车列表
        '''
        r = get(Url.cart_list)
        assert r.status_code == 401
        assert r.json()['status'] == 2401

    # def test_sku_in_cart(self):
    #     pass


class TestCartAdd():
    '''
    购物车添加商品
    '''

    def test_add_half_of_cart_capacity(self):
        '''添加购物车：连续添加购物车 一半购物车的数量 100
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        # 购物车超过一半 清空
        if len(skus) > CART_MAXIMUM/2:
            to_remove = [s['id'] for s in skus]
            MallV2.remove_cart_item(cartItemIds=to_remove)
            skus = MallV2.get_cart().json()['data']['skus']
        # to_add = Data.create_product().json()['data']['skus']
        skus300 = [i['skuId'] for i in Data.get_skus(size=300).json()['data']]
        to_add = list(set(skus300) - set([s['skuId']
                      for s in skus]))[:int(CART_MAXIMUM/2)]
        assert len(to_add) == int(CART_MAXIMUM/2)
        for sku in to_add:
            r = MallV2.add_to_cart(skuId=sku)
            assert r.status_code == 200
            assert r.json()['status'] == 0
        skus2 = MallV2.get_cart().json()['data']['skus']
        log.info(
            f'add to cart: {len(to_add)}, before: {len(skus)}, after: {len(skus2)}')

    def test_greater_quantity(self):
        '''购物车：同一sku添加3个。{"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        '''
        sku = Data.get_skus().json()['data'][0]
        r = MallV2.add_to_cart(skuId=sku['skuId'], quantity=4)
        assert r.status_code == 200
        assert r.json()['status'] == 5104

    # @pytest.mark.parametrize('userId', [
    #     USER_ID
    # ])
    # def test_0_quantity(self, userId):
    #     '''不存在的情况！！购物车：同一sku添加0个。{"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
    #     '''
    #     sku = Data.get_skus(400).json()['data'][-1]
    #     r = MallV2.add_to_cart(skuId=userId, sku['skuId'], quantity=0)
    #     assert r.status_code == 400
    #     assert r.json()['status'] == 400

    
    def test_minus_1_quantity(self):
        '''购物车：同一sku添加-1个。{"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        '''
        sku = Data.get_skus().json()['data'][0]
        r = post(Url.cart_add, params={"userId": USER_ID}, json={
            "skuId": sku,
            "quantity": -1,
            "storeCode": STORE1
        })
        assert r.status_code == 400
        assert r.json()['status'] == 400

    def test_invalid_store(self):
        '''
        {"status":1000,"message":"商品库不存在。"}
        '''
        r = post(Url.cart_add, params={"userId": USER_ID}, json={
            "skuId": SKU_ID_NOT_EXIST,  # 不校验
            "quantity": 1,
            "storeCode": STORE_NOT_EXIST
        })
        assert r.status_code == 200
        assert r.json()['status'] == 1000

    
    def test_invalid_skuId(self):
        '''
        {"status":404,"message":"sku not found"}
        '''
        r = post(Url.cart_add, params={"userId": USER_ID}, json={
            "skuId": SKU_ID_NOT_EXIST,
            "quantity": 1,
            "storeCode": STORE1
        })
        assert r.status_code == 200
        assert r.json()['status'] == 404

    
    def test_add_cart_twice(self):
        '''#商品库逻辑相同sku最多可以添加购物车2个
        '''

        cart = MallV2.get_cart().json()['data']['skus'] or []
        # 购物车超过一半 清空
        if len(cart) > CART_MAXIMUM/2:
            to_remove = [s['id'] for s in cart]
            MallV2.remove_cart_item(cartItemIds=
                to_remove[:int(CART_MAXIMUM/2)])
            cart = MallV2.get_cart().json()['data']['skus']
        # r = Data.create_product({"skus": [{}]})
        skus = list(set([s['skuId'] for s in Data.get_skus(size=CART_MAXIMUM).json()[
                    'data']]) - set([it['skuId'] for it in cart]))[:int(CART_MAXIMUM/4)]

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

    
    def test_add_cart_until_full(self):
        '''购物车：添加到满
        '''
        # TestCartRemove().test_clear_invalid_cart_item(userId)
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) >= CART_MAXIMUM:
            # 清空
            log.info(f'cart 满了, 清空')
            MallV2.remove_cart_item(cartItemIds=[s['id'] for s in skus])
            skus = MallV2.get_cart().json()['data']['skus']
            assert len(skus) == 0

        skus2 = Data.get_skus(300).json()['data']
        for skuId in list(set([s['skuId'] for s in skus2]) - set([s['skuId'] for s in skus]))[:200 - len(skus)]:
            r = MallV2.add_to_cart(skuId=skuId)
            assert r.status_code == 200
            assert r.json()['status'] == 0

        # log.info(f'before: {len(skus)}, loops: {v}, skus2.length: {len(skus)}, set: {len(set([s["skuId"] for s in skus2]))}')

        res = MallV2.get_cart()
        assert len(res.json()['data']['skus']) == CART_MAXIMUM

    
    def test_add_cart_more_than_full(self):
        '''购物车：满了后再添加 {"status":5106,"message":"购物车已满，最多200个"}
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) >= CART_MAXIMUM:
            # 清空
            log.info(f'cart 满了, 清空')
            MallV2.remove_cart_item(cartItemIds=[s['id'] for s in skus])
            skus = MallV2.get_cart().json()['data']['skus'] or []
            assert len(skus) == 0

        skus2 = Data.get_skus(300, 2).json()['data']
        skuIds2 = set([s['skuId'] for s in skus2])
        skuIds = set([s['skuId'] for s in skus])
        log.info(f'{len(skuIds2)}, {len(skuIds)}, 差：{len(skuIds2 - skuIds)}')
        # 确保超出最大值
        assert len(skuIds2 - skuIds) > CART_MAXIMUM
        cart_len = len(skuIds)
        for skuId in skuIds2 - skuIds:
            r = MallV2.add_to_cart(skuId=skuId)

            assert r.status_code == 200
            if cart_len < CART_MAXIMUM:
                assert r.json()['status'] == 0
                cart_len += 1
            else:
                assert r.json()['status'] == 5106

        res = MallV2.get_cart()
        assert len(res.json()['data']['skus']) == CART_MAXIMUM


class TestCartUpdate():
    '''
    #不存在的id 404
    #别人的id
    '''

    def test_update_cart_item_quantity(self):
        '''购物车：更新购物车item数量。可用值1/2
        >2: {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        0: {"status":400,"message":"quantity is required and not empty"}
        '''
        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            for sku in Data.get_skus().json()['data']:
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
        '''购物车：更新购物车item数量。可用值1/2
        >2: {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        '''
        skus = MallV2.get_cart().json()['data']['skus']

        if not skus:
            for sku in Data.get_skus().json()['data']:
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
            
            assert res[i].json()[
                'status'] == 5104, f'{expectation[i][0]}'
            # result['>2'].append(expectation[i])
                


    def test_update_cart_1_quantity(self):
        '''
        #todo: 
        '''

        cart_item1 = MallV2.get_cart().json()['data']['skus'][0]

        MallV2.update_cart_item_quantity(cartItemId=cart_item1['id'], quantity=1 if cart_item1['quantity'] == 2 else 2)

        cart_item2 = MallV2.get_cart().json()['data']['skus'][0]
        log.info(
            f'\n{"before":<15}: {cart_item1["quantity"]}\n{"after":<15}: {cart_item2["quantity"]}')
        assert cart_item2["quantity"] != cart_item1["quantity"]


class TestCartSelect():
    '''购物车item选中
    用户的操作：单个选/单个不选/全选/全不选/反选
    #不存在的id
    #别人的id
    '''

    def test_select_cart_item(self):
        '''购物车：随机单个选中或者取消选中购物车item
        '''
        # cart前多少个
        test = -1

        r1 = MallV2.get_cart()
        time.sleep(10)
        skus = r1.json()['data']['skus'][:test]
        before = [(s['id'], s['selected']) for s in skus]
        # log.info(f'{[b[0] for b in before]},{set([b[0] for b in before])}')
        # assert len([b[0] for b in before]) == len(set([b[0] for b in before]))
        expectations = [(s['id'], random.choice((True, False))) for s in skus]
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
        '''todo: 购物车：选中他人购物车商品
        '''
        pass


    def test_reversely_select_cart_item(self):
        '''购物车：单个反选
        '''
        # cart前多少个
        test = -1

        r1 = MallV2.get_cart()
        # time.sleep(5)
        skus = r1.json()['data']['skus'][:test]
        before = [(s['id'], s['selected']) for s in skus]
        # log.info(f'{[b[0] for b in before]},{set([b[0] for b in before])}')
        # assert len([b[0] for b in before]) == len(set([b[0] for b in before]))
        # expectations = [(s['id'], random.choice((True, False))) for s in skus]
        expectations = [(s[0], True if not s[1] else False) for s in before]
        for i in expectations:
            r2 = MallV2.select_cart_item(cartItemIds=[i[0]], selected=i[1])
            assert r2.status_code == 200
        # time.sleep(30)
        r3 = MallV2.get_cart()
        after = [(s['id'], s['selected'])
                 for s in r3.json()['data']['skus'][:test]]
        log.info(f'before selected: {before}')
        log.info(f'expectation    : {expectations}')
        log.info(f'after  selected: {after}')
        assert after == expectations

    def test_batch_select_cart_item(self):
        '''购物车：批量反选
        todo 有可能传空
        '''

        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) < 50:
            skus = Data.get_skus(100).json()['data']
            for s in skus:
                MallV2.add_to_cart(skuId=s['skuId'])
            skus = MallV2.get_cart().json()['data']['skus']
        if len(set([s['selected'] for s in skus])) < 2:
            self.test_select_cart_item()
        before = [(s['id'], s['selected']) for s in skus]
        log.info(f'before selected: {before}')
        expectations = [(s['id'], False if s['selected'] else True)
                        for s in skus]

        selected_cart_items = [e[0] for e in expectations if e[1]]
        r2 = MallV2.select_cart_item(cartItemIds=selected_cart_items, selected=True)
        assert r2.status_code == 200
        assert r2.json()['status'] == 0

        unselected_cart_items = [e[0] for e in expectations if not e[1]]
        r4 = MallV2.select_cart_item(cartItemIds=unselected_cart_items, selected=False)
        assert r4.status_code == 200
        assert r4.json()['status'] == 0

        r3 = MallV2.get_cart()
        after = [(s['id'], s['selected']) for s in r3.json()['data']['skus']]
        log.info(f'after selected: {after}')
        assert after == expectations

    def test_storeCode_after_bulk_select(self):
        '''购物车：批量反选 
        批量选中 导致storeCode被改
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if skus:
            MallV2.remove_cart_item(cartItemIds=[s['id'] for s in skus])
        
        skus = Data.get_skus(200).json()['data']
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
        


class TestCartRemove():
    '''购物车item移除
    #不可用商品？？
    #不存在的id
    #别人的id
    '''

    def test_remove_cart_item(self):
        '''购物车： 随机移除cart_item
        '''
        skus = MallV2.get_cart().json()['data']['skus'] or []
        if len(skus) < 100:
            for skuId in set([s['skuId'] for s in Data.get_skus(50).json()['data']]):
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
            for sku in Data.get_skus().json()['data']:
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
            for sku in Data.get_skus().json()['data']:
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
            for sku in Data.get_skus().json()['data']:
                MallV2.add_to_cart(skuId=sku['skuId'], userId=USER_ID2)
            carts2 = MallV2.get_cart().json()['data']['skus']

        r = MallV2.remove_cart_item(cartItemIds=[carts2[0]['id']])
        assert r.status_code == 200
        assert r.json()['status'] == 400


    def test_clear_invalid_cart_item(self):
        '''
        todo: 购物车：移除无效商品
        on_sale
        off_shelf/out_of_stock/404/store_failed
        '''

        cart = MallV2.get_cart().json()['data']['skus'] or []
        if len(cart) > 0:
            MallV2.remove_cart_item(cartItemIds=[s['id'] for s in cart])

        pskus = Data.get_skus(100, page=2).json()['data']
        for sku in pskus: MallV2.add_to_cart(skuId=sku['skuId'])
        
        skus = MallV2.get_cart().json()['data']['skus'] or []
        cart_items_ids = [s['id'] for s in skus]

        
        status = ('off_shelf', '404', 'store_failed', 'out_of_stock', 'on_sale')
        for i in range(len(skus)):
            skus[i]['status'] = status[i % len(status)]
            
        arr = [{"skuId": sku['skuId'], "status": sku['status']} for sku in skus if sku["status"] != "on_sale"]
        assert Data.update_sku(arr).status_code == 200

        to_delete_ids = [sku["id"] for sku in skus if sku["status"] != "on_sale"]

        MallV2.remove_cart_item(isRemoveAllInvalid=True)
        
        r3 = MallV2.get_cart()
        cart_items_ids3 = [sku['id'] for sku in r3.json()['data']['skus']]
        log.info(f'before: {cart_items_ids}, removed: {to_delete_ids}, after: {cart_items_ids3}')

        assert set(cart_items_ids3) == set(cart_items_ids) - set(to_delete_ids)
