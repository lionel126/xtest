import requests
from config import PAY_ADMIN_BASE_URL
from utils.utils import replace, append


session_pay_admin = requests.Session()
class PayAdmin():
    
    def __init__(self):
        if self._get_user().status_code == 403:
            self._login()

    def _get_user(self):
        return session_pay_admin.get(f'{PAY_ADMIN_BASE_URL}/api/current/user')

    def _login(self):
        session_pay_admin.post(f'{PAY_ADMIN_BASE_URL}/login', {"email": "chenshengguo@xinpianchang.com", "password": "123456"})
    
    def fix(self, order_no):
        '''补单
        '''
        return session_pay_admin.get(f'{PAY_ADMIN_BASE_URL}/api/trade/fix?order_no={order_no}')

    def refund(self, order_no, amount_refund):
        '''退款
        '''
        return session_pay_admin.get(f'{PAY_ADMIN_BASE_URL}/api/trade/refund?order_no={order_no}&amount_refund={amount_refund}')
    
    def current_trades(self, params=None, **kwargs):
        '''实时订单
        '''
        if params is None: 
            params = {
                "page": 1,
                "page_size": 10
            }
        replace(kwargs, params)
        append(kwargs, params, ["order_no","out_trade_no","channel","status","trans_type","phone","user_id","platform_no","tags","start","end",])
        return session_pay_admin.get(f'{PAY_ADMIN_BASE_URL}/api/trade', params=params)

    def historical_trades(self, params=None, **kwargs):
        '''历史订单
        '''
        if params is None: 
            params = {
                "page": 1,
                "page_size": 10
            }
        replace(kwargs, params)
        append(kwargs, params, ["order_no","out_trade_no","channel","status","trans_type","phone","user_id","platform_no","tags","start","end",])
        return session_pay_admin.get(f'{PAY_ADMIN_BASE_URL}/api/trade/history', params=params)