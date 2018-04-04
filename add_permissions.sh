#!/bin/sh
aws lambda add-permission --function-name int-editorial-search-galileo-babel --statement-id galileoBabelInt --action "lambda:InvokeFunction" --principal sns.amazonaws.com --source-arn arn:aws:sns:eu-west-1:161201357662:int-galileo-babel-resources-PublishTopic-ASEPFH7ABVQ2 --qualifier int
