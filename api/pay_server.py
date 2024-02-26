from requests import request
from config import PAY_SERVER_BASE_URL

def wx_contract_notify(method='POST', url=f'{PAY_SERVER_BASE_URL}/api/wx/notify/contract', data=None):
    headers = {'content-type': 'application/xml;charset=utf-8'}
    # 签约？
    # xml = '<xml><change_type>ADD</change_type><contract_code>C20221019180722N08133</contract_code><contract_expired_time>2032-10-16 18:07:37</contract_expired_time><contract_id>202210191687079060</contract_id><mch_id>1482023042</mch_id><openid>oyligwNXCVQvFfTtrwo0JERNsCw8</openid><operate_time>2022-10-19 18:07:39</operate_time><plan_id>159686</plan_id><request_serial>1666174042108</request_serial><result_code>SUCCESS</result_code><return_code>SUCCESS</return_code><return_msg>OK</return_msg><sign>0DDD63C7BAAD503153429479A8B67DA6</sign></xml>'
    
    return request(method, url, data=data, headers=headers)

def order_wx_notify():
    # 支付成功？
    xml = '<xml><nonce_str>p72Qh8RAA7y8Cf3NCElN</nonce_str><out_trade_no>20221019180722008134</out_trade_no><contract_id>202210191687079060</contract_id><appid>wxf3b92e7575e54565</appid><total_fee>1</total_fee><sign>fdfa4cf2d596f18502f9ec29cb247e64</sign><trade_type>PAP</trade_type><detail>连续包月</detail><mch_id>1482023042</mch_id><body>新片场 | 20221019180704037294</body><notify_url>http://pay-server.vmovier.cc/api/order/wx/notify</notify_url><spbill_create_ip>103.219.187.42</spbill_create_ip></xml>'