from troposphere import iam, Template, Parameter, Ref, Sub, Join, GetAtt, Tags
from troposphere.awslambda import Function, Code, Alias, Permission, Environment
from troposphere.iam import Role, PolicyType
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations
from awacs.aws import Action, Policy, Allow, Statement, Principal
from awacs.sts import AssumeRole
from awacs.s3 import ListBucket, GetObject, PutObject

t = Template(Description="Editorial Search Galileo Babel Stack")
t.set_version("2010-09-09")

t.add_parameter(Parameter(
    "LambdaBucket",
    Description="The S3 Bucket that contains the zip to bootstrap your lambda function",
    Type="String",
    Default="galileo-babel-lambda"
))

t.add_parameter(Parameter(
    "LambdaEnv",
    Description="The name of the environment.",
    Type="String",
    AllowedValues=["int","test","live"]
))

t.add_parameter(Parameter(
    "LambdaHandler",
    Description="The name of the function (within your source code) that Lambda calls to start running your code.",
    Type="String",
    Default="galileo-babel-s3.lambda_handler"
))

t.add_parameter(Parameter(
    "LambdaMemorySize",
    Description="The amount of memory, in MB, that is allocated to your Lambda function.",
    Type="Number",
    Default="512"
))

t.add_parameter(Parameter(
    "LambdaTimeout",
    Description="The function execution time (in seconds) after which Lambda terminates the function.",
    Type="Number",
    Default="15"
))

t.add_parameter(Parameter(
    "S3Key",
    Description="The S3 key that references the zip to bootstrap your lambda function.",
    Type="String",
    Default="GalileoBabel.zip"
))

t.add_resource(
    Role(
        "LambdaExecutionRole",
        Policies=[iam.Policy(
            PolicyName = "FunctionRolePolicy",
            PolicyDocument = Policy(
                Statement = [Statement(
                    Effect=Allow,
                    Action=[
                        Action("logs", "CreateLogGroup"),
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

t.add_resource(
    Function(
        "LambdaFunction",
        Code=Code(
            S3Bucket=Ref("LambdaBucket"),
            S3Key=Ref("S3Key")
        ),
        Description="Function used to save galileo babel notifications in a bucket",
        Handler=Ref("LambdaHandler"),
        MemorySize=Ref("LambdaMemorySize"),
        FunctionName=Sub("${LambdaEnv}-editorial-search-galileo-babel"),
        Environment=Environment(Variables={'GALILEO_BABEL_LAMBDA_ENV':Sub("${LambdaEnv}"), 'BUCKET':Sub("${LambdaEnv}-editorial-search-galileo-babel")}),
        Role=GetAtt("LambdaExecutionRole", "Arn"),
        Runtime="python3.6",
        Tags=Tags(BBCProject="editorial-platform",
                BBCComponent="editorial-search-galileo-babel",
                BBCEnvironment=Sub("${LambdaEnv}")),
        Timeout=Ref("LambdaTimeout")
    )
)

t.add_resource(PolicyType(
    "FunctionPolicy",
    PolicyName="FunctionPolicy",
    Roles=[Ref("LambdaExecutionRole")],
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

t.add_resource(Alias(
    "GalileoBabelLambdaAlias",
    Description="Alias for the galileo babel lambda",
    FunctionName=Ref("LambdaFunction"),
    FunctionVersion="$LATEST",
    Name=Ref("LambdaEnv")
))

t.add_resource(Bucket(
    "NotificationsToBeIngested", 
    BucketName= Sub("${LambdaEnv}-editorial-search-galileo-babel"),
    DeletionPolicy="Retain",
    NotificationConfiguration=NotificationConfiguration(
        TopicConfigurations=[
            TopicConfigurations(
                Event="s3:ObjectCreated:*",
                Topic=Ref("BucketNotificationTopicArn")
            ),
            TopicConfigurations(
                Event="s3:ObjectRemoved:*",
                Topic=Ref("BucketNotificationTopicArn")
            )
        ]
    )
))

print(t.to_json(indent=2))