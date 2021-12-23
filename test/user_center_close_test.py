'''
mq延迟消息 修改

'''
from api.user_center import Sess, Boss
from utils import user as userutils
from utils.utils import areq
import pytest


@pytest.fixture
def login():
    '''

    return user, session
    '''
    u = userutils.get_available_user()
    j = {
        "type": "phone",
        "regionCode": u['mobile_international_code'],
        "phone": u['input_phone'],
        "password": "999999"
    }
    s = Sess()
    r = s.login(json=j)
    assert r.status_code == 200
    return u, s

class TestUserCenter():
    ''' 与注销业务 非密切相关'''
    @pytest.mark.parametrize('code, phone', [
        ('+54', '1640243167')
    ])
    def test_login_by_password(self, code, phone):
        '''
        '''
        j = {
            "type": "phone",
            "regionCode": code,
            "phone": phone,
            "password": "999999"
        }
        s = Sess()
        r = s.login(json=j)
        assert r.status_code == 200
    def test_register(self):
        '''register '''

        code, phone = userutils.get_available_phone()
        s = Sess()
        s.send_captcha(json={'regionCode': code, 'phone': phone, 'type': 5})

        userutils.skip_tencent_captcha(s.HEADERS['authorization'])
        r = s.register(json={'nickname': 'puppeteernickname', 'regionCode': code, 'phone': phone, 'smsCaptcha': '000000'})
        assert r.status_code == 201
        j = r.json()
        assert j['code'] == 'SUCCESS'

class TestCloseUser():

    # def setup_method(self):
    #     self.u = user.get_available_user()
    #     self.login_data = {
    #         "type": "phone",
    #         "regionCode": self.u['mobile_international_code'],
    #         # "smsCaptcha": "000000",
    #         "phone": self.u['input_phone'],
    #         "password": "999999",
    #     }
    #     r = uc.login(json=self.login_data)
    #     assert r.status_code == 200

    def test_boss_api_without_token(self):
        res = Boss.user_review_list(headers={}, params={'searchStyle': 1})
        # assert res.status_code == 403
        j = res.json()
        assert j['success'] is False
        assert j['code'] == 'BOSS_USER_HEADER_EMPTY_CODE'

    def test_apply_without_auth(self):

        res = Sess().apply_user_close()
        # assert res.status_code == 403
        j = res.json()
        assert j['code'] == 'ID_NOT_IS_BLANK'
        assert j['success'] is False

    def test_boss_application_detail(self, login):
        '''用户申请注销，boss列表能看到对应数据
        '''
        u, s = login
        reason = ''
        r = s.apply_user_close(json={'applyReason': reason})
        assert r.status_code == 200
        review_list = Boss.user_review_list(
            params={'searchStyle': 1, 'userId': u['id']}).json()['data']['list']

        user_review = [r for r in review_list][0]
        assert user_review['actual_logout_time'] is None
        assert user_review['applicant'] == str(u['id'])
        assert user_review['apply_reason'] == reason

    def test_kick_off_after_application(self, login):
        '''用户申请注销，掉线
        '''
        u, s = login
        reason = ''
        r = s.apply_user_close(json={'applyReason': reason})
        assert r.status_code == 200
        r = s.user_info(params={'query': 1})
        assert r.status_code == 401
        assert r.json()['code'] == 'UNAUTHORIZED'

    def test_close_again(self, login):
        '''重复申请注销
        '''
        u, s = login
        r = Boss.apply_user_close()
        assert r.status_code == 200
        r = Boss.apply_user_close()
        assert r.status_code == 403
        j = r.json()
        assert j["code"] == "USER_LOGOUTING_CODE"
        assert j["success"] is False

    def test_login_after_application(self, login):
        '''申请注销后，无法登录
        '''
        u, s = login
        r = s.apply_user_close()
        assert r.status_code == 200
        j = {
            "type": "phone",
            "regionCode": u['mobile_international_code'],
            "phone": u['input_phone'],
            "password": "999999"
        }
        r = s.login(json=j)
        assert r.status_code == 403
        j = r.json()
        assert j['code'] == 'USER_STATUS_DISABLE'
        assert j['success'] == False


    def test_accept_to_close_user(self, login):
        '''同意注销申请
        '''
        u, s = login
        s.apply_user_close()
        r = Boss.user_review_list(
            params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']
        r = Boss.close_user(f'{apply_no}1', json={
                        'operateType': 0, 'applyNo': apply_no})
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True
        
        # r = s.login(json={
        #     "type": "phone",
        #     "regionCode": u['mobile_international_code'],
        #     "phone": u['input_phone'],
        #     "password": "999999"
        # })
        # assert r.status_code == 200
        # j = r.json()
        # assert j['code'] == 'USER_STATUS_DISABLE'
        # assert j['success'] == False

    @pytest.mark.asyncio
    async def test_con_apply(self, login):
        '''并发申请注销 
        todo 500
        '''
        u, s = login
        kwargs = {
            'url': Sess.URL_CLOSE_USER,
            'headers': s.HEADERS,
            'method': 'POST',
            'json': {}
        }
        res = await areq([kwargs]*10)
        for r in res:
            assert r.status == 200
        Boss.user_review_list(params={'searchStyle': 1, 'userId': u['id']})
    