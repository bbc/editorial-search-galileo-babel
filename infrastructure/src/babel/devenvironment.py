# -*- coding: utf-8 -*-
from troposphere import Template
from babel.common import CreateStack
from babel.galileobabelstack import GalileoBabelStack
import argparse
import sys


class InputParameters:
      
    def parse(self, argv):
        parser = argparse.ArgumentParser(description='Create galileo babel lambda')
        parser.add_argument('--lambda-function-bucket', required=True, dest='lambda_function_bucket', help='Lambda function bucket')
        parser.add_argument('--environment', required=True, dest='lambda_env', help='lambda env')
        args = parser.parse_args(argv)
        return (args.lambda_function_bucket, args.lambda_env)
            
    
class DevEnvironment:
    def __init__(self, template):
        self.template = template
                
    def createStack(self, lambda_function_bucket, lambda_env):
        createStack = CreateStack(lambda_env+"-editorial-search-galileo-babel-stack", self.template, "eu-west-2", lambda_function_bucket, lambda_env)
            
        if createStack.checkIfStackExist():
            createStack.updateStack()
        else:
            self.stackId = createStack.createStack()
                
def main():
    
    ip = InputParameters()
    params = ip.parse(sys.argv[1:])

    t = Template(Description=params[0]+" Galileo Bable Stack "+ params[1])
    t.add_version("2010-09-09")
    galileoBabelStack = GalileoBabelStack()
    galileoBabelStack.build(t)
    
    #print(t.to_json())
    devEnvironment = DevEnvironment(t.to_json())
    devEnvironment.createStack(params[0], params[1])
    
if __name__ == '__main__':
      main()
    
    
