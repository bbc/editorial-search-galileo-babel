from __future__ import print_function
import json, os, boto3, io, datetime, uuid, logging
from io import StringIO

client = boto3.client('s3')
bucket = os.environ['BUCKET']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    if 'testFileName' in event:
        client.put_object(Body="", Bucket=bucket, Key=event['testFileName'])

    else if "Type" in event and event["Type"] == "Notification":
        logger.info("checking for new code deployment["+str(event)+"]")
        io = StringIO()
        json.dump(event, io)
        messageId = event["MessageId"]

        ts = datetime.datetime.now().isoformat()
        key = ts.split("T")[0]+"/"+ts.split("T")[1].split(".")[0].replace(":","")+"_"+messageId
        client.put_object(Body=io.getvalue(), Bucket=bucket, Key=key)

    else if "Records" in event and "Sns" in event["Records"][0]:
        logger.warn("Call from deprecated trigger: SNS - the subscription should be disabled")
