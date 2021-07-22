from requests import delete, get, post
from config import USER_ID, STORE1
from . import mallv2 as MallV2

DJANGO_BASE = 'https://t.vmovier.cc'

class MallV2DB():
    '''mall-v2 数据库管理
    '''
    _DELETE_USER_COUPONS = DJANGO_BASE + '/user/{userId}/coupons'
    _DELETE_USER_TICKETS = DJANGO_BASE + '/user/{userId}/tickets'
    _DELETE_TICKETS = DJANGO_BASE + '/tickets'

    @staticmethod
    def delete_user_coupons(userId=USER_ID):
        r = delete(MallV2DB._DELETE_USER_COUPONS.format(userId=userId))
        assert r.status_code == 200
        return r

    @staticmethod
    def delete_user_tickets(userId=USER_ID):
        r = delete(MallV2DB._DELETE_USER_TICKETS.format(userId=userId))
        assert r.status_code == 200
        return r

    @staticmethod
    def delete_tickets(tickets=[]):
        r = delete(MallV2DB._DELETE_TICKETS, json=tickets)
        assert r.status_code == 200
        return r
    

class Data():
    '''mock商品库数据管理
    storeCode 暂时没用
    todo：接了真正的商品库，每个接口都应该传storeCode
    '''

    _CREATE_PRODUCT = DJANGO_BASE + '/{storeCode}/product'
    _DELETE_SKUS = DJANGO_BASE + '/skus'
    _GET_SKUS = DJANGO_BASE + '/skus'
    _UPDATE_SKU = DJANGO_BASE + '/skus'
    _CHANGE_SKUS_STATUS = DJANGO_BASE + '/skus/status'
    _CHANGE_SKU = DJANGO_BASE + '/sku/{skuId}'
    
    @staticmethod
    def create_product(json=None, storeCode=STORE1):
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
        if storeCode.startswith('mock'):
            if status:
                kwargs['status'] = status
            params = {"page": page, "size": size, **kwargs}
            if skus:
                params['skus'] = skus
            r = get(Data._GET_SKUS, params=params)
            assert r.status_code == 200
            return r
        else:
            r = get(
                'http://192.168.4.200:5006/rpc/pub/v1/search/query',
                # params={"productTypes": ["footage", "music"]}
            )
            pids = [{'productId': p['productId'], 'storeCode': storeCode} for p in r.json()['list']]
            p = [{'productId': p['productId'], 'productType': p['productType']} for p in r.json()['list']]
            r = MallV2.product_detail(json=pids[:])
            return r


    @staticmethod
    def update_sku(jsn):
        r = post(Data._UPDATE_SKU, json=jsn)
        assert r.status_code == 200
        return r