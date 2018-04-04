#!/bin/sh
aws sns subscribe  --topic-arn arn:aws:sns:eu-west-1:161201357662:int-galileo-babel-resources-PublishTopic-ASEPFH7ABVQ2  --protocol lambda --notification-endpoint arn:aws:lambda:eu-west-2:$1:function:$2:$3 --region eu-west-1
