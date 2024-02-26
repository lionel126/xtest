from datetime import datetime, timedelta
from pages.vip.index import Index as Vip
from pages.passport.login import Login
from api.user_center import InternalApi as UserInt

PHONE = 13521141218
USERID = 10000010

ten_days_ago = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
twenty_days_later = (datetime.now() + timedelta(days=20)).strftime('%Y%m%d')

def login():
    l = Login()
    l.load()
    l.login(PHONE)

def vip_notify():
    UserInt.vip_notify(**{
        "user_id": USERID,
        "start_time": ten_days_ago,
        "end_time": twenty_days_later,
        "flag": 1,
        "type": 1
    })
def svip_notify():
    UserInt.vip_notify(**{
        "user_id": USERID,
        "start_time": ten_days_ago,
        "end_time": twenty_days_later,
        "flag": 3,
        "type": 2
    })    
def vip_expired_notify():
    UserInt.vip_notify(**{
        "user_id": USERID,
        "start_time": ten_days_ago,
        "end_time": ten_days_ago,
        "flag": 1,
        "type": 1
    })    


def test_vip():
    # vip_expired_notify()
    v = Vip()
    v.load()
    v.order()
    v.save_qr_screenshot()
