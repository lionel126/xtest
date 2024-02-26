# to be continued...
import time
from pages.passport.person_verify import PersonVerify

def test_change_nickname():
    p = PersonVerify()
    p.load_with_auth('A60E14C5765A97B2D765A94942765A99417765A944CC5343DC84')    
    p.upload_credential()
    p.choose_role()
    p.desc('damn it!')    
    p.agree()
    p.submit()

def test_request():
    p = PersonVerify()
    p.load_with_auth('A60E14C5765A97B2D765A94942765A99417765A944CC5343DC84')
    # seleniumwire.webdriver
    # print(p.driver.requests)
    time.sleep(30)