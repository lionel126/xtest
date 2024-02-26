from urllib.parse import urlparse, parse_qs
from api import XpcApi

'''文案测试
    Android/iOS
    vip/svip
'''
expectation_base = {
    "data": {
        "vipTipMessage": {
            "agreement": [
                {
                    "link": "https://www.xinpianchang.com/aboutus/vip?t=0",
                    "name": "《新片场会员协议》"
                },
                {
                    "link": "https://www.xinpianchang.com/aboutus/vip?t=1",
                    "name": "《新片场自动续费协议》"
                }
            ],
            "skus": [
                {"confirmDescription": "支付并开通",},
                {"confirmDescription": "支付并开通",}
            ],
            "tags": [
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264ead458286.png",
                    "link": "",
                    "name": "作品优先推荐",
                    "type": "normal"
                },
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264ead45c2f0.png",
                    "link": "",
                    "name": "联系创作人",
                    "type": "normal"
                },
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264ead467970.png",
                    "link": "",
                    "name": "作品高级搜索",
                    "type": "normal"
                },
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264ead466bea.png",
                    "link": "",
                    "name": "音视频课程免费领",
                    "type": "normal"
                },
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264ead44b910.png",
                    "link": "",
                    "name": "商用素材优惠券",
                    "type": "normal"
                },                    
            ]
        }
    }
}
expectation_svip_ios = {
    "data": {
        "vipTipMessage": {
            # bug: svip iOS im 
            "remind": "自动续费服务声明\n付款：用户确认购买并付款后记入iTunes 账户\n取消续订：如需取消续订，请在当前订阅周期到期24小时以前，手动在iTunes/Apple ID设置管理中关闭自动续费功能；到期前24小时内取消，将会收取订阅费用\n续费：iTunes 账户会在到期前24小时内扣费，扣费成功后顺延一个订阅周期",
            "skus": [
                {
                    "isRecommend": False,
                    "isSelected": True,
                    "name": "连续包月",
                    "price": "158",
                    "priceDescription": "",
                    "priceText": "¥158/月",
                    "skuID": "NewStudios_SVIP_Month_Sub",
                    "storeCode": "vip_center"
                },
                {
                    "isRecommend": True,
                    "isSelected": False,
                    "name": "连续包年",
                    "price": "1698",
                    "priceDescription": "折合每月141.5元",
                    "priceText": "¥1698/年",
                    "skuID": "NewStudios_SVIP_Year_Sub",
                    "storeCode": "vip_center"
                }
            ],
            "vipFlag": 3
        }
    }
}
expectation_vip_ios = {
    "data": {
        "vipTipMessage": {
            "remind": "自动续费服务声明\n付款：用户确认购买并付款后记入iTunes 账户\n取消续订：如需取消续订，请在当前订阅周期到期24小时以前，手动在iTunes/Apple ID设置管理中关闭自动续费功能；到期前24小时内取消，将会收取订阅费用\n续费：iTunes 账户会在到期前24小时内扣费，扣费成功后顺延一个订阅周期",
            "skus": [
                {
                    "isRecommend": False,
                    "isSelected": True,
                    "name": "连续包月",
                    "price": "40",
                    "priceDescription": "到期按￥40/月自动续费",
                    "priceText": "新用户首月28元",
                    "skuID": "NewStudios_VIP_Month_Sub",
                    "storeCode": "vip_center"
                },
                {
                    "isRecommend": False,
                    "isSelected": False,
                    "name": "连续包年",
                    "price": "348",
                    "priceDescription": "折合每月29元",
                    "priceText": "¥348/年",
                    "skuID": "NewStudios_VIP_Year_Sub",
                    "storeCode": "vip_center"
                }
            ],
            "vipFlag": 1
        }
    }
}
expectation_svip_android = {
    "data": {
        "vipTipMessage": {
            "skus": [
                {
                    "isRecommend": False,
                    "isSelected": True,
                    "name": "连续包月",
                    "price": "158",
                    "priceDescription": "",
                    "priceText": "¥158/月",
                    "skuID": "v_super_month_subscribe",
                    "storeCode": "vip_center"
                },
                {
                    "isRecommend": False,
                    "isSelected": False,
                    "name": "单年",                        
                    "price": "1698",
                    "priceDescription": "折合每月141.5元",
                    "priceText": "¥1698/年",
                    "skuID": "v_super_year",
                    "storeCode": "vip_center"
                }
            ],
            "vipFlag": 3
        }
    }
}
expectation_vip_android = {
    "data": {
        "vipTipMessage": {
            "skus": [
                {
                    "isRecommend": False,
                    "isSelected": True,
                    "name": "连续包月",
                    "price": "39",
                    "priceDescription": "",
                    "priceText": "¥39/月",
                    "skuID": "v_general_month_subscribe",
                    "storeCode": "vip_center"
                },
                {
                    "isRecommend": False,
                    "isSelected": False,
                    "name": "连续包年",
                    "price": "348",
                    "priceDescription": "折合每月29元",
                    "priceText": "¥348/年",
                    "skuID": "v_general_year_subscribe",
                    "storeCode": "vip_center"
                }
            ],
            "vipFlag": 1
        }
    }
}

# svip 私信
expectation_svip_im = {
    "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "联系更多创作人请开通超级会员",
            "subTitle": "普通会员只能联系30位创作人",
            "guide": "开通新片场超级会员，即可享无限量联系创作人特权",
            "description": "超级会员每月联系创作人名额无限制，联系更高效",
            "channel": "appInstantMessage",
            "link": "https://vip-test.xinpianchang.com?channel=appInstantMessage",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappInstantMessage",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        },
        
    },
    "message": "",
    "status": -1
}

# svip 私密存储
expectation_svip_private_storage = {
    "data": {
        "vipTipMessage": {
            "title": "升级超级会员可获得更多空间",
            "subTitle": "普通会员空间为100G",
            "guide": "私密视频空间不足",
            "description": "超级会员享500G私密视频空间：下载不限速，加密分享，在线高清播放",
            "channel": "appPrivateExpandSpace",
            "link": "https://vip-test.xinpianchang.com?channel=appPrivateExpandSpace",
            "tags":[
                {},{},{},{},{},
                # bug: svip privateSpace
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappPrivateExpandSpace",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "私密视频空间不足，可升级会员扩容",
    "status": 1024
}
# svip download high quality video
expectation_svip_download_high_quality = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "超清下载为会员专属功能",
            "subTitle": "普通会员不可下载该作品",
            "guide": "开通新片场会员，即可享用超清下载、商用素材优惠券等 20 大特权",
            "description": "超级会员可以下载经作者授权的超清作品",
            "channel": "appPublicVideoDownload",
            "link": "https://vip-test.xinpianchang.com?channel=appPublicVideoDownload",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappPublicVideoDownload",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "",
    "status": -1
}

# vip 私信
expectation_vip_im = {
    "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "联系合作为会员专属功能",
            "subTitle": "非会员需要相互关注",
            "guide": "开通新片场会员，即可享用创作人高级筛选及联系合作等 20 大特权",
            "description": "普通会员每月可以联系 30 位创作人，沟通学习、快速搭建团队",
            "channel": "appInstantMessage",
            "link": "https://vip-test.xinpianchang.com?channel=appInstantMessage",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappInstantMessage",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        },
        
    },
    "message": "",
    "status": -1
}

# vip search auth
expectation_vip_search_auth = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "专业搜索为会员专属功能",
            "subTitle": "非会员为普通搜索",
            "guide": "开通新片场会员，即可享用专业搜索、高清下载等20 大特权",
            "description": "100多个搜索维度，搜索体验更加全面、专业，帮你快速找样片，找灵感",
            "channel": "appAdvanceSearch",
            "link": "https://vip-test.xinpianchang.com?channel=appAdvanceSearch",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappAdvanceSearch",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "",
    "status": 1024
}
# vip creators auth
expectation_vip_creators_auth = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "高级筛选为会员专属功能",
            "subTitle": "非会员不能使用该功能",
            "guide": "开通新片场会员，即可享用创作人联系合作、高级筛选等 20 大特权",
            "description": "精准筛选项目类型、职位分类，快速找到优质活跃创作人",
            "channel": "appCreatorListAdvancedFilter",
            "link": "https://vip-test.xinpianchang.com?channel=appCreatorListAdvancedFilter",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappCreatorListAdvancedFilter",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "",
    "status": -1
}
# vip allow comment
expectation_vip_allow_comment = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "关闭评论为会员专属功能",
            "subTitle": "非会员不能关闭评论",
            "guide": "开通新片场会员，即可享用关闭评论、隐私访问等 20 大特权",
            "description": "作品关闭评论后，用户不能在当前作品评论",
            "channel": "appCommentAreaDisable",
            "link": "https://vip-test.xinpianchang.com?channel=appCommentAreaDisable",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappCommentAreaDisable",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "开通新片场会员\n解锁“关闭评论”特权\n评论管理更方便",
    "status": -1
}

# vip download origin video
expectation_vip_download_url = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "下载原片为会员专属功能",
            "subTitle": "非会员只能下载普通清晰度作品",
            "guide": "开通新片场会员，即可享用下载原片等 20 大特权",
            "description": "作者下载自己上传的作品时，可按照原片清晰度下载",
            "channel": "appPersonalVideoDownload",
            "link": "https://vip-test.xinpianchang.com?channel=appPersonalVideoDownload",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappPersonalVideoDownload",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "",
    "status": -1
}

# vip download low quality video
expectation_vip_download_low_quality = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "高清下载为会员专属功能",
            "subTitle": "非会员不可下载该作品",
            "guide": "开通新片场会员，即可享用高清下载、商用素材优惠券等 20 大特权",
            "description": "会员可以下载经作者授权的高清作品",
            "channel": "appPublicVideoDownload",
            "link": "https://vip-test.xinpianchang.com?channel=appPublicVideoDownload",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappPublicVideoDownload",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "",
    "status": -1
}

# vip allow private article to be able to download
expectation_vip_article_share = {
    # "code": "VIP_TIP",
    "data": {
        "vipTipMessage": {
            "title": "私密视频允许观看下载为会员专属功能",
            "subTitle": "非会员不能使用该功能",
            "guide": "开通新片场会员，即可享用私密视频允许观看下载等 20 大特权",
            "description": "作者可设置私密视频的分享权限，使团队协作环境更私密安全",
            "channel": "appPrivateAllowDownload",
            "link": "https://vip-test.xinpianchang.com?channel=appPrivateAllowDownload",
            "tags":[
                {},{},{},{},{},
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappPrivateAllowDownload",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "",
    "status": -1
}
# vip: private storage space
expectation_vip_private_storage = {
    "data": {
        "vipTipMessage": {
            "title": "会员可获得更多空间",
            "subTitle": "非会员空间为10G",
            "guide": "私密视频空间不足",
            "description": "会员享100G私密视频空间：下载不限速，加密分享，在线高清播放",
            "channel": "appPrivateExpandSpace",
            "link": "https://vip-test.xinpianchang.com?channel=appPrivateExpandSpace",
            "tags":[
                {},{},{},{},{},
                # bug: svip privateSpace
                {
                    "icon": "https://oss-xpc0.xpccdn.com/Upload/edu/2022/04/246264edf2eedd4.png",
                    "link": "newstudios-ent://app-test.xinpianchang.com/web?url=https%3A%2F%2Fvip-test.xinpianchang.com%3Fchannel%3DappPrivateExpandSpace",
                    "name": "查看全部权益",
                    "type": "all"
                }
            ],
        }
    },
    "message": "私密视频空间不足，可升级会员扩容",
    "status": 1024
}


def assert_link_equal(act, exp, key=''):
    '''判断 scheme netloc path fragment 和 query.channel是否相等
    '''
    # print(act, exp, key)
    a = urlparse(act)
    e = urlparse(exp)
    for k in ('scheme', 'netloc', 'path', 'fragment'):    
        assert getattr(a, k) == getattr(e, k), f'{key}.{k}'
    
    aqs = parse_qs(a.query)
    eqs = parse_qs(e.query)
    
    for k, v in eqs.items():
        if k == 'channel':
            assert k in aqs, f'{key}.query.{k}'
            assert aqs[k] == v, f'{key}.query.{k}'


def assert_recursive_equal(act, exp, key=''):
    if isinstance(exp, dict):
        for k, v in exp.items():
            assert_recursive_equal(act[k], v, key=f'{key}.{k}')
    elif isinstance(exp, list):
        for idx in range(len(exp)):
            assert_recursive_equal(act[idx], exp[idx], key=f'{key}[{idx}]')
    else:
        if key == '.data.vipTipMessage.link':
            # 这个link的query有点混乱 只判断query.channel是否相等
            assert_link_equal(act, exp, key)
        else:
            assert act == exp, f"{key}"

def session(level='non-vip', os='iOS', accept_version=None):
    assert level in ('vip', 'non-vip', 'expired-vip')
    assert os in ('iOS', 'Android')
    x = XpcApi()
    if level=='vip':
        x.login('164076873057', code='+54')
    elif level=='expired-vip':
        x.login('164076873040', code='+54')
    else:
        # 过期vip 和 从来没买过会员，两种情况
        x.login('164076873030', code='+54')
    
    if os == 'iOS':
        x.headers.update({'user-agent': 'NewStudiosEnterprise/2.0.1 (com.xinpianchang.newstudios.ent; build:1092; iOS 15.1.0)'})
    else:
        x.headers.update({'user-agent': 'NewStudios/2.0.1 (com.xinpianchang.newstudios.enterprise; build:906; Android 12)'})
    
    if accept_version:
        x.headers.update({'accept-version': accept_version})
    return x

def test_svip_ios_storage():

    # svip user数据需要提前准备: 1 vip, 2 会员私信额度用光, 3 会员私密存储用光
    x = session(level='vip', os='iOS')

    actual = x.check_private_space().json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_svip_ios)
    assert_recursive_equal(actual, expectation_svip_private_storage)

def test_svip_ios_im():
    # svip user数据需要提前准备: 1 vip, 2 会员私信额度用光, 3 会员私密存储用光
    x = session(level='vip', os='iOS')
    
    actual = x.im_quota(to=10731761).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_svip_ios)
    assert_recursive_equal(actual, expectation_svip_im)

def test_svip_ios_download_high_quality_video():
    # svip user数据需要提前准备: 1 vip, 2 会员私信额度用光, 3 会员私密存储用光
    x = session(level='vip', os='iOS') 
    
    actual = x.check_download_permission(11296256, quality='4k60').json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_svip_ios)
    assert_recursive_equal(actual, expectation_svip_download_high_quality)

def test_svip_android_storage():
    x = session(level='vip', os='Android')

    actual = x.check_private_space().json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_svip_android)
    assert_recursive_equal(actual, expectation_svip_private_storage)

def test_svip_android_im():
    x = session(level='vip', os='Android')
    
    actual = x.im_quota(to=10731761).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_svip_android)
    assert_recursive_equal(actual, expectation_svip_im)

def test_svip_android_download_high_quality_video():
    # svip user数据需要提前准备: 1 vip, 2 会员私信额度用光, 3 会员私密存储用光
    x = session(level='vip', os='Android') 
    
    actual = x.check_download_permission(11296256, quality='4k60').json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_svip_android)
    assert_recursive_equal(actual, expectation_svip_download_high_quality)

def test_vip_ios_search():
    # # vip user: 非会员
    x = session(accept_version='2.1.1')

    # 专业搜索
    actual = x.search_auth().json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_search_auth)

def test_vip_ios_filter():
    # # vip user: 非会员
    x = session()
    # 高级筛选
    actual = x.creators_auth().json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_creators_auth)

def test_vip_ios_comment():
    # # vip user: 非会员
    x = session()
    # 关闭评论
    actual = x.allow_comment(11296930).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_allow_comment)

def test_vip_ios_download_origin():
    '''作者下载原片'''
    x = session()
    # 下载地址
    actual = x.get_download_url(11296929).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_download_url)

def test_vip_ios_download_low_quality():
    '''vip下载低清晰度'''
    x = session()
    # 下载地址
    actual = x.check_download_permission(11296256).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_download_low_quality)

def test_vip_ios_share_private_article():
    '''私密作品允许下载'''
    x = session()
    # 下载地址
    actual = x.article_share(11296929).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_article_share)

def test_vip_ios_storage():
    # # vip user: 非会员
    x = session()

    actual = x.check_private_space(fileSize=1024**4 + 1).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_private_storage)

def test_vip_ios_im():
    # # vip user: 非会员
    x = session() 
    
    actual = x.im_quota(to=10731761).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_ios)
    assert_recursive_equal(actual, expectation_vip_im)

def test_vip_android_search():
    # # vip user: 非会员
    x = session(os='Android', accept_version='2.1.1')

    # 专业搜索
    actual = x.search_auth().json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_search_auth)

def test_vip_android_filter():
    # # vip user: 非会员
    x = session(os='Android')
    # 高级筛选
    actual = x.creators_auth().json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_creators_auth)

def test_vip_android_comment():
    # # vip user: 非会员
    x = session(os='Android')
    # 关闭评论
    actual = x.allow_comment(11296930).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_allow_comment)

def test_vip_android_download_origin():
    '''作者下载原片'''
    x = session(os='Android')
    # 下载地址
    actual = x.get_download_url(11296929).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_download_url)

def test_vip_android_download_low_quality():
    '''vip下载低清晰度'''
    x = session(os='Android')
    # 下载地址
    actual = x.check_download_permission(11296256).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_download_low_quality)

def test_vip_android_share_private_article():
    '''私密作品允许下载'''
    x = session(os='Android')
    # 下载地址
    actual = x.article_share(11296929).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_article_share)

def test_vip_android_storage():
    # # vip user: 非会员
    x = session(os='Android')

    actual = x.check_private_space(fileSize=1024**4 + 1).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_private_storage)

def test_vip_android_im():
    # # vip user: 非会员
    x = session(os='Android') 
    # todo 
    actual = x.im_quota(to=10731761).json()
    assert_recursive_equal(actual, expectation_base)
    assert_recursive_equal(actual, expectation_vip_android)
    assert_recursive_equal(actual, expectation_vip_im)

# def test_vip_ios_search_2():
#     # # vip user: 过期会员
#     x = session(level='expired-vip', accept_version='2.1.1')

#     # 专业搜索
#     actual = x.search_auth().json()
#     assert_recursive_equal(actual, expectation_base)
#     assert_recursive_equal(actual, expectation_vip_ios)
#     assert_recursive_equal(actual, expectation_vip_search_auth)

# def test_vip_ios_filter_2():
#     # # vip user: 非会员
#     x = session(level='expired-vip')
#     # 高级筛选
#     actual = x.creators_auth().json()
#     assert_recursive_equal(actual, expectation_base)
#     assert_recursive_equal(actual, expectation_vip_ios)
#     assert_recursive_equal(actual, expectation_vip_creators_auth)

# def test_vip_ios_comment_2():
#     # # vip user: 非会员
#     x = session(level='expired-vip')
#     # 关闭评论
#     # todo
#     actual = x.allow_comment(11296930).json()
#     assert_recursive_equal(actual, expectation_base)
#     assert_recursive_equal(actual, expectation_vip_ios)
#     assert_recursive_equal(actual, expectation_vip_allow_comment)