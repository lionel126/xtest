import os
from requests import request

# 金山上传
def upload_video_part(method='PUT', url='', headers=None, params=None, data=None):
    return request(method, url, params=params, headers=headers, data=data)


def upload_video(method='POST', url='', data=None, files=None):
    return request(method, url, data=data, files=files)


# xpc v1 upload
FILE = '/Users/chensg/Movies/marvel10_480p.mov'
FilePartSize = 204800

def get_file(file=FILE):
    file_size = os.path.getsize(file)
    return os.path.split(file)[1], file_size

def upload(j:dict, file=FILE, file_part_size=FilePartSize):
    '''
    :param j: upload_token 响应体
    '''
    url = j['data']['original']['uploadDomain']+ '/' + j['data']['original']['key']
    accessKeyId = j['data']['original']['accessKeyId']
    signatures = j['data']['original']['signature']
    uploadId = j['data']['original']['uploadId']
    partCount = j['data']['original']['partCount']
    with open(file, 'rb') as f:
        for i in range(partCount):
            partNumber = i + 1
            upload_video_part(
                url=url, 
                headers={'Authorization': f'KSS {accessKeyId}:{signatures[i]}'}, 
                params={
                    'partNumber': partNumber,
                    'uploadId': uploadId
                },
                data=f.read(file_part_size) if i < partCount - 1 else f.read()
            )
    return j['data']['original']['partCount'], j['data']['original']['uploadId'], j['data']['uploadNo']