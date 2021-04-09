from troposphere import Template, Parameter, Sub, GetAtt, Ref
from troposphere.sqs import Queue, QueuePolicy, RedrivePolicy
from awacs.aws import Action, Policy, Allow, Statement, Principal, AWSPrincipal, Condition, ArnLike
from awacs.sqs import SendMessage

t = Template(Description="Stack to test queue connectivity to Galileo")
t.set_version("2010-09-09")

t.add_parameter(Parameter(
    "LambdaEnv",
    Description="The name of the environment.",
    Type="String",
    AllowedValues=["int","test","live"]
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

t.add_resource(Queue(
    "JsonNotificationReceiveQueue",
    QueueName=Sub("${LambdaEnv}-json-notification-inbound-queue"),
    RedrivePolicy=RedrivePolicy(
        deadLetterTargetArn=GetAtt("JsonNotificationDLQ", "Arn"),
        maxReceiveCount=3
    )
))

t.add_resource(Queue(
    "JsonNotificationDLQ",
    QueueName=Sub("${LambdaEnv}-json-notification-inbound-dlq"),
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

print(t.to_json(indent=2))