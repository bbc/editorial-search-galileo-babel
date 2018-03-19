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
            json.dump(data, io)

            response = aws_lambda.invoke(
                FunctionName=resource,
                    InvocationType='RequestResponse',
                    LogType='Tail',
                    Payload=io.getvalue().encode()
             )    
            time.sleep(0.05)

        time.sleep(15.0)
        size = sum(1 for _ in bucket.objects.all())
        assert size  == 10
