from api import testapi
from api.user_center import Sess
from config import LOCAL_IP
import time


def get_available_user(**kw):
    return testapi.user(params={'nickname': 'puppeteernickname', 'status': 0, **kw}).json()['data']
    # return request('GET', f'{DJANGO_BASE_URL}/garlic/user', params={'nickname': 'puppeteernickname', 'status':0}).json()['data']

def get_user(**kw):
    return testapi.user(params=kw).json()['data']

def get_available_users(n):
    return testapi.users(params={'nickname': 'puppeteernickname', 'status': 0, '_count': n}).json()['data']

def get_available_id():
    return


def get_available_phone():
    for i in range(10):
        # f'19{str(int(time.time()))[1:]}'
        phone = f'{str(int(time.time()))}'
        code = '+54'  # Argentina
        res = testapi.user(
            params={'input_phone': phone, 'mobile_international_code': code})
        if res.json()['code'] != 'SUCCESS':
            return code, phone
        time.sleep(1)
    raise Exception('no available phone num after end of loop')


def skip_tencent_captcha(auth):
    '''
    如果redis存在key: {PREFIX}:REGISTER_TICKET_{AUTH} 就跳过防水墙
    '''
    testapi.set_redis({'key': f'REGISTER_TICKET_{auth}', 'db': 'usercenter'})

def clear_sms_interval(code, phone):
    testapi.del_redis(
        {'db': 'common-service','key': f'user_ip_{LOCAL_IP}'}, 
        {'db': 'common-service','key': f'UC001_{code}{phone}_gap'}
    )

def vip_status(user_id):
    r = testapi.vip_status(user_id).json()
    if r['code'] == 'SUCCESS':
        return r['data']
    return {}


def register(code=None, phone=None):
    '''
    return {
        'data':{
            'user': {
                'regionCode': '',
                'phone': ''
            }
        }
    }
    '''
    if code is None or phone is None:
        code, phone = get_available_phone()
    s = Sess()
    s.send_captcha(json={'regionCode': code, 'phone': phone, 'type': 5})

    skip_tencent_captcha(s.headers['authorization'])
    r = s.register(json={'nickname': f'puppet{phone[-4:]}', 'regionCode': code, 'phone': phone, 'smsCaptcha': '000000', 'quickMode': False})
    # assert r.status_code == 201
    # j = r.json()
    # assert j['code'] == 'SUCCESS'
    # return j['data']['user']
    return r

def login(code=None, phone=None):
    '''

    return user, session
    '''
    if not (phone and code):
        u = register().json()['data']['user']
        code, phone= u['regionCode'], u['phone']
    j = {
        "type": "phone",
        "regionCode": code,
        "phone": phone,
        "password": "999999"
    }
    s = Sess()
    r = s.login(json=j)
    assert r.status_code == 200
    return r.json()['data']['user'], s