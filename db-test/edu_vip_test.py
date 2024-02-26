from datetime import datetime, timedelta
from db import edu_vip
from api.vip import trigger_status
from api import vip


# USER_ID = 11000000
# VIP_SNS_ID = 0
# VIP_EDU_ID = 31872


USER_ID = 10265312
VIP_SNS_ID = 30532
VIP_EDU_ID = 31852


def day(delta=0, date_str=''):
    '''
    :param date_str: format %Y-%m-%d
    '''
    if date_str:
        d = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        d = datetime.now()
    return (d + timedelta(days=delta)).date()

def test_vip_info():
    vip.vip_info(USER_ID)

def test_edu_vip():
    # edu_vip.update_expired_date(USER_ID, VIP_EDU_ID, day(30), vip_flag=8)
    edu_vip.update_expired_date(VIP_EDU_ID, end=day(90, date_str='2022-09-01'), start=day(date_str='2022-09-01'), vip_flag=8)


def test_edu_vip_expired():
    edu_vip.update_expired_date(VIP_EDU_ID, day(-7), vip_flag=8)

def test_sns_vip():
    edu_vip.update_expired_date(VIP_SNS_ID, day(+350), start=day(-15))
    vip.trigger_status(userId=USER_ID, group='sns')

def test_sns_vip_expired():
    edu_vip.update_expired_date(VIP_SNS_ID, day(-15), start=day(-45))
    vip.trigger_status(userId=USER_ID, group='sns')
