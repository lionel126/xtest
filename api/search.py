from config import SEARCH_BASE_URL
from requests import request
from utils.utils import append, replace


def query(method="GET", params=None, **kwargs):
    '''query

    :param userId:	TYPE_UINT64	用户/访客 (用于收集用户的搜索)
    :param q:	TYPE_STRING	关键字
    :param vendor:	TYPE_STRING	供应商 xpc, pond5, vfine. 不传时包括所有供应商
    :param producerId:	TYPE_STRING	供稿人 (供稿人id)
    :param productTypes:	[]TYPE_STRING	商品类型 footage, music, ae, photo, illustration. 因产品需求，部分列表页需要多种具体素材类型组合为一种，比如 picture(图片）包括 photo、illustration
    :param isAlpha:	TYPE_INT32	是否透明 0:全部 1:否 2:是
    :param isLoop:	TYPE_INT32	是否循环 0:全部 1:否 2:是
    :param isVipArea:	TYPE_INT32	是否为会员专区 0:全部 1:否 2:是
    :param resolution:	TYPE_STRING	分辨率: 720p, 1080p, 2k, 4k, all, 为空表示全部
    :param aspectRatio:	TYPE_STRING	宽高比: 4:3, 16:9, superWide 超宽屏, ultraWide 极宽屏, all, 自定义 100:100， 为空时表示全部
    :param duration:	TYPE_STRING	时长筛选: (前闭后开) 1 分钟以下: "0,60"; 1-3 分钟: "60,180"; 3-5 分钟: "180,300"; 全部: "all"， 为空表示全部
    :param color:	TYPE_STRING	色系 (暂时不支持)
    :param bpm:	TYPE_STRING	音乐bpm筛选（格式同duration) 如 "0,79" (前闭后开) 全部: "all"， 为空表示全部
    :param sort:	TYPE_STRING	排序方式 default 综合排序, hotDownload 热门下载, latest 最新
    :param page:	TYPE_INT32	分页， 默认 1
    :param pageSize:	TYPE_INT32	页大小，默认 40 最大 64
    '''
    url = SEARCH_BASE_URL + '/query'
    if params is None:
           params = {}
    append(kwargs, params, ("userId", "q", "vendor", "producerId", "productTypes", "isAlpha", "isLoop",
           "isVipArea", "resolution", "aspectRatio", "duration", "color", "bpm", "sort", "page", "pageSize"))
    return request(method=method, url=url, params=params)
