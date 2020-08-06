# -*- coding: utf-8 -*-
import boto3
import botocore
import json
import io
from io import StringIO
import sys
import argparse
import time

class TestGalileoBabel(object):

    def test_lambda(self, resource, data, aws_lambda, s3):
        
        # Delete all items within the bucket
        objects_to_delete = s3.meta.client.list_objects_v2(Bucket=resource, Delimiter="/", Prefix="TEST/")

        delete_keys = {'Objects' : [{}]}
        if 'Contents' in objects_to_delete:
            delete_keys['Objects'] = [{'Key' : k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents')]]
            s3.meta.client.delete_objects(Bucket=resource, Delete=delete_keys)
        
        onetoten = range(1,11)
        for count in onetoten:
            io = StringIO()
            fileName = 'TEST/' + str(count)
            data.update({'testFileName':fileName})
            json.dump(data, io)

            response = aws_lambda.invoke(
                FunctionName=resource,
                    InvocationType='RequestResponse',
                    LogType='Tail',
                    Payload=io.getvalue().encode()
             )    
            time.sleep(0.05)

        time.sleep(15.0)
        resp = s3.meta.client.list_objects_v2(Bucket=resource, Delimiter= "/", Prefix="TEST/")
        size = len(resp.get('Contents'))
        delete_keys['Objects'] = [{'Key' : k} for k in [obj['Key'] for obj in resp.get('Contents')]]
        s3.meta.client.delete_objects(Bucket=resource, Delete=delete_keys)
        assert size  == 10
