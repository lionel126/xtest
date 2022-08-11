from requests import request
from api import MallV2, PayAdmin
from utils.utils import get_available_channel
from config import STORE_RESOURCE, STOCK_BASE_URL



url = f'{STOCK_BASE_URL}/nuxt-api-v2/search/query?stockType=footage&productTypes=footage&q=&duration=&resolution=&aspectRatio=&sort=default&page={{}}&pageSize=60&personalPriceRange=&enterprisePriceRange=&isAlpha=0&isLoop=0&userId=10265312&firstCategoryId=1&from=searchtop&_keyword='



def test_stock():
    skus = []
    for page in range(1, 2):
        r = request('GET', url.format(page))
        pids = [{"productId": p['productId'], "storeCode": STORE_RESOURCE} for p in r.json()['list']]
        products = MallV2.product_detail(json=pids[:]).json()['data']

        skus.extend([{
            "skuId": sku['skuId'],
            "quantity": 1,
            "storeCode": STORE_RESOURCE
        } for p in products for _, sku in p['data']['productSkuMap'].items()])
    
    skus=[skus[0]]
    totalPrice = MallV2.trade_confirmation(skus=skus).json()['data']['result']['totalPrice']
    tradeNo = MallV2.trade_submit(skus=skus, totalPriceViewed=totalPrice, disableAccount=True).json()['data']['trade'][0]
    location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
    token = location.split('/')[-1]
    channels = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']['channelList']
    # channel = channels[random.randint(0, len(channels)-1)]
    channel = get_available_channel(channels, location, 'WX_QR_')
    # payload = {
    #     "channel": channel['channelCode'],
    #     "token": token,
    #     "appId": channel['appId'],
    # }
    r = MallV2.pay(**channel)
    PayAdmin().fix(r.json()['data']['order'])

