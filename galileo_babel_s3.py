from __future__ import print_function
import json, os, boto3, io, datetime, uuid, logging
from io import StringIO

client = boto3.client('s3')
bucket = os.environ['BUCKET']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_pid_from_message_content(body):
    content = json.loads(body["Message"])
    return content["programme"]["pid"]

def lambda_handler(event, context):

    logger.info("Received: {}".format(json.dumps(event)))

    if "Sns" in event["Records"][0]:
        logger.error('Unsupported event source: sns')
    elif 'testFileName' in event:
        client.put_object(
            Body='', 
            Bucket=bucket, 
            Key=event['testFileName']
        )
    else:
        body = json.loads(event["Records"][0]["body"])
        pid = get_pid_from_message_content(body)
        ts = datetime.datetime.now().isoformat()
        key = ts.split("T")[0]+"/"+ts.split("T")[1].split(".")[0].replace(":","")+"_clip_"+pid
        client.put_object(
            Body=json.dumps(body, indent=2), 
            Bucket=bucket, 
            Key=key
        )