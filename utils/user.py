from api import testapi
from config import REDIS_KEY_REGISTER_PREFIX
import time

def get_available_user():
    return testapi.user(params={'nickname': 'puppeteernickname', 'status':0}).json()['data']
    # return request('GET', f'{DJANGO_BASE_URL}/garlic/user', params={'nickname': 'puppeteernickname', 'status':0}).json()['data']

def get_available_phone():
    for i in range(10):
        # f'19{str(int(time.time()))[1:]}'
        phone = f'{str(int(time.time()))}'
        code = '+54' # Argentina
        res = testapi.user(params={'input_phone': phone, 'mobile_international_code': code})
        if res.json()['code'] != 'SUCCESS':
            return code, phone
        time.sleep(1)
    raise Exception('no available phone num after end of loop')

def skip_tencent_captcha(auth):
    '''
    如果redis存在key: {PREFIX}:REGISTER_TICKET_{AUTH} 就跳过防水墙
    '''
    testapi.set_redis(f'{REDIS_KEY_REGISTER_PREFIX}{auth}')