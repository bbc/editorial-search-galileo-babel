# -*- coding: utf-8 -*-
from troposphere import Template
from babel.common import CreateStack, WormHoleCredentials
from babel.galileobabelstack import GalileoBabelStack
import argparse
import sys
import boto3
from botocore.client import ClientError

class InputParameters(object):
      
    def parse(self, argv):
        parser = argparse.ArgumentParser(description='Create galileo babel lambda')
        parser.add_argument('--lambda-function-bucket', required=True, dest='lambda_function_bucket', help='Lambda function bucket')
        parser.add_argument('--environment', required=True, dest='lambda_env', help='lambda env')
        parser.add_argument('--aws-accountId', required=True, dest='awsAccountId', help='AWS accountId to create the resources')
        parser.add_argument('--region', required=True, dest='region', help='AWS region')
        parser.add_argument('--galileo-accountId', required=True, dest='gallileo_accountId', help='Galilio Babel AccountId')
        parser.add_argument('--galileo-region', required=True, dest='galileo_region', help='Galileo Region')
        parser.add_argument('--galileo-topic', required=True, dest='galileo_topic', help='Galileo Topic')
        args = parser.parse_args(argv)
        return (args.lambda_function_bucket, 
                args.lambda_env, 
                args.awsAccountId, 
                args.region,
                args.gallileo_accountId,
                args.galileo_region,
                args.galileo_topic,)
            
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
    

class GalileoPermisionAndSubscription(object):

        def __init__(self, accountId, topic, region, wormHoleCredentials):
            self.accountId = accountId
            self.topic = topic
            self.region = region
            self.wormCredentials = wormCredentials

        def add_permisions(self, env, region, accountId):
            print("-----------")
            client = boto3.client('lambda',region_name=region,
                                aws_access_key_id=self.wormHoleCredentials['accessKeyId'],
                                aws_secret_access_key=self.wormHoleCredentials['secretAccessKey'],
                                aws_session_token=self.wormHoleCredentials['sessionToken'])

            response = client.add_permission(
                FunctionName='arn:aws:lambda:'+region+':'+accountId+':function:'+str(env)+'-editorial-search-galileo-babel:'+str(env),
                StatementId='galilioBabel'+str(env),
                Action='lambda:InvokeFunction',
                #Principal=str(self.accountId), NOTE: BOTO3 says this should be the accountId
                Principal='sns.amazonaws.com',
                SourceArn='arn:aws:sns:'+str(self.region)+':'+str(self.accountId)+':'+str(self.topic),
                Qualifier=str(env))
            
            print("Add permssion response["+str(response)+']')

        def subscribe_to_topic(self, region, accountId, env):
            client = boto3.client('sns',region_name=self.region,
                                aws_access_key_id=self.wormHoleCredentials['accessKeyId'],
                                aws_secret_access_key=self.wormHoleCredentials['secretAccessKey'],
                                aws_session_token=self.wormHoleCredentials['sessionToken'])
            
            response = client.subscribe(
                        TopicArn='arn:aws:sns:'+self.region+':'+self.accountId+':'+self.topic,
                        Protocol='lambda',
                        Endpoint='arn:aws:lambda:'+region+':'+accountId+':function:'+env+'-editorial-search-galileo-babel:'+env)
            
            print("subscription response["+str(response)+']')

class EnvironmentBuilder(object):
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
    awsAccountId = params[2]
    wormCredentials = WormHoleCredentials(awsAccountId)
    wormHoleCredentials = wormCredentials.credentials()

    region = params[3]
    bucketUtils = BucketUtils(wormHoleCredentials, region)
    environment = params[1]
    t = Template(Description=params[0]+" Galileo Bable Stack "+ environment)
    t.add_version("2010-09-09")
    galileoBabelStack = GalileoBabelStack()

    if (bucketUtils.bucketNotExist(environment+"-editorial-search-galileo-babel")):
        print("Bucket does not exist -- addding")
        galileoBabelStack.addBucket(t)
    
    galileoBabelStack.build(t)
    #print(t.to_json())
    environmentBuilder = EnvironmentBuilder(t.to_json(), region)
    lambdaBucket = params[0]
    environmentBuilder.createStack(lambdaBucket, environment, wormHoleCredentials)

    galileoAccountId = params[4]
    galileoRegion = params[5]
    galileoTopic = params[6]
    galileoPermisionAndSubscription = GalileoPermisionAndSubscription(galileoAccountId, 
                                                                      galileoTopic, 
                                                                      galileoRegion, 
                                                                      wormHoleCredentials)
    #galileoPermisionAndSubscription.add_permisions(environment, region, awsAccountId)
    galileoPermisionAndSubscription.subscribe_to_topic(region, awsAccountId, environment)
    
if __name__ == '__main__':
      main()
    
    