''' only mall-v2 invoke mock service, 

'''

from utils import post

BASE_URL = 'http://192.168.4.200:5000'

# DJANGO_BASE = 'http://192.168.100.110:8000/mock'

class Url():
    product_detail = BASE_URL + '/pond5/api/v2/product/detail'
    sku_detail = BASE_URL + '/pond5/api/v2/sku/detail'

class TestMock():
    def test_product_detail(self):
        post(Url.product_detail, json=['11c39fd6-9791-4aae-b05c-451efc94807a'])

    def test_sku_detail(self):
        post(Url.sku_detail, json={
            "userId": "10000010",
            "skus": [
                {
                    "skuId": "54b5ecc3293de21a1797afceaa50cc2e",
                    "quantity": 2
                },
            ]
        })


