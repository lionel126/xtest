from hashlib import md5
from datetime import datetime, timedelta, date
import pytest
import xml.etree.ElementTree as et
import dicttoxml
from api import vip, MallV2, PayAdmin, PayServer
from config import STORE_VIP
from utils.utils import get_available_channel

def d(date_str, format='%Y-%m-%d'):
    return datetime.strptime(date_str, format)

def test_wx_subscribe_contract():
    '''微信订阅会员签约成功回调
    todo: 
    :param contract_code:
    :plan_id??:
    '''
    key = 'vmovierVmovierVideoaisdjasuoaKQX'
    
    # s = 'appid=wxf3b92e7575e54565&body=新片场 | 20221019180704037294&contract_id=202210191687079060&detail=连续包月&mch_id=1482023042&nonce_str=p72Qh8RAA7y8Cf3NCElN&notify_url=http://pay-server.vmovier.cc/api/order/wx/notify&out_trade_no=20221019180722008134&spbill_create_ip=103.219.187.42&total_fee=1&trade_type=PAP&key=vmovierVmovierVideoaisdjasuoaKQX'
    # d = {}
    # for kv in s.split('&'):
    #     k, v = kv.split('=')
    #     d[k] = v
    # print(d['out_trade_no'])
    # print(d)
    # s2 = str(dicttoxml.dicttoxml(d, root=True, custom_root='xml', attr_type=False), encoding='utf-8')
    # print(s2)
    s = '<xml><change_type>ADD</change_type><contract_code>C20221019180722N08133</contract_code><contract_expired_time>2032-10-16 18:07:37</contract_expired_time><contract_id>222202222222222222</contract_id><mch_id>1482023042</mch_id><openid>oyligwNXCVQvFfTtrwo0JERNsCw8</openid><operate_time>2222-02-22 22:22:22</operate_time><plan_id>159686</plan_id><request_serial>1666174042108</request_serial><result_code>SUCCESS</result_code><return_code>SUCCESS</return_code><return_msg>OK</return_msg><sign>0DDD63C7BAAD503153429479A8B67DA6</sign></xml>'
    xml = et.fromstring(s)
    print('sign', xml.find('sign').text)
    xml.find('contract_code').text = 'C20221020144817N08163'
    # xml.remove('sign')
    d = {elem.tag: elem.text for elem in xml}
    print(d)
    d = dict(sorted(d.items(), key=lambda kv: kv[0]))
    print(d)
    del d['sign']
    dict_str = '&'.join([f'{k}={v}' for k, v in d.items()]) + f'&key={key}'
    sign = md5(bytes(dict_str, encoding='utf-8')).hexdigest()
    print(f'{sign=}')
    xml.find('sign').text = sign
    print(et.tostring(xml))
    PayServer.wx_contract_notify(data=et.tostring(xml))

def test_fix_trade():
    PayAdmin().fix(20221020144818008164)

def test_sync_vip_status():
    vip.trigger_status(json={"userId": 10265312, "group": "sns"})

def test_date():
    print(d('2023-11-14') - d('2022-08-19'))
    print(d('2023-10-15') - d('2022-08-19'))

    print(d('2023-12-30') - d('2023-11-15'))
    print(d('2023-11-30') - d('2023-10-16'))

@pytest.mark.parametrize('userId, skuId, pay_channel_prefix', [
    # (10265312, 'resource_month', 'WX'),
    # (10265312, 'resource_month', 'ZFB'),
    # (10265312, 'resource_quarter', 'ZFB'),
    # (10265312, 'resource_quarter', 'WX'),
    # (10265312, 'resource_year', 'ZFB'),
    # (10265312, 'resource_year', 'WX'),
    

    # (10265312, 'v_general_month', 'ZFB'),
    # (10265312, 'v_general_month', 'WX'),
    (10265312, 'v_general_month_subscribe', 'WX')
])
def test_buy_resource_vip(userId, skuId, pay_channel_prefix):
    '''todo: 订阅会员购买
    1 update db 相同模版已签约数据 enable=0
    2 获取contract_code 回调签约成功
    3 修改订单状态为已创建status=0 以补单
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

