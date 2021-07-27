from utils import MallV2, Search, PayAdmin
from config import STORE_RESOURCE
import random

class TestResourceTrade():
    def test_gt_0(self):
        pids = [{"productId": p['productId'], "storeCode": STORE_RESOURCE}
                for p in Search.query().json()['list']]
        products = MallV2.product_detail(json=pids[:]).json()['data']

        skus = [{
            "skuId": sku['skuId'],
            "quantity": 1,
            "storeCode": STORE_RESOURCE
        } for p in products for _, sku in p['data']['productSkuMap'].items()]
        skus=[skus[1]]
        totalPrice = MallV2.trade_confirmation(skus=skus).json()['data']['result']['totalPrice']
        tradeNo = MallV2.trade_submit(skus=skus, totalPriceViewed=totalPrice).json()['data']['trade'][0]
        location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
        token = location.split('/')[-1]
        channels = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']['channelList']
        channel = channels[random.randint(0, len(channels)-1)]
        payload = {
            "channel": channel['channelCode'],
            "token": token,
            "appId": channel['appId'],
        }
        r = MallV2.pay(**payload)
        PayAdmin().fix(r.json()['data']['order'])

    def test_0(self):
        pids = [{"productId": p['productId'], "storeCode": STORE_RESOURCE}
                for p in Search.query().json()['list']]
        products = MallV2.product_detail(json=pids[:]).json()['data']

        skus = [{
            "skuId": sku['skuId'],
            "quantity": 1,
            "storeCode": STORE_RESOURCE
        } for p in products for _, sku in p['data']['productSkuMap'].items()]
        skus=[skus[0]]
        totalPrice = MallV2.trade_confirmation(skus=skus).json()['data']['result']['totalPrice']
        MallV2.trade_submit(skus=skus, totalPriceViewed=totalPrice)

    def test_(self):
        pass