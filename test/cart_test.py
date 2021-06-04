import pytest
import time
import random
import math
import logging
from utils import post, get
from config import Url, STORE1, STORE_NOT_EXIST, SKU_ID_NOT_EXIST, USER_ID, USER_ID2
from utils import Data, MallV2


log = logging.getLogger('cart_test')

# 购物车上限200
CART_MAXIMUM = 200


class TestCartList():

    

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_cart_list(self, userId):
        '''购物车：查询用户购物车列表
        '''
        r = MallV2.get_cart(userId)
        assert r.status_code == 200
        return r

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_cart_list_empty(self, userId):
        '''购物车：空购物车
        '''
        skus = MallV2.get_cart(userId).json()['data']['skus']
        if len(skus) != 0:
            r = MallV2.remove_cart_item(userId, [s['id'] for s in skus])
            assert r.status_code == 200
            skus = MallV2.get_cart(userId).json()['data']['skus']
        assert skus == []

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_cart_list_full(self, userId):
        '''购物车: 满购物车
        '''
        skus = MallV2.get_cart(userId).json()['data']['skus']
        if len(skus) < CART_MAXIMUM:
            TestCartAdd().test_add_cart_until_full(userId)
            skus = MallV2.get_cart(userId).json()['data']['skus']
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
        assert r.status_code == 400

    # def test_sku_in_cart(self):
    #     pass


class TestCartAdd():
    '''
    购物车添加商品
    '''

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_add_until_half(self, userId):
        '''添加购物车：连续添加购物车 一半购物车的数量
        '''
        skus = MallV2.get_cart(userId).json()['data']['skus']
        # 购物车超过一半 清空
        if len(skus) >= CART_MAXIMUM/2:
            to_remove = [s['id'] for s in skus]
            MallV2.remove_cart_item(userId, to_remove)
            skus = MallV2.get_cart(userId).json()['data']['skus']
        # to_add = Data.create_product().json()['data']['skus']
        skus300 = [i['skuId'] for i in Data.get_skus(size=300).json()['data']]
        to_add = list(set(skus300) - set([s['skuId']
                      for s in skus]))[:int(CART_MAXIMUM/2)]

        for sku in to_add:
            r = MallV2.add_to_cart(userId, sku)
            assert r.status_code == 200
            assert r.json()['status'] == 0
        skus2 = MallV2.get_cart(userId).json()['data']['skus']
        log.info(
            f'add to cart: {len(to_add)}, before: {len(skus)}, after: {len(skus2)}')



    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_greater_quantity(self, userId):
        '''购物车：同一sku添加3个。{"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        '''
        sku = Data.get_skus().json()['data'][0]
        r = MallV2.add_to_cart(userId, sku['skuId'], quantity=3)
        assert r.status_code == 200
        assert r.json()['status'] == 5104

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_0_quantity(self, userId):
        '''购物车：同一sku添加0个。{"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        '''
        sku = Data.get_skus(400).json()['data'][-1]
        r = MallV2.add_to_cart(userId, sku['skuId'], quantity=0)
        assert r.status_code == 400
        assert r.json()['status'] == 400

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_minus_1_quantity(self, userId):
        '''购物车：同一sku添加-1个。{"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        '''
        sku = Data.get_skus().json()['data'][0]
        r = post(Url.cart_add, params={"userId":userId}, json={
            "skuId": sku,
            "quantity": -1,
            "storeCode": STORE1
        })
        assert r.status_code == 400
        assert r.json()['status'] == 400

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_invalid_store(self, userId):
        '''
        {"status":1000,"message":"商品库不存在。"}
        '''
        r = post(Url.cart_add, params={"userId":userId}, json={
            "skuId": SKU_ID_NOT_EXIST,  # 不校验
            "quantity": 1,
            "storeCode": STORE_NOT_EXIST
        })
        assert r.status_code == 200
        assert r.json()['status'] == 1000

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_invalid_skuid(self, userId):
        '''
        {"status":404,"message":"sku not found"}
        '''
        r = post(Url.cart_add, params={"userId":userId}, json={
            "skuId": SKU_ID_NOT_EXIST,
            "quantity": 1,
            "storeCode": STORE1
        })
        assert r.status_code == 200
        assert r.json()['status'] == 404

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_add_cart_twice(self, userId):
        '''#商品库逻辑相同sku最多可以添加购物车2个
        '''

        cart = MallV2.get_cart(userId).json()['data']['skus']
        # 购物车超过一半 清空
        if len(cart) > CART_MAXIMUM/2:
            to_remove = [s['id'] for s in cart]
            MallV2.remove_cart_item(
                userId, to_remove[:int(CART_MAXIMUM/2)])
            cart = MallV2.get_cart(userId).json()['data']['skus']
        # r = Data.create_product({"skus": [{}]})
        skus = list(set([s['skuId'] for s in Data.get_skus(size=CART_MAXIMUM).json()[
                    'data']]) - set([it['skuId'] for it in cart]))[:int(CART_MAXIMUM/4)]

        ids = []
        for sku in skus:
            r = MallV2.add_to_cart(userId, sku)
            assert r.status_code == 200
            ids.append(r.json()['data']['id'])
        # time.sleep(10)

        for sku in skus:
            r = MallV2.add_to_cart(userId, sku)
            assert r.status_code == 200
            assert r.json()['data']['id'] == ids.pop(0)

        for sku in skus:
            r = MallV2.add_to_cart(userId, sku)
            assert r.status_code == 200
            assert r.json()['status'] == 5104
        cart2 = MallV2.get_cart(userId).json()['data']['skus']
        assert len(cart2) == len(skus) + len(cart)

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_add_cart_until_full(self, userId):
        '''购物车：添加到满
        '''
        # TestCartRemove().test_clear_invalid_cart_item(userId)
        skus = MallV2.get_cart(userId).json()['data']['skus']
        if len(skus) >= CART_MAXIMUM:
            # 清空
            log.info(f'cart 满了, 清空')
            MallV2.remove_cart_item(userId, [s['id'] for s in skus])
            skus = MallV2.get_cart(userId).json()['data']['skus']
            assert len(skus) == 0
        # 有重复数据 多取一些去重
        length1 = len(skus)

        skus2 = Data.get_skus(300).json()['data']
        for skuId in list(set([s['skuId'] for s in skus2]) - set([s['skuId'] for s in skus]))[:200 - length1]:
            r = MallV2.add_to_cart(userId, skuId)
            assert r.status_code == 200
            assert r.json()['status'] == 0
        

        # log.info(f'before: {len(skus)}, loops: {v}, skus2.length: {len(skus)}, set: {len(set([s["skuId"] for s in skus2]))}')
        
        res = MallV2.get_cart(userId)
        assert len(res.json()['data']['skus']) == CART_MAXIMUM

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_add_cart_more_than_full(self, userId):
        '''购物车：满了后再添加 {"status":5106,"message":"购物车已满，最多200个"}
        '''
        skus = MallV2.get_cart(userId).json()['data']['skus']
        if len(skus) >= CART_MAXIMUM:
            # 清空
            log.info(f'cart 满了, 清空')
            MallV2.remove_cart_item(userId, [s['id'] for s in skus])
            skus = MallV2.get_cart(userId).json()['data']['skus']
            assert len(skus) == 0

        skus2 = Data.get_skus(300, 2).json()['data']
        skuIds2 = set([s['skuId'] for s in skus2])
        skuIds = set([s['skuId'] for s in skus])
        log.info(f'{len(skuIds2)}, {len(skuIds)}, 差：{len(skuIds2 - skuIds)}')
        assert len(skuIds2 - skuIds) > 200
        cart_len = len(skuIds)
        for skuId in skuIds2 - skuIds:
            r = MallV2.add_to_cart(userId, skuId)
            
            assert r.status_code == 200
            if cart_len < CART_MAXIMUM:
                assert r.json()['status'] == 0
                cart_len += 1
            else:
                assert r.json()['status'] == 5106
            
        
        res = MallV2.get_cart(userId)
        assert len(res.json()['data']['skus']) == CART_MAXIMUM

class TestCartUpdate():
    '''
    #不存在的id 404
    #别人的id
    '''

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_update_cart_item_quantity(self, userId):
        '''购物车：更新购物车item数量。可用值1/2
        >2: {"status":5104,"message":"操作失败了，原因：限购，库存检查失败"}
        0: {"status":400,"message":"quantity is required and not empty"}
        '''
        skus = MallV2.get_cart(userId).json()['data']['skus']

        if not skus:
            for sku in Data.get_skus().json()['data']:
                MallV2.add_to_cart(userId, sku['skuId'])
            skus = MallV2.get_cart(userId).json()['data']['skus']

        # 移除无效商品
        MallV2.remove_invalid(userId)

        before = [(sku['id'], sku['quantity']) for sku in skus]
        expectation = [(it[0], math.floor(random.random() * 4))
                       for it in before]
        res = []
        for cart_id, amount in expectation:
            res.append(MallV2.update_cart_item_quantity(userId, cart_id, amount))
        r = MallV2.get_cart(userId)
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
                    assert res[i].json()['status'] == 5104, f'{expectation[i][0]}'
                    # result['>2'].append(expectation[i])
                else:
                    # set quantity = 0
                    assert res[i].json()['status'] == 400
                    # result['0'].append(expectation[i])
        # log.debug(result)

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_update_cart_1_quantity(self, userId):
        '''
        #todo: 
        '''

        cart_item1 = MallV2.get_cart(userId).json()['data']['skus'][0]

        MallV2.update_cart_item_quantity(userId, cart_item1['id'], 1 if cart_item1['quantity'] == 2 else 2)

        cart_item2 = MallV2.get_cart(userId).json()['data']['skus'][0]
        log.info(
            f'\n{"before":<15}: {cart_item1["quantity"]}\n{"after":<15}: {cart_item2["quantity"]}')
        assert cart_item2["quantity"] != cart_item1["quantity"]


class TestCartSelect():
    '''购物车item选中
    用户的操作：单个选/单个不选/全选/全不选/反选
    #不存在的id
    #别人的id
    '''

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_select_cart_item(self, userId):
        '''购物车：随机单个选中或者取消选中购物车item
        '''
        r1 = MallV2.get_cart(userId)
        skus = r1.json()['data']['skus']
        before = [(s['id'], s['selected']) for s in skus]
        expectations = [(s['id'], random.choice((True, False))) for s in skus]
        for i in expectations:
            r2 = MallV2.select_cart_item(userId, [i[0]], i[1])
            assert r2.status_code == 200
        r3 = MallV2.get_cart(userId)
        after = [(s['id'], s['selected']) for s in r3.json()['data']['skus']]
        log.info(f'after selected: {after}')
        assert after == expectations

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_batch_select_cart_item(self, userId):
        '''购物车：反选
        '''
        r1 = MallV2.get_cart(userId)
        skus = r1.json()['data']['skus']
        before = [(s['id'], s['selected']) for s in skus]
        log.info(f'before selected: {before}')
        expectations = [(s['id'], False if s['selected'] else True)
                        for s in skus]

        selected_cart_items = [e[0] for e in expectations if e[1]]
        r2 = MallV2.select_cart_item(userId, selected_cart_items, True)
        assert r2.status_code == 200

        unselected_cart_items = [e[0] for e in expectations if not e[1]]
        r4 = MallV2.select_cart_item(userId, unselected_cart_items, False)
        assert r4.status_code == 200

        r3 = MallV2.get_cart(userId)
        after = [(s['id'], s['selected']) for s in r3.json()['data']['skus']]
        log.info(f'after selected: {after}')
        assert after == expectations


class TestCartRemove():
    '''购物车item移除
    #不可用商品？？
    #不存在的id
    #别人的id
    '''


    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_remove_cart_item(self, userId):
        '''购物车： 随机移除cart_item
        '''
        skus = MallV2.get_cart(userId).json()['data']['skus']
        if len(skus) < 100:
            for skuId in set([s['skuId'] for s in Data.get_skus(50).json()['data']]):
                MallV2.add_to_cart(userId, skuId)
            skus = MallV2.get_cart(userId).json()['data']['skus']

        cart_items = [sku['id'] for sku in skus]
        to_remove = random.sample(cart_items, k=math.ceil(
            random.random() * len(cart_items)))

        MallV2.remove_cart_item(userId, to_remove)

        cart_items2 = [sku['id'] for sku in MallV2.get_cart(userId).json()[
            'data']['skus']]
        log.info(
            f'to remove {len(to_remove)} cart items from {userId} \'s {len(skus)}; after: {len(cart_items2)} ')
        assert set(cart_items2) == set(cart_items) - set(to_remove)
        assert set(to_remove) & set(cart_items2) == set()

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_remove_single_cart_item(self, userId):
        ''' 购物车：移除单个cart item 
        '''

        skus = MallV2.get_cart(userId).json()['data']['skus']
        if not skus:
            for sku in Data.get_skus().json()['data']:
                MallV2.add_to_cart(userId, sku['skuId'])
            skus = MallV2.get_cart(userId).json()['data']['skus']
        cart_items = [sku['id'] for sku in skus]

        to_remove = random.sample(cart_items, k=math.ceil(
            random.random() * len(cart_items)))

        MallV2.remove_cart_item(userId, to_remove)

        cart_items2 = [sku['id'] for sku in MallV2.get_cart(userId).json()[
            'data']['skus']]
        log.info(
            f'remove from cart: {len(to_remove)}, before: {len(cart_items)}, after: {len(cart_items2)}')
        assert set(cart_items2) == set(cart_items) - set(to_remove)
        assert set(to_remove) & set(cart_items2) == set()

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_clear_cart(self, userId):
        ''' 购物车：清空cart item。如果cart是空的 先添加
        '''

        skus = MallV2.get_cart(userId).json()['data']['skus']
        if not skus:
            for sku in Data.get_skus().json()['data']:
                MallV2.add_to_cart(userId, sku['skuId'])
            skus = MallV2.get_cart(userId).json()['data']['skus']
        cart_items = [sku['id'] for sku in skus]

        MallV2.remove_cart_item(userId, cart_items)

        skus2 = MallV2.get_cart(userId).json()['data']['skus']
        log.info(
            f'remove all from cart, before: {len(skus)}, after: {len(skus2)}')
        assert len(skus2) == 0

    @pytest.mark.parametrize('userId, userId2', [
        (USER_ID, USER_ID2)
    ])
    def test_remove_others_cart(self, userId, userId2):
        '''购物车：移除别人的cart item id
        '''
        carts2 = MallV2.get_cart(userId2).json()['data']['skus']
        if not carts2:
            for sku in Data.get_skus().json()['data']:
                MallV2.add_to_cart(userId2, sku['skuId'])
            carts2 = MallV2.get_cart(userId2).json()['data']['skus']

        r = MallV2.remove_cart_item(userId, [carts2[0]['id']])
        assert r.status_code == 200
        assert r.json()['status'] == 400

    @pytest.mark.parametrize('userId', [
        USER_ID
    ])
    def test_clear_invalid_cart_item(self, userId):
        '''
        todo: 购物车：移除无效商品
        '''
        r1 = MallV2.get_cart(userId)
        skus = r1.json()['data']['skus']
        cart_items_ids = [sku['id'] for sku in skus]
        log.info(f'before: {cart_items_ids}')

        to_delete_ids = [sku["id"] for sku in skus if sku["status"] == "404"]

        log.info(f'sku 404: {to_delete_ids}')
        if not to_delete_ids:
            k = math.ceil(random.random() * len(cart_items_ids))
            to_delete_items = random.sample(skus, k=k)
            to_delete_ids = [s["id"] for s in to_delete_items]
            log.info(f'delete {k} skus form Store database: {to_delete_ids}')
            time.sleep(5)
            x = Data.delete_skus([s["skuId"] for s in to_delete_items])
            assert x.status_code == 200

            time.sleep(30)
            r2 = MallV2.get_cart(userId)
            items_404 = [sku['id'] for sku in r2.json()['data']['skus'] if sku['status'] == '404']
            log.info(f'sku 404 after deleted: {items_404}')
            assert set(to_delete_ids) == set(items_404)

        
        MallV2.remove_invalid(userId)

        r3 = MallV2.get_cart(userId)
        cart_items_ids3 = [sku['id'] for sku in r3.json()['data']['skus']]
        log.info(f'after invalid removed: {cart_items_ids3}')

        assert set(cart_items_ids3) == set(cart_items_ids) - set(to_delete_ids)

    
