from requests import request
from config import MALL_BASE_URL, PAY_SITE_BASE_URL
from utils.utils import replace, append

URL_CREATE_ORDER = f'{MALL_BASE_URL}/trade/create'
URL_ORDER_DETAILS = f'{MALL_BASE_URL}/order/{{}}'
URL_PAY = f'{MALL_BASE_URL}/order/{{}}/pay'

def create_order(method='POST', json=None, **kwargs):
    '''
    :param json: {
        "user_id":10265312,
        "expand":{"order_desc":"人世间 冰淇淋 ?22Sep09 14:37:14.206839-作品通","use_package":false},
        "goods":[{"sku_id":"11297732#2800","platform":12,"count":1}]
    }
    '''
    if json is None:
        json = {
            "user_id": 0,
            "expand":{
                "order_desc":"test下单",
                "use_package":False
            },
            "goods":[{"sku_id":"0#2800","platform":12,"count":1}]
        }

    replace(kwargs, json)

    return request(method=method, url=URL_CREATE_ORDER, json=json)

def order_details(order_no, method='GET', params=None, **kwargs):
    if params is None:
        params = {"expand": "detail"}
    replace(kwargs, params)

    return request(method=method, url=URL_ORDER_DETAILS.format(order_no), params=params)

def pay(order_no, method='POST', json=None, **kwargs):
    '''
    ?? !!! data 是 string
    :param json: {"data": {
        "channel":"WX_QR_005",
        "user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "return_url":"https://pay-test.xinpianchang.com/pay/2022092117091900296"
    }} 
    '''
    if json is None:
        json = {
            "data": {
                "channel":"WX_QR_005",
                "user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                "return_url": f"{PAY_SITE_BASE_URL}/pay/{order_no}"
            }
        }
    replace(kwargs, json)
    import json as j
    # data是string 
    json['data'] = j.dumps(json['data'])
    return request(method, url=URL_PAY.format(order_no), json=json)
