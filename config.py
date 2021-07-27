BASE_URL = 'http://192.168.4.200:5004/mall/v2'
SEARCH_BASE_URL = 'http://192.168.4.200:5006/rpc/pub/v1/search'
PAY_ADMIN_BASE_URL = 'https://pay-admin-wkm.vmovier.cc'
TESTAPI_BASE = 'https://t.vmovier.cc'


USER_ID = 10000010
# USER_ID = 12340006
USER_ID_WANGCHANG = 10000002 
USER_ID2 = 11111112
USER_ID3 = 10006752
USER_ID_TANGYE = 10000006
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