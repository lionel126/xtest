# 临时测试用的 

import time, json
import datetime as dt
import pytest
from api import vip, Data, MallV2, MallV2DB, PayAdmin, Url
from api.user_center import InternalApi as UserInt
from config import STORE_VIP
from utils.utils import get_available_channel
from utils import user as userutils
from api.user_center import Sess, InternalApi


def test_user_center_vip_status():
    UserInt.vip_notify(user_id=10265312, type=2, flag=7, start_time='20220101', end_time='20230201')


def test_sync_vip_status():
    vip.trigger_status(json={"userId": 11487935, "group": "sns"})


def test_wx_subscribe():
    # {'force': 'true'}
    vip.wx_subsribe(params={'user_id': 11487161})


def test_wx_papay():
    '''
    '''
    vip.wx_papay(params={'user_id': 11487267})


def test_cron_wx_papay():
    vip.cron_wx_papay()


def test_cron_wx_subscribe():
    vip.cron_wx_subsribe()


def test_cron_sns_notice():
    vip.cron_sns_notice()


def test_cron_sms_notice():
    vip.cron_sms_notice()


def test_cron_send_coupon():
    vip.cron_send_coupon()


@pytest.mark.parametrize('userId, skuId, pay_channel_prefix', [
    (10487227, 'v_general_month', 'WX'),
    # (11488173, 'v_general_quarter', 'ZFB'),

    # (11487227, 'v_general_month', 'ZFB'),
    # (11488131, 'v_general_quarter', 'ZFB'),

    # (11488206, 'v_general_year', 'WX'),
    # (11488229, 'v_super_month', 'WX'),
    # (11488131, 'v_super_year', 'ZFB'),
    # (11487470, 'v_super_2year'),

    # 不能补单 ？: 新模版无法下单
    # todo怎么续订下单？
    # todo iap
    # (10487227, 'v_general_month_subscribe', 'WX')
    # (11488200, 'v_general_quarter_subscribe', 'WX')

    # (11488131, 'v_general_year_subscribe', 'WX_QR'),
    # (11488131, 'v_super_month_subscribe', 'WX_QR'),

    # (11488200,'NewStudios_VIP_Month_Sub', 'WX'),
    # (11487270,'NewStudios_VIP_Quarter_Sub', 'WX'),

])
def test_purchase_vip(userId, skuId, pay_channel_prefix):
    '''
    '''
    sku1 = {"skuId": skuId, "quantity": 1, "storeCode": STORE_VIP}
    ka = {"userId": userId, "skus": [sku1]}
    totalPriceViewed = MallV2.trade_confirmation(
        **ka).json()['data']['result']['totalPrice']
    trades = MallV2.trade_submit(
        ** ka | {"totalPriceViewed": totalPriceViewed}).json()['data']['trade']

    assert len(trades) == 1
    tradeNo = trades[0]
    location = MallV2.trade_token(userId=userId, tradeNo=tradeNo).json()[
        'data']['location']
    token = location.split('/')[-1]
    data = MallV2.trade_detail(
        userId=userId, tradeNo=tradeNo, token=token).json()['data']

    # channel = data['channelList'][random.randint(0, len(data['channelList'])-1)]
    channel = get_available_channel(
        data['channelList'], location, pay_channel_prefix)
    price = data['price']

    order = MallV2.pay(**channel).json()['data']['order']
    PayAdmin().fix(order)


@pytest.mark.parametrize('userId, skus, expectation', [
    
    # # 非订阅 + 非订阅 
    # # 相同package
    # (0, [('v_general_month', 'WX'), ('v_general_month', 'WX')], {"end_time": "+59", "flag": 1, "package_type": "month", "start_time": "", "subscribe": 0}),
    # (11488175, [('v_general_month', 'WX'), ('v_general_month', 'ZFB')], {"end_time": "+59", "flag": 1, "package_type": "month", "start_time": "", "subscribe": 0}), # bug1 起止时间错误
    # # 平级: package channel
    
    # (11487165, [('v_general_month', 'WX'), ('v_general_quarter', 'WX')], {"end_time": "+119", "flag": 1, "package_type": "month", "start_time": "", "subscribe": 0}), #  month ? 没意义
    # (11488169, [('v_general_month', 'WX'), ('v_general_quarter', 'ZFB')], {"end_time": "+119", "flag": 1, "package_type": "quarter", "start_time": "", "subscribe": 0}),
    # (11488165, [('v_super_month', 'ZFB'), ('v_super_year', 'WX')], {"end_time": "+394", "flag": 3, "package_type": "year", "start_time": "", "subscribe": 0}),
    # (5, [('v_super_year', 'ZFB'), ('v_super_month', 'ZFB'), ], {"end_time": "+394", "flag": 3, "package_type": "year", "start_time": "", "subscribe": 0}), # month ?
    # # 升级: package channel
    # (11488193, [('v_general_month', 'WX'), ('v_super_year', 'WX')], {"end_time": "+364", "flag": 3, "package_type": "year", "start_time": "", "subscribe": 0}),
    # (11488191, [('v_general_quarter', 'ZFB'), ('v_super_month', 'WX')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 0}),
    # # 降级: package channel
    # (11488162, [('v_super_month', 'WX'), ('v_general_year', 'ZFB')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 0}),
    # (11488161, [('v_super_year', 'WX'), ('v_general_month', 'WX')], {"end_time": "+364", "flag": 3, "package_type": "year", "start_time": "", "subscribe": 0}),

    # # 订阅 + 非订阅
    # # 微信订阅+微信单月 通知用户中心时长是合并的，续订后延
    # (10, [('v_general_year_subscribe', 'WX_QR'), ('v_general_month', 'WX')], {"end_time": "+394", "flag": 1, "package_type": "year", "start_time": "", "subscribe": 1, "next_renew_time": "+393"}),
    #  微信订阅+支付宝单月 通知用户中心时长是合并的，续订时间没变
    # (11487164, [('v_general_year_subscribe', 'WX_QR'), ('v_general_month', 'ZFB')], {"end_time": "+394", "flag": 1, "package_type": "year", "start_time": "", "subscribe": 1, "next_renew_time": "+363"}),
    # (11488152, [('v_general_year_subscribe', 'WX_QR'), ('v_super_month', 'WX')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 0, "next_renew_time": None}),
    # (11488151, [('v_general_year_subscribe', 'WX_QR'), ('v_super_month', 'ZFB')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 0, "next_renew_time": None}),
    
    # (11488136, [('v_super_month_subscribe', 'WX_QR'), ('v_general_quarter', 'WX')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    # (15, [('v_super_month_subscribe', 'WX_QR'), ('v_general_year', 'ZFB')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    # (11488132, [('v_super_month_subscribe', 'WX_QR'), ('v_super_year', 'WX')], {"end_time": "+394", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+393"}),
    
    # (11487200, [('v_super_month_subscribe', 'WX_QR'), ('v_super_year', 'ZFB')], {"end_time": "+394", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),

    # # 非订阅 + 订阅
    # (11488129, [('v_general_month', 'WX'), ('v_general_year_subscribe', 'WX_QR'), ], {"end_time": "+394", "flag": 1, "package_type": "year", "start_time": "", "subscribe": 1, "next_renew_time": "+393"}),
    
    # (11487199, [('v_general_month', 'ZFB'), ('v_general_year_subscribe', 'WX_QR'), ], {"end_time": "+394", "flag": 1, "package_type": "year", "start_time": "", "subscribe": 1, "next_renew_time": "+363"}),
    # (20, [('v_super_month', 'WX'), ('v_general_year_subscribe', 'WX_QR')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 0, "next_renew_time": None}),
    # (11488146, [('v_super_month', 'ZFB'), ('v_general_year_subscribe', 'WX_QR')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 0, "next_renew_time": None}),
    
    # (11487198, [('v_super_year', 'ZFB'), ('v_super_month_subscribe', 'WX_QR')], {"end_time": "+394", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    # (11488126, [('v_super_year', 'WX'), ('v_super_month_subscribe', 'WX_QR')], {"end_time": "+394", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+393"}),
    # (11488143, [('v_general_quarter', 'ZFB'), ('v_super_month_subscribe', 'WX_QR')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    # (25, [('v_general_year', 'WX'), ('v_super_month_subscribe', 'WX_QR')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    # (11487163, [('v_general_month', 'WX'), ('v_general_month', 'ZFB'), ('v_general_year_subscribe', 'WX_QR')], {"end_time": "+424", "flag": 1, "package_type": "year", "start_time": "", "subscribe": 1, "next_renew_time": "+393"}),
    
    # # 订阅+订阅 缺少vip的不同package混合购买
    # (11488141, [('v_general_year_subscribe', 'WX_QR'), ('v_general_year_subscribe', 'WX_QR')], {"end_time": "+729", "flag": 1, "package_type": "year", "start_time": "", "subscribe": 1, "next_renew_time": "+728"}),
    # (11488139, [('v_super_month_subscribe', 'WX_QR'), ('v_super_month_subscribe', 'WX_QR')], {"end_time": "+59", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+58"}),
    # (11488138, [('v_general_year_subscribe', 'WX_QR'), ('v_super_month_subscribe', 'WX_QR')], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    # (11488137, [('v_super_month_subscribe', 'WX_QR'), ('v_general_year_subscribe', 'WX_QR'), ], {"end_time": "+29", "flag": 3, "package_type": "month", "start_time": "", "subscribe": 1, "next_renew_time": "+28"}),
    


])
def test_combined_vip(userId, skus, expectation):
    '''测试不到开始日期早于今天 或者 过期会员的情况; 无法测试新模版/iap
    #todo: 把开始日期/结束日期提前(使用中会员/过期会员); 

    case组合维度:
    - 是否订阅
    - vip/svip
    - 支付渠道: wx/zfb/jd 
    - package

    '''
    # userId = u.get()
    # print(userId)
    # return
    for sku in skus:
        test_purchase_vip(userId, sku[0], sku[1] if len(sku) > 1 else 'WX')

    # userutils.vip_status(userId)
    time.sleep(3)
    result = userutils.vip_status(userId)
    assert_equal(result, expectation)


def test_cancel_subscription():
    '''iap订阅用户调用取消订阅接口'''
    vip.cancel_subscribe(params={"user_id": 11488208})

# @pytest.mark.parametrize('userId, tradeNo', [
#     (11487267, '20220321145841073180')
# ])
# def test_xxx(userId, tradeNo):
#     location = MallV2.trade_token(userId=userId, tradeNo=tradeNo).json()['data']['location']
#     token = location.split('/')[-1]
#     MallV2.trade_detail(userId=userId, tradeNo=tradeNo, token=token).json()['data']


# def test_yyy():
#     '''
#     学院币支付
#     '''
#     s = r'{"data":"{\"channel\":\"EDU_COIN\",\"user_agent\":\"Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 NewStudios/1.9.7 (com.xinpianchang.newstudios; build:1037; iOS 15.1.0)\",\"return_url\":\"https://pay-test.xinpianchang.com/pay/2022031816282900385\"}","s":"/order/2022031816282900385/pay"}'

#     data = json.loads(s)
#     print(data)
#     requests.post('https://mall-test.xinpianchang.com/order/2022031816282900385/pay', data=data)


def test_register():
    '''注册测试账号'''
    for i in range(5):
        code, phone = userutils.get_available_phone()
        s = Sess()
        s.send_captcha(json={'regionCode': code, 'phone': phone, 'type': 5})

        userutils.skip_tencent_captcha(s.headers['authorization'])
        r = s.register(json={'nickname': f'puppet{phone[-4:]}', 'regionCode': code,
                       'phone': phone, 'smsCaptcha': '000000', 'quickMode': False})


def assert_equal(r, e):
    # r = userutils.vip_status(11488200)
    # e = {
    #         "end_time": "2025-04-21",
    #         # "end_time": "+1110",
    #         "flag": 1,
    #         "package_type": "year",
    #         "start_time": "",
    #         "subscribe": 0
    # }
    for k, v in e.items():
        if k.endswith('time'):
            if v is None:
                assert r[k] is None, k
            else:
                if v == "":
                    v = dt.date.today().strftime('%Y-%m-%d')
                elif v.startswith('+'):
                    v = (dt.date.today() +
                         dt.timedelta(days=int(v[1:]))).strftime('%Y-%m-%d')
                elif v.startswith('-'):
                    v = (dt.date.today() -
                         dt.timedelta(days=int(v[1:]))).strftime('%Y-%m-%d')

                assert r[k][:10] == v, k
        else:
            assert r[k] == v, k


class UserIds():
    ids = [x for x in range(11487197, 11487137, -1)]
    def __init__(self):
        self.i = -1

    def get(self):
        self.i = self.i + 1
        return UserIds.ids[self.i]

u = UserIds()


@pytest.mark.parametrize('userId, skuId, pay_channel_prefix', [
    
    
    (11487222, 'v_general_month', 'ZFB'),
    # (11487223, 'v_general_quarter', 'ZFB'),
    # (11487223, 'v_general_year', 'WX'),

    # (11488229, 'v_super_month', 'WX'),
    # (11488131, 'v_super_year', 'ZFB'),
    
    # (11487222, 'v_general_month_subscribe', 'WX')
    # (11487223, 'v_general_quarter_subscribe', 'WX'),
    # (11487222, 'v_general_year_subscribe', 'WX'),

    # (11488131, 'v_super_month_subscribe', 'WX_QR'),
])
def test_purchase_vip_with_coupon(userId, skuId, pay_channel_prefix):
    '''
    '''
    t = 1 # 0: spu, 1: sku, 2: promotionTag
    spu = 'sns_vip' # 'sns_vip' 'sns_svip'
    b = skuId if t==1 else spu 

    c = MallV2.create_coupon(**{
                "thresholdPrice": 1,
                "couponValue": 1,                
                "rangeType": t,
                "rangeValue": b,                
                "rangeStoreCode": 'vip_center',
                "returnable": True,
                "name": f"ç会员优惠券title",
                "brief": f"ç{'sku' if t==1 else 'spu'}:{b}",
            }).json()['data']
    MallV2.coupon_shelf(code=c['code'], action='on')
    MallV2.receive_coupon(userId=userId, code=c['code'])
    sku1 = {"skuId": skuId, "quantity": 1, "storeCode": STORE_VIP}
    ka = {"userId": userId, "skus": [sku1]}
    totalPriceViewed = MallV2.trade_confirmation(
        **ka).json()['data']['result']['totalPrice']
    trades = MallV2.trade_submit(
        ** ka | {"totalPriceViewed": totalPriceViewed}).json()['data']['trade']

    assert len(trades) == 1
    tradeNo = trades[0]
    location = MallV2.trade_token(userId=userId, tradeNo=tradeNo).json()[
        'data']['location']
    token = location.split('/')[-1]
    data = MallV2.trade_detail(
        userId=userId, tradeNo=tradeNo, token=token).json()['data']

    # channel = data['channelList'][random.randint(0, len(data['channelList'])-1)]
    channel = get_available_channel(
        data['channelList'], location, pay_channel_prefix)
    price = data['price']

    order = MallV2.pay(**channel).json()['data']['order']
    PayAdmin().fix(order)

def test_user_vip_notify():
    InternalApi.vip_notify(user_id=10265312, end_time="20220101")


def test_generate_giftcard():

    temp = r'''{{
        "name": "618普通会员{0}卡 ",
        "meta": [
            {{
                "expiredAt": 1755189520000,
                "cardType": "{0}",
                "num": 1000,
                "effectiveAt": 1655189520000,
                "cardCategory": 80 
            }}
        ],
        "remark": "618"
    }}'''
    gift_cards = dict(
        GriftCardTypeVipMonth    = "vip_month",
        GriftCardTypeVipWeek     = "vip_week",
        GriftCardTypeVipQuarter  = "vip_quarter",
        GriftCardTypeVipYear     = "vip_year",
        GriftCardTypeVip14Mouth  = "vip_14month",
        GriftCardTypeSvipWeek    = "svip_week",
        GriftCardTypeSvipMonth   = "svip_month",
        GriftCardTypeSvipQuarter = "svip_quarter",
        GriftCardTypeSvipYear    = "svip_year",
    )
    for gift in gift_cards.values():
        vip.generate_giftcard(json=json.loads(temp.format(gift)))

def test_exchange_giftcard():
    '''兑换
    '''
    user_id = 10265312
    card_no = '1280344604486412'
    userutils.vip_status(user_id)
    vip.exchange_giftcard(json={'user_id': user_id, 'card_category': 80, 'card_no': card_no})
    userutils.vip_status(user_id)

def test_giftcard_validity():
    '''有效期'''