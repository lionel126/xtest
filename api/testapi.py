from config import DJANGO_BASE_URL
from requests import request

def user(method='GET', params=None):
    '''
    :params params: {
        avatar_big: "https://cs.xinpianchang.com/passport/default.png"
        avatar_middle: "https://cs.xinpianchang.com/passport/default.png"
        avatar_small: "https://cs.xinpianchang.com/passport/default.png"
        badge: 0
        badge_from: "common"
        birthday: null
        created_date: "2020-09-17T15:22:41Z"
        email_validate: null
        id: 11485425
        id_validate: null
        if_set_password: true
        input_email: null
        input_phone: "19600327322"
        mobile_international_code: "+86"
        mobile_validate: 1
        nationality: null
        nickname: "puppeteernickname"
        salt: "vePQ9"
        status: 2
        updated_date: "2021-12-17T14:15:42Z"
        user_email: null
        user_group: "UC001"
        user_id_number: null
        user_id_type: null
        user_name: "_user_11485425"
        user_password: "d665a7803ac7bc5bc12af72f6640a68e"
        user_phone: "+86-19600327322"
        user_real_name: null
        user_sex: 0
    }
    '''
    return request('GET', f'{DJANGO_BASE_URL}/garlic/user', params=params)


def set_redis(k, v=None):
    data = {
        'db': 'usercenter',
        'key': k,
        'value': v
    }
    return request('POST', f'{DJANGO_BASE_URL}/garlic/redis/set', data=data)