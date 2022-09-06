import os
import time
import mimetypes
from datetime import datetime as dt
import pytest
from api.xpcapi import XpcApi
from api.upload import upload_video_part, upload_video


FILE = '/Users/chensg/Movies/qhl-10.mp4'
filePartSize = 204800

def get_file():
    file_size = os.path.getsize(FILE)
    return os.path.split(FILE)[1], file_size

@pytest.fixture
def user():
    app = XpcApi('18679311959')
    yield app
    app.logout()

def upload(j:dict):
    url = j['data']['original']['uploadDomain']+ '/' + j['data']['original']['key']
    accessKeyId = j['data']['original']['accessKeyId']
    signatures = j['data']['original']['signature']
    uploadId = j['data']['original']['uploadId']
    partCount = j['data']['original']['partCount']
    with open(FILE, 'rb') as f:
        for i in range(partCount):
            partNumber = i + 1
            upload_video_part(
                url=url, 
                headers={'Authorization': f'KSS {accessKeyId}:{signatures[i]}'}, 
                params={
                    'partNumber': partNumber,
                    'uploadId': uploadId
                },
                data=f.read(filePartSize) if i < partCount - 1 else f.read()
            )

def test_publish_v2():
    '''v2 upload api
    '''
    app = XpcApi()
    app.login(17600465113)
    now = dt.now().strftime('%Y%m%d%H%M%S')
    r = app.check_params(title=f'article{now}')
    formToken = r.json()['data']['formToken']
    
    # file = '/Users/csg/Movies/laoxie.mp4'
    file = '/Users/csg/Movies/tbbt_S11E16_name.mp4'
    file_size = os.path.getsize(file)
    file_name = os.path.split(file)[1]
    file_mime_type = mimetypes.guess_type(file)[0]
    r = app.upload_prepare(fileName=file_name, fileSize=file_size, fileMimeType=file_mime_type)
    data = r.json()['data']
    
    
    complete = []
    
    with open(file, 'rb') as f:
        for uploadParam in data['uploadParams']:
            if 'header' in uploadParam:
                # 分片
                r = upload_video_part(
                    method=data['requestMethod'], 
                    url=uploadParam['uploadUrl'], 
                    # params={'partNumber' :uploadParam['partNumber'], 'uploadId': data['uploadId']}, 
                    headers=uploadParam['header'], 
                    data=f.read(uploadParam['size'])
                )
            else:
                # 单片 'body' in uploadParam
                r = upload_video(
                    method=data['requestMethod'], 
                    url=uploadParam['uploadUrl'], 
                    data=uploadParam['body'],
                    files=[('file', (file_name, f, file_mime_type))]
                )
            result = {
                "body": "",
                "headers": {
                    "ETag": r.headers['etag'],
                }, 
                "partNumber": uploadParam['partNumber'],
            }
            complete.append(result)
            
    app.upload_complete(complete=complete, fileName=file_name, uploadNo=data['uploadNo'], formToken=formToken)




def test_publish_v1(user:XpcApi):
    '''
    '''
    key, fileSize = get_file()
    res = user.upload_token(key=key, fileSize=fileSize, filePartSize=filePartSize)
    j = res.json()
    
    upload(j)

    partCount = j['data']['original']['partCount']
    uploadId = j['data']['original']['uploadId']
    uploadNo = j['data']['uploadNo']
    user.upload_finish(partCount=partCount, uploadId=uploadId, uploadNo=uploadNo)
    time.sleep(2)
    user.publish_article(upload_no=uploadNo, public_status=2, team=False)
    