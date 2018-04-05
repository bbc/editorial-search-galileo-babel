# Editorial Search - Galileo Babel

This is the lambda function used to put galileo babel notifications into a bucket.

##### Fetch aws credentials #####
fetch-aws-creds 195048873603

##### Create virtual environment

```
sudo yum install python34-devel libcurl-devel
sudo pip3.4 install virtualenv
python3.4 -m virtualenv ~/galileo-babel
source ~/galileo-babel/bin/activate
```

You will need to install troposhere and some other Python packages:

```pip install troposphere```

```pip install awacs```

```pip install pytest```

```pip install pycurl```

```pip install boto3```

##### Upload Lambda Function
1. create a bucket to hold the lambda function. e.g```galileo-babel-lambda```. 
2. Execute the script ```deploy.sh``` to build and upload the zip file to the bucket

##### Create the lambda stack

1. Create the stack template for an environment
    
    In the directory  ```<APP_DIRECTORY>/infrastructure/src``` 
    
    Type the following:
    ```python -m babel.environmentbuilder --lambda-function-bucket <s3-bucket-containing-zipped-lambda-function> --environment <env> --aws-accountId <aws account id> --region <aws region> --galileo-accountId <galileo accountId> --galileo-region <galileo region> --galileo-topic <galileo topic>```

    eg:
    ```python -m babel.environmentbuilder --lambda-function-bucket galileo-babel-lambda --environment int --aws-accountId 195048873603 --region eu-west-2 --galileo-accountId 161201357662 --galileo-region eu-west-1 --galileo-topic int-galileo-babel-resources-PublishTopic-ASEPFH7ABVQ2```

    NOTE: 
    1. When you first run this, if the bucket does not exist it will create one. The name of the bucket created is extactly the same name as the lambda.
    2. When you delete the stack if there is data in the bucket then it will not attempt to delete the bucket.
    3. When you try to create the stack if the bucket already exist then the cloudformation script will not include the bucket creation component.

##### Test the lambda function

To test the lambda function execute the following command: 

    In the directory  ```<APP_DIRECTORY>/infrastructure``` 

```pytest tests/test_galileobabel.py```

Note: Make sure to change the name of the function in  ```setup.cfg```.

#### Development ####
After making changes to the lambda peform the  following operations:
1. "deploy.sh" This is used to put new code in to the bucket
2. "update.sh" This is used to update the lambda to use the new code in the bucket


