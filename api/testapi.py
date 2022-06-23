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

def users(method='GET', params=None):
    '''
    :param _count: number of users
    '''
    return request('GET', f'{DJANGO_BASE_URL}/garlic/users', params=params)

def get_redis(db, key):
    '''
    
    '''
    return request('GET', f'{DJANGO_BASE_URL}/garlic/redis/get', params = {'key': key, 'db': db})

def del_redis(*a):
    '''
    :param a: e.g. {
        "db": "usercenter",
        "key": "user_info_10265312"
    }
    '''
    return request('POST', f'{DJANGO_BASE_URL}/garlic/redis/del', json=a)

def set_redis(*a):
    '''
    :param a: e.g. {
        "db": "usercenter",
        "key": "user_info_10265312"
    }
    '''
    return request('POST', f'{DJANGO_BASE_URL}/garlic/redis/set', json=a)
def del_redis(*a):
    '''
    :param a: e.g. {
        "db": "usercenter",
        "key": "user_info_10265312"
    }
    '''
    return request('POST', f'{DJANGO_BASE_URL}/garlic/redis/del', json=a)

def users_with_realname():
    return request('GET', f'{DJANGO_BASE_URL}/garlic/users/realname/status?u.status=0&r.status=3')
def users_without_realname():
    return request('GET', f'{DJANGO_BASE_URL}/garlic/users/realname/status?u.status=0&r.status=0')

def vip_status(user_id):
    return request("GET", f'{DJANGO_BASE_URL}/garlic/user/{user_id}/vip_status')

def team_applications(**params):
    return request("GET", f'{DJANGO_BASE_URL}/sns/team/applications', params=params)

def get_article_rewards(**params):
    '''
    :params: 查询条件
    '''
    return request("GET", f'{DJANGO_BASE_URL}/sns/article/rewards', params=params)

def update_article_rewards(**kwargs):
    '''
    :params: 查询条件
    :json: 更新数据
    '''
    return request("PATCH", f'{DJANGO_BASE_URL}/sns/article/rewards', **kwargs)