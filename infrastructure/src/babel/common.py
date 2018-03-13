# -*- coding: utf-8 -*-
import boto3
import botocore
                
class CreateStack:
    
    def __init__(self, stackName, template,region, lambdaFunctionBucket, lambda_env):
        self.capabilities = ['CAPABILITY_NAMED_IAM']
        self.template = template
        self.stackName = stackName
        self.lambdaFunctionBucket = lambdaFunctionBucket
        self.lambda_env = lambda_env
        self.region = region
        self.parameters = [{
                                'ParameterKey': 'LambdaBucket',
                                'ParameterValue': self.lambdaFunctionBucket
                            },{
                                'ParameterKey': 'S3Key',
                                'ParameterValue': "GalileoBabel.zip"
                            },{
                                'ParameterKey': 'LambdaHandler',
                                'ParameterValue': "galileo_babel_s3.lambda_handler"
                            },{
                                'ParameterKey': 'LambdaMemorySize',
                                'ParameterValue': "512"
                            },{
                                'ParameterKey': 'LambdaTimeout',
                                'ParameterValue': "15"
                            },{
                                'ParameterKey': 'LambdaEnv',
                                'ParameterValue': self.lambda_env
                         }]
    
    def checkIfStackExist(self):
        client = boto3.client('cloudformation', region_name=self.region)

        try:
            response = client.describe_stacks(StackName=self.stackName)
            return True
        
        except botocore.exceptions.ClientError as ce:
            return False
        
    def createStack(self):
        client = boto3.client('cloudformation', region_name=self.region)
        try:
            response = client.create_stack(
                        StackName=self.stackName,
                        TemplateBody=self.template,
                        Parameters= self.parameters,
                        Capabilities= self.capabilities,
                        OnFailure='ROLLBACK'
                    )
            self.stackId = response['StackId']
            print("waiting for stack_create_complete [" + self.stackId +"]")
            waiter = client.get_waiter('stack_create_complete')
            waiter.wait(StackName=self.stackId)
            print("stack creation completed")
            
        except botocore.exceptions.ClientError as e:
            print(str(e))
            return None
        except botocore.exceptions.WaiterError as e:
            response = client.describe_stacks(StackName=stackId)
            print(str(response))
            return None
        
        return self.stackId
    
    def updateStack(self):
        client = boto3.client('cloudformation', region_name=self.region)
        try:
            response = client.update_stack(
                    StackName=self.stackName,
                    StackPolicyDuringUpdateBody=self.template,
                    UsePreviousTemplate=True,
                    Parameters = self.parameters,
                    Capabilities= self.capabilities
                    )
            self.stackId = response['StackId']
            print("waiting for stack_update_complete [" + self.stackId + "]")
            waiter = client.get_waiter('stack_update_complete')
            waiter.wait(StackName=self.stackId)
            print("stack update completed")

        except botocore.exceptions.ClientError as e:
            error = str(e)
            # based on comments from here https://github.com/hashicorp/terraform/issues/5653
            if error.find('No updates are to be performed') != -1:
                print("Nothing to update")
            else:
                print("something went wrong")
                print(error)
            return None
        except botocore.exceptions.WaiterError as e:
            response = client.describe_stacks(StackName=stackId)
            print(str(response))
            return None
        
        return self.stackId