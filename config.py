BASE_URL = 'http://192.168.4.200:5004/mall/v2'
SEARCH_BASE_URL = 'http://192.168.4.200:5006/rpc/pub/v1/search'
PAY_ADMIN_BASE_URL = 'https://pay-admin-wkm.vmovier.cc'
TESTAPI_BASE = 'http://192.168.103.100:5000'
X_USER_TOKEN = "eyAiaWQiOiAiMSIsICJ1c2VybmFtZSI6ICJ6aGFuZ3NhbiIsICJuaWNrbmFtZSI6ICJ6aGFuZ3NhbiIsICJlbWFpbCI6ICJ6aGFuZ3NhbkB4aW5waWFuY2hhbmcuY29tIiB9.72cc72bd0924b2bbe747c1267719ad44359d6cc4"

PAY_NOTICE_DELAY = 0
# CASHIER_URL = 'https://dev-cashier.vmovier.cc/'

USER_ID = 10265312
USER_ID2 = 11111112
USER_ID3 = 10006752
BLOCKED_USER_ID = 11111111
STORE1 = 'mock2'
STORE2 = 'mock3'
STORE3 = 'mock4'
STORE4 = 'mock5'
STORE_RESOURCE = 'resource'
STORE5 = STORE_RESOURCE
STORE_NOT_EXIST = 'store_not_exist_yhnmkijhasdf'
SKU_ID_NOT_EXIST = 'sku-id-not-exist-izcvkjhqwer'

try:
    from config_local import *
except:
    pass