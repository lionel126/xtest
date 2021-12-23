from api import MallV2, PayAdmin
from utils.utils import fake, get_available_channel
import random

class TestTicketSale():
    def test_(self):
        payload = {
            "skus": [{
                # "skuId": "6e9815327d9e44ddab4f9a881d7385db",
                "skuId": "ad7e1d14026311ecab5c000c2972099a",
                "quantity": 1,
                "storeCode": "ticket"
            }]
        }
        totalPrice = MallV2.trade_confirmation(json=payload).json()['data']['result']['totalPrice']

        r = MallV2.trade_submit(json=payload| {"totalPriceViewed": totalPrice})
        tradeNo = r.json()['data']['trade'][0]
        location = MallV2.trade_token(tradeNo=tradeNo).json()['data']['location']
        token = location.split('/')[-1]
        channels = MallV2.trade_detail(tradeNo=tradeNo, token=token).json()['data']['channelList']
        # channel = channels[fake.random_int(0, len(channels)-1)]
        channel = get_available_channel(channels, location)
        
        r = MallV2.pay(**channel)
        PayAdmin().fix(r.json()['data']['order'])