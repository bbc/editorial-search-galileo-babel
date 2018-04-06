from troposphere import Template,Ref,Parameter,Sub,GetAtt,Join, Tags
from troposphere.s3 import Rules as S3Key,Bucket,LifecycleConfiguration,LifecycleRule
from troposphere.awslambda import Function, Code, Alias, Permission, Environment
import awacs
from troposphere.iam import Role, PolicyType
from awacs.aws import Action,Allow,Condition,Policy,PolicyDocument,Principal,Statement,Condition
from awacs.sts import AssumeRole
from awacs.s3 import ListBucket,GetObject,PutObject
from troposphere import iam

class GalileoBabelStack(object):
    def __init__(self):
        pass

    def addBucket(self, template):
        template.add_resource(Bucket(
                    "NotificationsToBeIngested", 
                    BucketName= Sub("${LambdaEnv}-editorial-search-galileo-babel"),
                    DeletionPolicy="Retain"
        ))
        

    def add_permisions(self, template, aws_lambda, galileoAccountId, galileoTopic, galileoRegion):
            galileoBabelTopic = "arn:aws:sns:"+galileoRegion+":"+galileoAccountId+":"+galileoTopic
            print("gallioe babel topic ["+galileoBabelTopic+"]")
            template.add_resource(Permission(
                "InvokeLambdaPermission",
                FunctionName=GetAtt(aws_lambda, "Arn"),
                Action="lambda:InvokeFunction",
                SourceArn = galileoBabelTopic,
                Principal= galileoAccountId
            ))
   
    def build(self, template):
        
        lambda_bucket = template.add_parameter(Parameter(
            "LambdaBucket",
            Type="String",
            Default="galileo-babel-lambda",
            Description="The S3 Bucket that contains the zip to bootstrap your "
                "lambda function"
        ))

        s3_key = template.add_parameter(Parameter(
            "S3Key",
            Type="String",
            Default="GalileoBabel.zip",
            Description="The S3 key that references the zip to bootstrap your "
                "lambda function"
        ))

        handler = template.add_parameter(Parameter(
            "LambdaHandler",
            Type="String",
            Default="galileo-babel-s3.lambda_handler",
            Description="The name of the function (within your source code) "
                "that Lambda calls to start running your code."
        ))

        memory_size = template.add_parameter(Parameter(
            "LambdaMemorySize",
            Type="Number",
            Default="512",
            Description="The amount of memory, in MB, that is allocated to "
                "your Lambda function."
        ))

        timeout = template.add_parameter(Parameter(
            "LambdaTimeout",
            Type="Number",
            Default="15",
            Description="The function execution time (in seconds) after which "
                "Lambda terminates the function. "
        ))

        env = template.add_parameter(Parameter(
            "LambdaEnv",
            AllowedValues=["int", "test", "live", "dev"],
            Default="int",
            Description="Environment this lambda represents - used for alias name",
            Type="String",
        ))

        function_role = template.add_resource(
            Role(
                "LambdaExecutionRole",
                Policies=[iam.Policy(
                    PolicyName = "FunctionRolePolicy",
                    PolicyDocument = Policy(
                        Statement = [ 
                            Statement(
                                Effect=Allow,
                                Action = [ Action("logs", "CreateLogGroup"),
                                    Action("logs", "CreateLogStream"),
                                    Action("logs", "PutLogEvents"),
                                ],
                                Resource = ["arn:aws:logs:*:*:*"]
                            )]
                ))],
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["lambda.amazonaws.com"]
                            )
                        )
                    ]
                )
            )

        )

        aws_lambda = template.add_resource(
            Function(
                "LambdaFunction",
                Code=Code(
                    S3Bucket=Ref(lambda_bucket),
                    S3Key=Ref(s3_key)
                ),
                Description="Function used to save galileo babel notifications in a bucket",
                Handler=Ref(handler),
                MemorySize=Ref(memory_size),
                FunctionName=Sub("${LambdaEnv}-editorial-search-galileo-babel"),
                Environment = Environment(Variables= {'GALILEO_BABEL_LAMBDA_ENV':Sub("${LambdaEnv}"), 'BUCKET':Sub("${LambdaEnv}-editorial-search-galileo-babel")}),
                Role=GetAtt(function_role, "Arn"),
                Runtime="python3.6",
                Tags =Tags(BBCProject="editorial-platform",
                        BBCComponent="editorial-search-galileo-babel",
                        BBCEnvironment=Sub("${LambdaEnv}")),
                Timeout=Ref(timeout)
            )
        )

                    
        template.add_resource(PolicyType(
            "FunctionPolicy",
            PolicyName="FunctionPolicy",
            Roles=[Ref(function_role)],
            PolicyDocument= Policy(
                Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[ListBucket],
                        Resource=[Join("",["arn:aws:s3:::",Sub("${LambdaEnv}"),"-editorial-search-galileo-babel"])]
                    ),
                    Statement(
                        Effect=Allow,
                        Action=[GetObject,PutObject],
                        Resource=[Join("/", [Join("",["arn:aws:s3:::",Sub("${LambdaEnv}"),"-editorial-search-galileo-babel"]),"*"])],
                    )
                ]
            
            )
        ))

        template.add_resource(Alias(
            "GalileoBabelLambdaAlias",
            Description="Alias for the galileo babel lambda",
            FunctionName=Ref(aws_lambda),
            FunctionVersion="$LATEST",
            Name=Ref(env)
        ))

        return aws_lambda