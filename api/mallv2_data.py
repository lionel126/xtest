from requests import delete, get, post
from config import USER_ID, STORE1, TESTAPI_BASE
from . import mallv2 as MallV2
from utils.utils import fake


class MallV2DB():
    '''mall-v2 数据库管理
    '''
    _DELETE_USER_COUPONS = TESTAPI_BASE + '/user/{userId}/coupons'
    _DELETE_USER_TICKETS = TESTAPI_BASE + '/user/{userId}/tickets'
    _DELETE_TICKETS = TESTAPI_BASE + '/tickets'

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
    def delete_tickets(tickets=None):
        if tickets is None:
            tickets = []
        r = delete(MallV2DB._DELETE_TICKETS, json=tickets)
        assert r.status_code == 200
        return r


class Data():
    '''mock商品库数据管理
    storeCode 暂时没用
    todo：接了真正的商品库，每个接口都应该传storeCode
    '''

    _CREATE_PRODUCT = TESTAPI_BASE + '/{storeCode}/product'
    _DELETE_SKUS = TESTAPI_BASE + '/skus'
    _GET_SKUS = TESTAPI_BASE + '/skus'
    _UPDATE_SKU = TESTAPI_BASE + '/skus'
    _CHANGE_SKUS_STATUS = TESTAPI_BASE + '/skus/status'
    _CHANGE_SKU = TESTAPI_BASE + '/sku/{skuId}'

    @staticmethod
    def create_product(json=None, storeCode=STORE1):
        '''storeCode没有用：目前只有一个mock server
        {
            "id": 9074,
            "productBrief": "励志的/振奋人心",
            "productId": "08e90ab2-af9b-4ca2-9ec5-ee897ecd0fa2",
            "productImg": "https://oss-xpc0.xpccdn.com/Upload/edu/2018/09/115b976c23b867d.jpg",
            "productName": "勇敢 打 工人 - 2021-07-27 174826.132144",
            "productType": "music",
            "promotionBadge": null,
            "promotionLabel": null,
            "promotionTags": null,
            "shopId": "shopX"
            "skus": [
                {
                    "id": 12873,
                    "originalPrice": 100000,
                    "price": 99900,
                    "productId": "08e90ab2-af9b-4ca2-9ec5-ee897ecd0fa2",
                    "promotionBadge": null,
                    "promotionLabel": null,
                    "promotionTags": [
                        "tag-a1c643ab-cd7a-41c6-9a2b-f5c601d44711"
                    ],
                    "skuBrief": "sku brief desc",
                    "skuId": "bdbbac94-8664-4cdc-950e-d4f1a49871b6",
                    "skuImg": "https://oss-xpc0.xpccdn.com/Upload/edu/2018/09/115b976c23b867d.jpg?_sku",
                    "skuProp": "29_1,200",
                    "skuTitle": "",
                    "status": "on_sale",
                    "stock": 5
                }
            ]
        }
        '''
        r = post(Data._CREATE_PRODUCT.format(storeCode=storeCode), json=json)
        assert r.status_code == 200
        return r.json()['data']

    @staticmethod
    def delete_skus(json=[]):
        # r = delete(Data._DELETE_SKUS, json=json)
        r = post(Data._DELETE_SKUS, json=json)
        assert r.status_code == 200


    @staticmethod
    def get_skus(limit=10, offset=None, status='on_sale', storeCode=STORE1, skus=None, **kwargs):
        '''default: status = on_sale
        商品库暂时没提供商品列表接口
        预留storeCode 暂时无用。多个mock商品库 实际连接同一个mock服务：相同商品 不同storeCode
        '''
        # if storeCode.startswith('mock'):
        if offset is None:
            offset = fake.random_int(0, int(5000/limit)) * limit # 表里sku数量: 5000。 有可能越界
        if status:
            kwargs['status'] = status
        params = {"offset": offset, "limit": limit, **kwargs}
        if skus:
            params['skus'] = skus
        r = get(Data._GET_SKUS, params=params)
        assert r.status_code == 200
        return [{
                    "skuId": s["skuId"],
                    "status": s["status"],
                    "price": s["price"]
                } for s in r.json()["data"]]
        # return r
        # else:
        #     """temporary"""
        #     r = get(
        #         'http://192.168.4.200:5006/rpc/pub/v1/search/query',
        #         # params={"productTypes": ["footage", "music"]}
        #     )
        #     pids = [{'productId': p['productId'], 'storeCode': storeCode} for p in r.json()['list']]
        #     p = [{'productId': p['productId'], 'productType': p['productType']} for p in r.json()['list']]
        #     r = MallV2.product_detail(json=pids[:])
        #     return r

    @staticmethod
    def update_sku(jsn):
        r = post(Data._UPDATE_SKU, json=jsn)
        assert r.status_code == 200
        
