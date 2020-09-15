from troposphere import iam, Template, Parameter, Ref, Sub, Join, GetAtt, Tags, ImportValue, Equals, If
from troposphere.awslambda import Function, Code, Alias, Permission, Environment
from troposphere.iam import Role, PolicyType
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations
from troposphere.sqs import Queue, QueuePolicy, RedrivePolicy
from awacs.aws import Action, Policy, Allow, Statement, Principal, AWSPrincipal, Condition, ArnLike
from awacs.sts import AssumeRole
from awacs.s3 import ListBucket, GetObject, PutObject
from awacs.sqs import SendMessage

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

t.add_parameter(Parameter(
    "GalileoBabelTopicArn",
    Description="The arn of the Galileo Babel topic that should trigger the lambda",
    Type="String",
    AllowedValues=[
        "arn:aws:sns:eu-west-1:161201357662:int-galileo-babel-resources-PublishTopic-ASEPFH7ABVQ2",
        "arn:aws:sns:eu-west-1:161201357662:test-galileo-babel-resources-PublishTopic-1JLISD0OVHPNZ",
        "arn:aws:sns:eu-west-1:816201991468:live-galileo-babel-resources-PublishTopic-15KDT1FKBRA4M"
    ]
))

t.add_parameter(Parameter(
    "TestAccountTopicArn",
    Description="The arn of the topic in the 'test' account. Only required for live environment.",
    Type="String",
    Default="arn:aws:sns:eu-west-2:195048873603:test-editorial-search-app-JsonMessageTopic-KPL25WOSM3VC"
))

t.add_condition("IsInt", Equals(Ref("LambdaEnv"), "int"))
t.add_condition("IsTest", Equals(Ref("LambdaEnv"), "test"))
t.add_condition("IsLive", Equals(Ref("LambdaEnv"), "live"))

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
        FunctionName=If("IsTest", "testtest-editorial-search-galileo-babel", Sub("${LambdaEnv}-editorial-search-galileo-babel")),
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
    PolicyDocument=Policy(
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

t.add_resource(Permission(
    "InvokeLambdaPermission",
    FunctionName=Join(':',[GetAtt("LambdaFunction", "Arn"), Ref("LambdaEnv")]),
    Action="lambda:InvokeFunction",
    SourceArn=Ref("GalileoBabelTopicArn"),
    Principal="sns.amazonaws.com"
))

t.add_resource(Alias(
    "GalileoBabelLambdaAlias",
    Description="Alias for the galileo babel lambda",
    FunctionName=Ref("LambdaFunction"),
    FunctionVersion="$LATEST",
    Name=Ref("LambdaEnv")
))

t.add_resource(Queue(
    "JsonNotificationReceiveQueue",
    QueueName=Sub("${LambdaEnv}-json-notification-receive-queue"),
    RedrivePolicy=RedrivePolicy(
        deadLetterTargetArn=GetAtt("JsonNotificationDLQ", "Arn"),
        maxReceiveCount=3
    )
))

t.add_resource(Queue(
    "JsonNotificationDLQ",
    QueueName=Sub("${LambdaEnv}-json-notification-receive-dlq"),
))

t.add_resource(QueuePolicy(
    "JsonNotificationReceiveQueuePolicy",
    Queues=[Ref("JsonNotificationReceiveQueue")],
    PolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[SendMessage],
                Resource=[GetAtt("JsonNotificationReceiveQueue", "Arn")],
                Principal=AWSPrincipal("*"),
                Condition=Condition([
                    ArnLike("aws:SourceArn", Ref("GalileoBabelTopicArn"))
                ])
            )
        ]
    )
))

t.add_resource(Bucket(
    "NotificationsToBeIngested", 
    BucketName= Sub("${LambdaEnv}-editorial-search-galileo-babel"),
    DeletionPolicy="Retain",
    NotificationConfiguration=NotificationConfiguration(
        TopicConfigurations=If("IsLive", [
            # live - notify live and test
            TopicConfigurations(
                Event="s3:ObjectCreated:*",
                Topic=ImportValue(Sub("${LambdaEnv}-JsonTopicArn"))
            ),
            TopicConfigurations(
                Event="s3:ObjectRemoved:*",
                Topic=ImportValue(Sub("${LambdaEnv}-JsonTopicArn"))
            ),
            TopicConfigurations(
                Event="s3:ObjectCreated:*",
                Topic=Ref("TestAccountTopicArn")
            ),
            TopicConfigurations(
                Event="s3:ObjectRemoved:*",
                Topic=Ref("TestAccountTopicArn")
            )
        ],  
            If("IsInt", [
                # int - notify int
                TopicConfigurations(
                    Event="s3:ObjectCreated:*",
                    Topic=ImportValue(Sub("${LambdaEnv}-JsonTopicArn"))
                ),
                TopicConfigurations(
                    Event="s3:ObjectRemoved:*",
                    Topic=ImportValue(Sub("${LambdaEnv}-JsonTopicArn"))
                )
            ], [
                # test - no notifications
            ])
        )
    )
))

print(t.to_json(indent=2))