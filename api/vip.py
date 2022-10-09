from requests import request
from config import VIP_CENTER_BASE_URL
from utils.utils import replace, append

URL_WX_SUBSCRIBE = f'{VIP_CENTER_BASE_URL}/__door/vip/trigger_wx_subscribe_by_user_id'
URL_WX_PAPAY = f'{VIP_CENTER_BASE_URL}/__door/vip/trigger_wx_subscribe_notify_by_user_id'

URL_CRON_WX_SUBSCRIBE = f'{VIP_CENTER_BASE_URL}/__door/vip/cron/wx_subscribe'
URL_CRON_WX_PAPAY = f'{VIP_CENTER_BASE_URL}/__door/vip/cron/papay_notice'
URL_CRON_SNS_NOTICE = f'{VIP_CENTER_BASE_URL}/__door/vip/cron/sns_notice'
URL_CRON_SMS_NOTICE = f'{VIP_CENTER_BASE_URL}/__door/vip/cron/sms_notice'
URL_CRON_SEND_COUPON = f'{VIP_CENTER_BASE_URL}/__door/vip/cron/send_coupon'

URL_TRIGGER_USER_STATUS = f'{VIP_CENTER_BASE_URL}/__door/vip/trigger_status'

URL_CANCEL_SUBSCRIBE = f'{VIP_CENTER_BASE_URL}/vip/cancel_subscribe'

URL_GIFTCARD = f'{VIP_CENTER_BASE_URL}/__door/giftcard/generate'
URL_EXCHANGE_GIFTCARD = f'{VIP_CENTER_BASE_URL}/gift_card/exchange'

def trigger_status(method='POST', url=URL_TRIGGER_USER_STATUS, json=None, auth=None):
    '''
    :param json:{
        'userId': 10000000,
        'group': 'sns'
    }
    '''
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, json=json, auth=auth)

def wx_subsribe(method='POST', url=URL_WX_SUBSCRIBE, params=None, auth=None):
    '''
    :param params: {'user_id': 10000000}
    '''
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, params=params, auth=auth)

def wx_papay(method='POST', url=URL_WX_PAPAY, params=None, auth=None):
    '''
    :param params: {'user_id': 10000000}
    '''
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, params=params, auth=auth)

def cron_wx_subsribe(method='POST', url=URL_CRON_WX_SUBSCRIBE, auth=None):
    
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, auth=auth)

def cron_wx_papay(method='POST', url=URL_CRON_WX_PAPAY, auth=None):
    
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, auth=auth)

def cron_sns_notice(method='POST', url=URL_CRON_SNS_NOTICE, auth=None):
    
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, auth=auth)

def cron_sms_notice(method='POST', url=URL_CRON_SMS_NOTICE, auth=None):
    
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, auth=auth)

def cron_send_coupon(method='POST', url=URL_CRON_SEND_COUPON, auth=None):
    
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    return request(method, url, auth=auth)


def cancel_subscribe(method='POST', url=URL_CANCEL_SUBSCRIBE, params=None):
    '''
    :param params={"user_id": 10000000}:
    http://mall.test.xinpianchang.com/server-api/subscribe/notify?contract_code=C20220419143400N00388&contract_id=202204195746772071&model_id=147013&contract_termination_mode=2&enable=false&user_id=11487157&pay_channel=WX_QR_CONTRACT_005&out_trade_no=20220419143400109791&trace_no=20220419143400000387
    '''
    return request(method, url, params=params)

def generate_giftcard(method='POST', url=URL_GIFTCARD, auth=None, json=None, **kwargs):
    '''
    :param json: default
       {
            "name": "618普通会员vip_14month卡 ",
            "meta": [
                {
                "expiredAt": 1755189520000,
                "cardType": "vip_14month",
                "num": 1,
                "effectiveAt": 1655189520000,
                "cardCategory": 80
                }
            ],
            "remark": "618"
        }
    '''
    if auth is None: auth = ('vmovier', 'ilovevmovier')
    if json is None: 
        json={
            "name": "618普通会员vip_14month卡 ",
            "meta": [
                {
                "expiredAt": 1755189520000,
                "cardType": "vip_14month",
                "num": 1,
                "effectiveAt": 1655189520000,
                "cardCategory": 80
                }
            ],
            "remark": "618"
        }
    replace(kwargs, json)
    return request(method, url, auth=auth, json=json)

def exchange_giftcard(method='POST', url=URL_EXCHANGE_GIFTCARD, json=None):
    '''
    {"user_id":10265312,"card_category":80,"card_no":"1280331420892933"}
    '''
    return request(method, url, json=json)