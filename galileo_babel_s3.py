from __future__ import print_function
import json
import os
import boto3
import io
from io import StringIO


print('Loading function')

client = boto3.client('s3')

bucket = os.environ['BUCKET']
print('BUCKET '+bucket)

def lambda_handler(event, context):
    
    io = StringIO()
    json.dump(event, io)
    pid = event['programme']['pid']
    print("this is the pid [" + pid+"]")
    client.put_object(Body=io.getvalue(), Bucket=bucket, Key=pid)
