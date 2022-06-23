from api import testapi
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

