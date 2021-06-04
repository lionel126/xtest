import requests
from functools import partial
from config import Url
import config

get = partial(getattr(requests, 'get'), **{"verify": False})
post = partial(getattr(requests, 'post'), **{"verify": False})
put = partial(getattr(requests, 'put'), **{"verify": False})
delete = partial(getattr(requests, 'delete'), **{"verify": False})

# for req_method in ('get', 'post', 'delete', 'patch', 'put'):
#     globals()[req_method] = partial(getattr(requests, req_method), **{"verify": False})


DJANGO_BASE = 'http://t.vmovier.cc'


class Data():

    _CREATE_PRODUCT = DJANGO_BASE + '/{storeCode}/product'
    _DELETE_SKUS = DJANGO_BASE + '/skus'
    _GET_SKUS = DJANGO_BASE + '/skus'
    _CHANGE_SKU_STATUS = DJANGO_BASE + '/skus/status'

    @staticmethod
    def create_product(json=None, storeCode=config.StoreCode):
        r = post(Data._CREATE_PRODUCT.format(storeCode=storeCode), json=json)
        return r

    @staticmethod
    def delete_skus(json=[]):
        # r = delete(Data._DELETE_SKUS, json=json)
        r = post(Data._DELETE_SKUS, json=json)
        return r

    @staticmethod
    def get_skus(size=10, page=0, status='on_sale', **kwargs):
        if status:
            kwargs['status'] = status
        r = get(Data._GET_SKUS, params={"page": page, "size": size, **kwargs})
        return r

    @staticmethod
    def sku_status(jsn):
        '''修改sku status
        '''
        return post(Data._CHANGE_SKU_STATUS, json=jsn)


class MallV2():

    @staticmethod
    def get_cart(userId):
        params = {"userId": userId} if userId else None
        r = get(Url.cart_list, params=params)
        # assert r.status_code == 200
        return r

    @staticmethod
    def add_to_cart(userId, sku, store=config.STORE1, quantity=1):
        params = {"userId": userId} if userId else None
        r = post(Url.cart_add, params=params, json={
            "skuId": sku,
            "quantity": quantity,
            "storeCode": store
        })
        # assert r.status_code == 200
        return r

    @staticmethod
    def remove_cart_item(userId, items_to_remove):
        params = {"userId": userId} if userId else None
        r = post(Url.cart_remove, params=params, json={
            'cartItemIds': items_to_remove,
            # 'isRemoveAllInvalid': True
        })
        # assert r.status_code == 200
        return r

    @staticmethod
    def remove_invalid(userId):
        '''
        '''
        params = {"userId": userId} if userId else None
        r = post(Url.cart_remove, params=params, json={
            # 'cartItemIds': items_to_remove,
            'isRemoveAllInvalid': True
        })
        # assert r.status_code == 200
        return r

    @staticmethod
    def update_cart_item_quantity(userId, cartItemId, quantity):
        params = {"userId": userId} if userId else None
        return post(Url.cart_update_quantity, params=params, json={
            "cartItemId": cartItemId,
            "quantity": quantity
        })

    @staticmethod
    def select_cart_item(userId, cartItemIds, selected=True):
        params = {"userId": userId} if userId else None
        return post(Url.cart_select, params=params, json={
            "cartItemIds": cartItemIds,
            "selected": selected,
        })