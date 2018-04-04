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

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.info("checking for new code deployement")
    io = StringIO()
    json.dump(event, io)

    pid = event["MessageId"]
    if 'testFileName' in event:
        key = event['testFileName']
    else:
        ts = datetime.datetime.now().isoformat()
        key = ts.split("T")[0]+"/"+ts.split("T")[1].split(".")[0].replace(":","")+"_"+pid
    
    client.put_object(Body=io.getvalue(), Bucket=bucket, Key=key)
