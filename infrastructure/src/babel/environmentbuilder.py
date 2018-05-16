# -*- coding: utf-8 -*-
from troposphere import Template
from babel.common import CreateStack, WormHoleCredentials
from babel.galileobabelstack import GalileoBabelStack
import argparse
import sys
import boto3
import botocore
from botocore.client import ClientError
import json
from pprint import pprint
import os


class Config(object):

    def __init__(self, awsAccountId, awsRegion, babelAccountId, babelRegion, babelTopic):
        self.awsAccountId = awsAccountId
        self.awsRegion = awsRegion
        self.babelAccountId = babelAccountId
        self.babelRegion = babelRegion
        self.babelTopic = babelTopic

class ConfigParser(object):
    
    def __init__(self):
        cwd = os.getcwd()
        with open('babel/config.json') as f:
            self.config = json.load(f)
        
    def getConfig(self, env):
        try:
            envOfInterest = self.config[env]
            return self._create_config(env)
        except KeyError as e:
            return self._create_config("int")

    def _create_config(self, env):
        return Config(self.config[env]["awsAccountId"],
            self.config[env]["awsRegion"],
            self.config[env]["galileoBabel"]["awsAccountId"],
            self.config[env]["galileoBabel"]["awsRegion"],
            self.config[env]["galileoBabel"]["topic"])
               

class InputParameters(object):
      
    def parse(self, argv):
        parser = argparse.ArgumentParser(description='Create galileo babel lambda')
        parser.add_argument('--env', required=True, dest='lambda_env', help='lambda env')
        parser.add_argument('--lambda-function-bucket', required=True, dest='lambda_bucket', help='lambda env')
        args = parser.parse_args(argv)
        return (args.lambda_env, args.lambda_bucket)
            
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
    

class GalileoSubscription(object):

        def __init__(self, accountId, topicArn, region, wormHoleCredentials, stackCreator):
            self.accountId = accountId
            self.topicArn = topicArn
            self.region = region
            self.wormHoleCredentials = wormHoleCredentials
            self.createStack = stackCreator

        def subscribe_to_topic(self, region, accountId, env):
                client = boto3.client('sns',region_name=self.region,
                                aws_access_key_id=self.wormHoleCredentials['accessKeyId'],
                                aws_secret_access_key=self.wormHoleCredentials['secretAccessKey'],
                                aws_session_token=self.wormHoleCredentials['sessionToken'])
            
                try:
                    response = client.subscribe(
                            TopicArn=self.topicArn,
                            Protocol='lambda',
                            Endpoint='arn:aws:lambda:'+region+':'+accountId+':function:'+env+'-editorial-search-galileo-babel:'+env)
            
                    print("subscription response["+str(response)+']')
                except ClientError as e:
                    print("subscription already exists ["+str(e)+"]")


class EnvironmentBuilder(object):
    def __init__(self, stackCreator):
        self.createStack = stackCreator
                
    def buildEnvironment(self):   
        print(" calling create stack")        
        if self.createStack.checkIfStackExist():
            self.createStack.updateStack()
        else:
            self.stackId = self.createStack.createStack()
                
def main():
    
    ip = InputParameters()
    params = ip.parse(sys.argv[1:])

    configParser = ConfigParser()
    config = configParser.getConfig(params[0])
    
    wormCredentials = WormHoleCredentials(config.awsAccountId)
    wormHoleCredentials = wormCredentials.credentials()

    bucketUtils = BucketUtils(wormHoleCredentials, config.awsRegion)
    t = Template(Description=params[0]+" Galileo Babel Stack ")
    t.add_version("2010-09-09")
    galileoBabelStack = GalileoBabelStack()

    if (bucketUtils.bucketNotExist(params[0]+"-editorial-search-galileo-babel")):
        print("Bucket does not exist -- addding")
        galileoBabelStack.addBucket(t)
    
    lambdaBucket = params[1]
    aws_lambda = galileoBabelStack.build(t)
    galileoBabelStack.add_permissions(t, aws_lambda, config.babelTopic, params[0])
    
    stackCreator = CreateStack(params[0]+"-editorial-search-galileo-babel-stack", 
                                t.to_json(), 
                                config.awsRegion, 
                                lambdaBucket, 
                                params[0],
                                wormHoleCredentials)
    galileoSubscription = GalileoSubscription(config.babelAccountId, 
                                                                      config.babelTopic, 
                                                                      config.babelRegion, 
                                                                      wormHoleCredentials,
                                                                      stackCreator)
    environmentBuilder = EnvironmentBuilder(stackCreator)
    environmentBuilder.buildEnvironment()
    galileoSubscription.subscribe_to_topic(config.awsRegion, config.awsAccountId, params[0])
    
if __name__ == '__main__':
      main()
    
    
