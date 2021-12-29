from config import USER_CENTER_BASE_URL, X_USER_TOKEN
from requests import request
from functools import wraps
import random
from utils.utils import fake
import time

BOSS_HEADERS = {
    "x-user-id": "1", 
    # "x-user-token": boss_gateway_token(), # token算法
    "x-user-token": X_USER_TOKEN
}



def set_auth(func):
    @wraps(func)
    def wrapper(slf, **kwargs):
        r = func(slf, **kwargs)
        if 'set-authorization' in r.headers:
            slf.HEADERS['authorization'] = r.headers['set-authorization']
        return r
    return wrapper

class Sess():
    
    URL_LOGIN = f'{USER_CENTER_BASE_URL}/v2/user/login'
    URL_REGISTER = f'{USER_CENTER_BASE_URL}/v2/user/register'
    URL_SEND_CAPTCHA = f'{USER_CENTER_BASE_URL}/v2/captcha/send'
    URL_CLOSE_USER = f'{USER_CENTER_BASE_URL}/v2/user/close'
    URL_USER_INFO = f'{USER_CENTER_BASE_URL}/v2/user/info/all'
    URL_APPLY_REALNAME = f'{USER_CENTER_BASE_URL}/v2/user/verify/realname/push'
    
    def __init__(self):
        self.HEADERS = {'device-no': f'xpctest-{time.time()}'}
    
    @set_auth
    def login(self, method='POST', headers=None, json=None):
        '''
        :param json: {
            #
            #### optional ⬇  
            loginType:int	不建议使用, 登录类型 3 - 手机号+密码登录、4 - 邮箱+密码登录 6 - 手机号+验证码登录
            type:string	建议使用该参数来标明登录类型, 手机号+密码登录:phone、邮箱+密码登录:email、手机号+验证码登录:captcha
            regionCode:string	地区区号,不传默认+86
            phone:string	用户手机号,短信验证码登录,手机密码登录下必填
            email:string	用户邮箱,邮箱登录下必填
            password:string	登录密码,密码登录下必填
            smsCaptcha:string	短信验证码,验证码登录下必填
            thirdTmpToken:string	第三方绑定现有的账号并且通过验证码登录下必填
        }
        '''
        if headers is None: headers = self.HEADERS
        res = request(method, Sess.URL_LOGIN, headers=headers, json=json)
        # if 'Set-Authorization' in res.headers:
        #     self.HEADERS['authorization'] = res.headers['Set-Authorization']
        return res

    def register(self, method='POST', headers=None, json=None):
        '''
        :param json: {
            # 
            #### mandatory ⬇
            phone:string	注册手机号
            #### optional ⬇
            regionCode:string	地区区号,不传默认+86
            nickname:string	用户昵称
            password:string	用户密码
            smsCaptcha:string	短信验证码
            quickMode:boolean	是否是快速注册模式, 默认是true
            thirdTmpToken:string	第三方登录失败需注册情况下,下发的临时 token
            ticket:string	验证码客户端验证回调的票据(腾讯验证码服务)
            randStr:string	验证码客户端验证回调的随机串(腾讯验证码服务)
            captchaState:string	验证码state透传
        }
        '''
        if headers is None: headers = self.HEADERS
        return request(method, Sess.URL_REGISTER, headers=headers, json=json)

    def user_info(self, method='GET', headers=None, params=None):
        '''
        :param params: {
            query	int	是	查询类型, 0x0001 : 基础信息, 0x0010:扩展信息, 0x0100:第三方信息, 0x1000:认证信息.举例说明:同时需要基础信息和扩展信息则为0x0011,则query值为3,同时需要基础信息和认证信息的话则为0x1001,query值为9,如果需要全部信息则为0x1111,query值为15 以此类推
        }
        '''
        if headers is None: headers = self.HEADERS
        return request(method, Sess.URL_USER_INFO, headers=headers, params=params)
    
    @set_auth
    def send_captcha(self, method='POST', headers=None, json=None):
        '''
        :param json: {
            regionCode:string	地区区号,不传默认+86
            phone:string	用户手机号
            type:int	验证码类型 0	修改手机号-验证现有手机号, 1	修改密码, 2	重置密码, 3	修改邮箱, 4	验证码登录, 5	注册时验证手机号, 6	修改手机号-验证新手机号, 7	游客绑定手机号, 8	苹果未授权账号绑定手机号, 9	签约银行账号之前 验证注册手机号, 10	注销
        }
        
        '''
        if headers is None: headers = self.HEADERS
        res = request(method, Sess.URL_SEND_CAPTCHA, headers=headers, json=json)

        return res
        



    def apply_user_close(self, method="POST", headers=None, json=None):
        '''
        :param headers: {
                divice-no: ''
                authorization: ''
            }
        :param json: {
                'applyReason': '' # optional apply_00001 - apply_00004
            }
        '''
        if headers is None: headers = self.HEADERS
        if json is None: json={'applyReason': random.choice(['apply_00001', 'apply_00002', 'apply_00003', 'apply_00004', 'apply_00020'])}
        if json and 'applyReason' in json and json['applyReason'] == 'apply_00020':
            json['applyReasonValue'] = fake.text(max_nb_chars=30)
            
        return request(method, Sess.URL_CLOSE_USER, headers=headers, json=json)

    def apply_for_realname(self, method='POST', headers=None, json=None):
        '''
        :param json: {  
            "type": "alipay", // alipay: 支付宝, foreign : 国外
            "realname":"李哲",  
            "platform":"app", // 支付宝实名认证的平台, app, mobile, pc 
            "returnUrl":"https://www.xinpianchang.com" , // 落地页,必传
            "idNumber": "372901200707060213", // 身份证号, 支付宝认证必传
            "credential": "https://www.xinpianchang.com/工牌.png", // 证明材料, 海外认证必传
            "credentialInHand": "https://www.xinpianchang.com/手持工牌.png" // 手持证明材料, 海外认证必传
        }
        '''
        if headers is None: headers = self.HEADERS
        if json is None: 
            json={
                "credential": "https://oss-xpc0.xpccdn.com/passport/assets/verify/11486339/2021/12/61c5773a64a95.jpg",
                "credentialInHand": "https://oss-xpc0.xpccdn.com/passport/assets/verify/11486339/2021/12/61c57732c3785.jpg",
                "realname": "hello",
                "type": "foreign"
            }
        return request(method, Sess.URL_APPLY_REALNAME, headers=headers, json=json)

class Boss():
    URL_USER_CLOSE_REVIEW_LIST = f'{USER_CENTER_BASE_URL}/v2/internal/user/close/review'
    URL_ACCEPT_USER_CLOSE = f'{USER_CENTER_BASE_URL}' + '/v2/internal/user/{}/close/review'
    URL_REVIEW_REALNAME = f'{USER_CENTER_BASE_URL}' + '/v2/internal/user/verify/realname/{}'
    URL_REALNAME_LIST = f'{USER_CENTER_BASE_URL}' + '/v2/user/internal/user/verify/realname/list'
    URL_REASON = f'{USER_CENTER_BASE_URL}' + '/v2/internal/user/{}/reason'
    
    @staticmethod
    def user_close_review_list(method='GET', headers=None, params=None):
        '''
        :param params: {
            # 
            #### mandatory ⬇
            searchStyle: int	查询类型 1-待人工审核列表 2-注销中列表 3-已注销列表 4-拒绝列表 5取消列表
            #### optional ⬇
            applyNo: string	申请编号
            applyStartTime: string	申请开始时间（yyyy-MM-dd HH:mm:SS）
            applyEndTime: string	申请结束时间（yyyy-MM-dd HH:mm:SS）
            applyReason: string	申请原因
            approvalStartTime: string	审核通过开始时间（yyyy-MM-dd HH:mm:SS）
            approvalEndTime: string	审核通过结束时间（yyyy-MM-dd HH:mm:SS）
            cancelStartTime: string	取消开始时间（yyyy-MM-dd HH:mm:SS）
            cancelEndTime: string	取消结束时间（yyyy-MM-dd HH:mm:SS）
            cancelReason: string	取消原因
            refuseStartTime: string	拒绝开始时间（yyyy-MM-dd HH:mm:SS）
            refuseEndTime: string	拒绝结束时间（yyyy-MM-dd HH:mm:SS）
            refuseReason: string	拒绝原因
            logoutStartTime: string	实际注销开始时间（yyyy-MM-dd HH:mm:SS）
            logoutEndTime: string	实际注销结束时间（yyyy-MM-dd HH:mm:SS）
            reviewOperaters: string	审核操作人（多个用","分开，如:（1212，2323））
            applyReason: string	申请理由
            userId: string	用户id
            page: int	页数 默认1
            size: int	每页数量 默认20   
        }
        '''
        if headers is None: headers = BOSS_HEADERS
        return request(method, Boss.URL_USER_CLOSE_REVIEW_LIST, headers=headers, params=params)

    @staticmethod
    def close_user(applyNo, method='POST', headers=None, json=None):
        '''boss 注销用户

        :param json: {
            applyNo	string	是	申请编号  

            operateType	string	是	操作类型: 0-同意 1-拒绝 2-取消  

            reason	string	否	取消原因code或拒绝原因code
        }
        '''
        if headers is None: headers = BOSS_HEADERS
        return request(method, Boss.URL_ACCEPT_USER_CLOSE.format(applyNo), headers=headers, json=json)

    @staticmethod
    def realname_list(method='POST', headers=None, json=None):
        '''
        status	string	列表类型, INREVIEW/REJECTED/MERGED(待审核/未通过/已通过)
        userId	string	用户ID
        page	int	页数
        size	int	每页条数, 默认为20
        '''
        if headers is None: headers = BOSS_HEADERS
        return request(method, Boss.URL_REALNAME_LIST, headers=headers, json=json)
    
    @staticmethod
    def verify_realname(id, method='POST', headers=None, json=None):
        '''
        status	string	认证结果:REJECTED/MERGED(拒绝通过/通过)
        rejectReason	string	拒绝原因:身份证不够清晰
        '''
        if headers is None: headers = BOSS_HEADERS
        return request(method, Boss.URL_REVIEW_REALNAME.format(id), headers=headers, json=json)

    @staticmethod
    def reason(typ, method="GET", headers=None):
        '''
        type	string	是	0-申请理由 1-拒绝原因 2-取消原因
        '''
        if headers is None: headers = BOSS_HEADERS
        return request(method, Boss.URL_REASON.format(typ), headers=headers)