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
        bucket = s3.Bucket(resource)
        bucket.objects.all().delete()

        onetoten = range(1,11)
        for count in onetoten:
            io = StringIO()
            iter(data).next()['testFileName'] = 'TEST/'+count
            json.dump(data, io)

            response = aws_lambda.invoke(
                FunctionName=resource,
                    InvocationType='RequestResponse',
                    LogType='Tail',
                    Payload=io.getvalue().encode()
             )    
            time.sleep(0.05)

        time.sleep(15.0)
        kwargs = {'Bucket': resource, 'Delimiter': "Test/"}
        resp = s3.list_objects_v2(**kwargs)
        size = sum(1 for _ in resp['Contents'].all())
        assert size  == 10
