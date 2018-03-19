from __future__ import print_function
import json
import os
import boto3
import io
from io import StringIO
import datetime
import uuid

client = boto3.client('s3')
bucket = os.environ['BUCKET']

def lambda_handler(event, context):
    
    io = StringIO()
    json.dump(event, io)
    ts = datetime.datetime.now().isoformat()
    key = ts.split("T")[0]+"/"+ts.split("T")[1].split(".")[0].replace(":","")
    pid = event["programme"]["pid"]
    client.put_object(Body=io.getvalue(), Bucket=bucket, Key=key+"_"+str(uuid.uuid4())+"_"+pid)
