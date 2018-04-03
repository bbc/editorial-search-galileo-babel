#!/bin/sh
aws lambda add-permission --function-name $1 --statement-id galileoBabel --action "lambda:InvokeFunction" --principal sns.amazonaws.com --source-arn arn:aws:sns:eu-west-1:161201357662:int-galileo-babel-resources-PublishTopic-ASEPFH7ABVQ2 
