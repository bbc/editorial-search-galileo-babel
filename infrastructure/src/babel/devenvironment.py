# -*- coding: utf-8 -*-
from troposphere import Template
from babel.common import CreateStack, WormHoleCredentials
from babel.galileobabelstack import GalileoBabelStack
import argparse
import sys
import boto3
from botocore.client import ClientError

class InputParameters:
      
    def parse(self, argv):
        parser = argparse.ArgumentParser(description='Create galileo babel lambda')
        parser.add_argument('--lambda-function-bucket', required=True, dest='lambda_function_bucket', help='Lambda function bucket')
        parser.add_argument('--environment', required=True, dest='lambda_env', help='lambda env')
        parser.add_argument('--aws-accountId', required=True, dest='awsAccountId', help='AWS accountId to create the resources')
        parser.add_argument('--region', required=True, dest='region', help='AWS region')
        args = parser.parse_args(argv)
        return (args.lambda_function_bucket, args.lambda_env, args.awsAccountId, args.region)
            
class BucketUtils:
    
    def __init__(self, wormHoleCredentials, region):
            self.wormHoleCredentials = wormHoleCredentials
            self.region = region
    
    def bucketNotExist(self, bucketName):
        s3 = boto3.resource('s3',self.region,
                                aws_access_key_id=self.wormHoleCredentials['accessKeyId'],
                                aws_secret_access_key=self.wormHoleCredentials['secretAccessKey'],
                                aws_session_token=self.wormHoleCredentials['sessionToken'],)
        try:
            s3.meta.client.head_bucket(Bucket=bucketName)
            return False
        except ClientError as error:
            return True            
    
class DevEnvironment:
    def __init__(self, template, region):
        self.template = template
        self.region = region
                
    def createStack(self, lambda_function_bucket, lambda_env, wormHoleCredentials):
        createStack = CreateStack(lambda_env+"-editorial-search-galileo-babel-stack", 
                                    self.template, self.region, 
                                    lambda_function_bucket, 
                                    lambda_env,
                                    wormHoleCredentials)
            
        if createStack.checkIfStackExist():
            createStack.updateStack()
        else:
            self.stackId = createStack.createStack()
                
def main():
    
    ip = InputParameters()
    params = ip.parse(sys.argv[1:])
    wormCredentials = WormHoleCredentials(params[2])
    wormHoleCredentials = wormCredentials.credentials()
    bucketUtils = BucketUtils(wormHoleCredentials, params[3])
    t = Template(Description=params[0]+" Galileo Bable Stack "+ params[1])
    t.add_version("2010-09-09")
    galileoBabelStack = GalileoBabelStack()

    if (bucketUtils.bucketNotExist(params[1]+"-editorial-search-galileo-babel")):
        print("Bucket does not exist -- addding")
        galileoBabelStack.addBucket(t)
    
    galileoBabelStack.build(t)
    #print(t.to_json())
    devEnvironment = DevEnvironment(t.to_json(), params[3])
    devEnvironment.createStack(params[0], params[1], wormHoleCredentials)
    
if __name__ == '__main__':
      main()
    
    
