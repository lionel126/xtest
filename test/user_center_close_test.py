'''
mq延迟消息 修改

'''
from api.user_center import Sess, Boss
from utils import user as userutils
from utils.utils import areq, generate_id
import pytest
import time
import json
import config

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
        code, phone = userutils.get_available_phone()
    s = Sess()
    s.send_captcha(json={'regionCode': code, 'phone': phone, 'type': 5})

    userutils.skip_tencent_captcha(s.HEADERS['authorization'])
    r = s.register(json={'nickname': 'puppeteernickname', 'regionCode': code, 'phone': phone, 'smsCaptcha': '000000', 'quickMode': False})
    # assert r.status_code == 201
    # j = r.json()
    # assert j['code'] == 'SUCCESS'
    # return j['data']['user']
    return r

# @pytest.fixture
def login():
    '''

    return user, session
    '''
    # u = userutils.get_available_user()
    # j = {
    #     "type": "phone",
    #     "regionCode": u['mobile_international_code'],
    #     "phone": u['input_phone'],
    #     "password": "999999"
    # }
    u = register().json()['data']['user']
    # j = {
    #     "type": "phone",
    #     "regionCode": u['regionCode'],
    #     "phone": u['phone'],
    #     "password": "999999"
    # }
    # s = Sess()
    # r = s.login(json=j)
    # assert r.status_code == 200
    # return u, s
    return login_by_password(u['regionCode'], u['phone'])

def login_by_password(code, phone):
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
    return r.json()['data']['user'], s

# @pytest.fixture
def login_n(n):
    # def _login(n):
        result = []
        us = userutils.get_available_users(n)
        for u in us:
            j = {
                "type": "phone",
                "regionCode": u['mobile_international_code'],
                "phone": u['input_phone'],
                "password": "999999"
            }
            s = Sess()
            r = s.login(json=j)
            assert r.status_code == 200
            result.append((u, s))
        return result
    # return _login

def f(apply_no, operate, code, success):
    '''operate	string	是	操作类型: 0-同意 1-拒绝 2-取消
    '''
    r = Boss.close_user(f'{apply_no}123', json={
                'operateType': operate, 'applyNo': apply_no})
    assert r.status_code == 200
    j = r.json()
    assert j['code'] == code
    assert j['success'] is success

class TestTest():
    ''' 半自动用例 辅助测试'''
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
        # code, phone = '+54', '1640346586'
        s = Sess()
        s.send_captcha(json={'regionCode': code, 'phone': phone, 'type': 5})

        userutils.skip_tencent_captcha(s.HEADERS['authorization'])
        r = s.register(json={'nickname': 'puppeteernickname', 'regionCode': code, 'phone': phone, 'smsCaptcha': '000000', 'quickMode': False})
        assert r.status_code == 201
        j = r.json()
        assert j['code'] == 'SUCCESS'
    
    def test_without_auth(self):
        '''
        '''
        s = Sess()
        s.apply_for_realname()
    @pytest.mark.parametrize('code, phone',[
        ('+54', '1640766221')
    ])
    def test_close_one_user(self, code, phone):
        '''注销用户
        
        '''
        u, s = login_by_password(code, phone)
        # s.apply_for_realname()
        # r = Boss.realname_list(params={'userId': u['id'], 'status':'INREVIEW'})
        # Boss.verify_realname(r.json()['data']['list'][0]['id'])
        
        s.apply_user_close()
        
        # r = Boss.user_close_review_list(
        #     params={'userId': str(u['id']), 'searchStyle': 1})
        # apply_no = r.json()['data']['list'][0]['apply_no']
        # r = Boss.close_user(f'{apply_no}1', json={
        #                 'operateType': 0, 'applyNo': apply_no})
        # j = r.json()
        # assert j['code'] == 'SUCCESS'
        # assert j['success'] is True
        # print('审核通过，冷静期开始')
        # time.sleep(config.USER_CLOSE_DELAY)
        # print('冷静期结束')

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
        '''boss auth test, 没有signature校验？
        todo: 多个接口
        '''
        res = Boss.user_close_review_list(headers={}, params={'searchStyle': 1})
        # assert res.status_code == 403
        j = res.json()
        assert j['success'] is False
        assert j['code'] == 'BOSS_USER_HEADER_EMPTY_CODE'

    def test_apply_without_auth(self):
        '''api auth test
        '''
        res = Sess().apply_user_close()
        # assert res.status_code == 403
        j = res.json()
        assert j['code'] == 'ID_NOT_IS_BLANK'
        assert j['success'] is False

    def test_boss_application_detail(self):
        '''用户申请注销，boss列表能看到对应数据
        '''
        u, s = login()
        r = s.apply_user_close()
        assert r.status_code == 200
        review_list = Boss.user_close_review_list(
            params={'searchStyle': 1, 'userId': u['id']}).json()['data']['list']

        user_review = [r for r in review_list][0]
        assert user_review['actual_logout_time'] is None
        assert user_review['applicant'] == str(u['id'])
        # assert user_review['apply_reason'] == reason

    def test_boss_application_detail(self):
        '''todo 用户申请注销，原因太长
        原因必填？
        '''
        u, s = login()
        r = s.apply_user_close()
        assert r.status_code == 200
        review_list = Boss.user_close_review_list(
            params={'searchStyle': 1, 'userId': u['id']}).json()['data']['list']

        user_review = [r for r in review_list][0]
        assert user_review['actual_logout_time'] is None
        assert user_review['applicant'] == str(u['id'])
        # assert user_review['apply_reason'] == reason

    def test_kick_off_after_application(self):
        '''用户申请注销，掉线
        '''
        u, s = login()
        reason = ''
        r = s.apply_user_close(json={'applyReason': reason})
        assert r.status_code == 200
        r = s.user_info(params={'query': 1})
        assert r.status_code == 401
        assert r.json()['code'] == 'UNAUTHORIZED'

    def test_close_again(self):
        '''重复申请注销
        '''
        u, s = login()
        r = s.apply_user_close()
        assert r.status_code == 200
        r = s.apply_user_close()
        assert r.status_code == 403
        j = r.json()
        assert j["code"] == "USER_LOGOUTING_CODE"
        assert j["success"] is False

    def test_cant_login_after_close_application(self):
        '''申请注销后，无法登录
        '''
        u, s = login()
        r = s.apply_user_close()
        assert r.status_code == 200
        j = {
            "type": "phone",
            "regionCode": u['regionCode'],
            "phone": u['phone'],
            "password": "999999"
        }
        r = s.login(json=j)
        assert r.status_code == 403
        j = r.json()
        assert j['code'] == 'USER_STATUS_DISABLE'
        assert j['success'] == False


    def test_accept_user_close(self):
        '''同意注销申请 账号无法登录
        '''
        u, s = login()
        s.apply_user_close()
        r = Boss.user_close_review_list(
            params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']
        r = Boss.close_user(f'{apply_no}1', json={
                        'operateType': 0, 'applyNo': apply_no})
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True
        
        time.sleep(config.USER_CLOSE_DELAY - 10)
        r = s.login(json={
            "type": "phone",
            "regionCode": u['regionCode'],
            "phone": u['phone'],
            "password": "999999"
        })
        assert r.status_code == 403
        j = r.json()
        assert j['code'] == 'USER_STATUS_DISABLE'
        assert j['success'] == False

        time.sleep(15)
        r = s.login(json={
            "type": "phone",
            "regionCode": u['regionCode'],
            "phone": u['phone'],
            "password": "999999"
        })
        assert r.status_code == 403
        j = r.json()
        assert j['code'] == 'PHONE_USER_NOT_EXIST'
        assert j['success'] == False

    def test_reject_user_close(self):
        '''拒绝用户申请 用户可以登录
        '''
        u, s = login()
        r = s.apply_user_close()
        assert r.status_code == 200
        r = Boss.user_close_review_list(
            params={'userId': u['id'], 'searchStyle': 1})

        apply_no = r.json()['data']['list'][0]['apply_no']
        r = Boss.close_user(f'{apply_no}1', json={
                        'operateType': 1, 'applyNo': apply_no})
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True
        
        
        r = s.login(json={
            "type": "phone",
            "regionCode": u['regionCode'],
            "phone": u['phone'],
            "password": "999999"
        })
        assert r.status_code == 200
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True

    def test_cancel_user_close(self):
        '''冷静期取消用户注销
        '''
        u, s = login()
        s.apply_user_close()
        r = Boss.user_close_review_list(
            params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']
        r = Boss.close_user(f'{apply_no}1', json={
                        'operateType': 0, 'applyNo': apply_no})
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True
        
        r = Boss.close_user(f'{apply_no}1', json={
                        'operateType': 2, 'applyNo': apply_no})
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True
        
        r = s.login(json={
            "type": "phone",
            "regionCode": u['regionCode'],
            "phone": u['phone'],
            "password": "999999"
        })
        assert r.status_code == 200
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True

       
    
    def test_not_supported_operation(self):
        '''
        操作: 取消/同意/拒绝
        状态: 审核中/注销中/已注销/已取消/已拒绝
        共3*5=15种情况（1/3）
        1 可以同意审核中
        3 不能操作已注销的申请
        3 不能取消审核中，不能同意/拒绝注销中
        '''
        u, s = login()
        s.apply_user_close()
        r = Boss.user_close_review_list(
            params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']

        
        # 取消 审核中 ❌
        f(apply_no, 2, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 同意 审核中 -> 注销中 ✅
        f(apply_no, 0, 'SUCCESS', True)
        # 同意 注销中 ❌
        f(apply_no, 0, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 拒绝 注销中 ❌
        f(apply_no, 1, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)

        time.sleep(config.USER_CLOSE_DELAY)
        # 同意 已注销 ❌
        f(apply_no, 0, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 拒绝 已注销 ❌
        f(apply_no, 1, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 取消 已注销 ❌
        f(apply_no, 2, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)

    def test_not_supported_operation_4_cancelled(self):
        '''操作: 取消/同意/拒绝
        状态: 审核中/注销中/已注销/已取消/已拒绝
        共3*5=15种情况（2/3）
        1 可以取消注销中
        3 不能操作已取消的申请 
        '''
        u, s = login()
        s.apply_user_close()
        r = Boss.user_close_review_list(
            params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']
        
        # 同意 审核中 -> 注销中
        f(apply_no, 0, 'SUCCESS', True)
        # 取消 注销中 -> 已取消 ✅
        f(apply_no, 2, 'SUCCESS', True)
        
        # 同意 已取消 ❌
        f(apply_no, 0, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 拒绝 已取消 ❌
        f(apply_no, 1, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 取消 已取消 ❌
        f(apply_no, 2, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)

    def test_not_supported_operation_4_rejected(self):
        '''操作: 取消/同意/拒绝
        状态: 审核中/注销中/已注销/已取消/已拒绝
        共3*5=15种情况（3/3）
        1 可以拒绝审核中
        3 不能操作已拒绝的申请 
        '''
        u, s = login()
        s.apply_user_close()
        r = Boss.user_close_review_list(
            params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']
        
        # 拒绝 审核中 -> 已拒绝 ✅
        f(apply_no, 1, 'SUCCESS', True)
        
        # 同意 已拒绝 ❌
        f(apply_no, 0, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 拒绝 已拒绝 ❌
        f(apply_no, 1, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)
        # 取消 已拒绝 ❌
        f(apply_no, 2, 'STATE_NOT_ALLOWED_OPERATE_CODE', False)


    def test_reason(self):
        '''todo
        '''
    @pytest.mark.asyncio
    async def test_con_apply(self):
        '''并发申请注销 
        
        '''
        u, s = login()
        kwargs = {
            'url': Sess.URL_CLOSE_USER,
            'headers': s.HEADERS,
            'method': 'POST',
            'json': {}
        }
        res = await areq([kwargs]*10)
        codes = []
        for r in res:
            assert r.status == 200
            codes.append((await r.json())['code'])
        print({c: codes.count(c) for c in set(codes)})
        assert codes.count('SUCCESS') == 1
        
        r = Boss.user_close_review_list(params={'searchStyle': 1, 'userId': u['id']})
        assert r.status_code == 200
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert len(j['data']['list']) == 1

    @pytest.mark.asyncio
    async def test_multiple_users_con_apply(self):
        '''多用户并发申请注销
        '''
        kw = []
        
        us = login_n(10)
        assert len(us) == 10
        for u, s in us:
            kw.append({
                'url': Sess.URL_CLOSE_USER,
                'headers': s.HEADERS,
                'method': 'POST',
                'json': {}
            })
        res = await areq(kw * 5)
        rs = {}
        rs2 = {}
        for r in res:
            assert r.status == 200
            j = await r.json()
            c = j['code']
            a = r.request_info.headers['authorization']
            # print(a, c, j)
            if a in rs:
                if c in rs[a]:
                    rs[a][c] += 1
                else:
                    rs[a][c] = 1
            else:
                rs[a] = {c: 1}
            if c in rs2:
                if a in rs2[c]:
                    rs2[c][a] += 1
                else:
                    rs2[c][a] = 1
            else:
                rs2[c] = {a:1}
        print(json.dumps(rs))
        print(json.dumps(rs2))
        assert 'SUCCESS' in rs2
        assert len(rs2['SUCCESS']) == 10
        for a in rs2['SUCCESS']:
            assert rs2['SUCCESS'][a] == 1
    
    def test_phone_availability(self):
        '''手机号的释放'''
        u = register().json()['data']['user']
        
        # 手机号不可以重复注册
        r = register(u['regionCode'], u['phone'])
        assert r.status_code == 403
        assert r.json()['code'] == 'PHONE_REGISTERED'
        
        s = Sess()
        s.login(json={
            "type": "phone",
            "regionCode": u['regionCode'],
            "phone": u['phone'],
            "password": "999999"
        })

        s.apply_user_close()

        # 申请注销后 不可以重复注册
        r = register(u['regionCode'], u['phone'])
        assert r.status_code == 403
        assert r.json()['code'] == 'PHONE_REGISTERED'
        
        r = Boss.user_close_review_list(params={'userId': str(u['id']), 'searchStyle': 1})
        apply_no = r.json()['data']['list'][0]['apply_no']
        r = Boss.close_user(f'{apply_no}1', json={
                        'operateType': 0, 'applyNo': apply_no})
        j = r.json()
        assert j['code'] == 'SUCCESS'
        assert j['success'] is True
        
        # 冷静期 手机号不可以注册
        r = register(u['regionCode'], u['phone'])
        assert r.status_code == 403
        assert r.json()['code'] == 'PHONE_REGISTERED'

        time.sleep(config.USER_CLOSE_DELAY + 5)

        # 冷静期后 手机号可以注册成功
        r = register(u['regionCode'], u['phone'])
        assert r.status_code == 201
        
        # 手机号不可以重复注册
        r = register(u['regionCode'], u['phone'])
        assert r.status_code == 403
        assert r.json()['code'] == 'PHONE_REGISTERED'


    