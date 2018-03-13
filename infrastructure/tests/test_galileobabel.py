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
        pid = data['programme']['pid']
    
        onetoten = range(1,11)

        #First delete previous
        for count in onetoten:
            key = pid + str(count)
            s3.delete_object(Bucket=resource, Key= key)

        for count in onetoten:
            data['programme']['pid'] = pid + str(count)
            io = StringIO()
            json.dump(data, io)

            response = aws_lambda.invoke(
                FunctionName=resource,
                    InvocationType='RequestResponse',
                    LogType='Tail',
                    Payload=io.getvalue().encode()
             )    

        time.sleep(5.0)
        for count in onetoten:
            key = pid + str(count)
            try:
                obj = s3.get_object(Bucket=resource,Key=key)
                content = obj['Body'].read().decode('utf-8')
                actual = json.loads(content)
                assert key  == actual['programme']['pid']
            except s3.exceptions.NoSuchKey:
                 print("something when wrong [" + key +"]")
                 raise    