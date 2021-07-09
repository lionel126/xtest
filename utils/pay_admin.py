import requests

PAY_ADMIN_BASE = 'https://pay-admin-wkm.vmovier.cc'

session_pay_admin = requests.Session()
class PayAdmin():
    

    def __init__(self):
        if self._get_user().status_code == 403:
            self._login()


    def _get_user(self):
        return session_pay_admin.get(f'{PAY_ADMIN_BASE}/api/current/user')
    def _login(self):
        session_pay_admin.post(f'{PAY_ADMIN_BASE}/login', {"email": "chenshengguo@xinpianchang.com", "password": "123456"})

    
    def fix(self, order_no):
        '''补单
        '''
        session_pay_admin.get(f'{PAY_ADMIN_BASE}/api/trade/fix?order_no={order_no}')

    def refund(self, order_no):
        '''退款
        '''
        session_pay_admin.get(f'{PAY_ADMIN_BASE}/api/trade/refund?order_no={order_no}&amount_refund=1')