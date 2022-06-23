import os
import mimetypes
from datetime import datetime as dt
from api.xpcapi import XpcApi, upload_video_part, upload_video


def test_audit_articles():
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