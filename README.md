# Editorial Search - Galileo Babel

This is the lambda function used to put galileo babel notifications into a bucket.

## Stack template

Located in `./infrastructure/json` and should be generated using the accompanying troposphere script.

## Deployment
To deploy a new version of the lambda to the bucket, run the following:

```
./deploy.sh
./update.sh <environment>
```
### Important note!
Because at some point in the past we've ended up with a test environment named 'testtest', the correct syntax for updating the test environment is:

```
./update.sh testtest
```

## Future work

We plan to remove the legacy scripts below as part of the work on [EDPLAT-675](https://jira.dev.bbc.co.uk/browse/EDPLAT-675). They have been left here for reference, but should not be used in the meantime.

## Legacy (deprecated) scripts

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
    ```python -m babel.environmentbuilder --lambda-function-bucket <s3-bucket-containing-zipped-lambda-function> --env <env> ```

    eg:
    ```python -m babel.environmentbuilder --lambda-function-bucket galileo-babel-lambda --env int ```

    NOTE: 
    1. When you first run this, if the bucket does not exist it will create one. The name of the bucket created is extactly the same name as the lambda.
    2. When you delete the stack if there is data in the bucket then it will not attempt to delete the bucket.
    3. When you try to create the stack if the bucket already exist then the cloudformation script will not include the bucket creation component.
    4. ```config.json``` contains the aws environment configurations used to create the stack
    5. This is the link to the galileo bable documentationp page: https://confluence.dev.bbc.co.uk/display/mediatools/Galileo+Babel+User+Guide

##### Test the lambda function

To test the lambda function execute the following command: 

    In the directory  ```<APP_DIRECTORY>/infrastructure``` 

```pytest tests/test_galileobabel.py```

Note: Make sure to change the name of the function in  ```setup.cfg```.

#### Development ####
After making changes to the lambda peform the  following operations:
1. "deploy.sh" This is used to put new code in to the bucket
2. "update.sh" This is used to update the lambda to use the new code in the bucket


