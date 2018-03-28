# Editorial Search - Galileo Babel


This is the lambda function used to put galileo babel notifications into a bucket.

##### Create a aws credentials #####
./fetch-aws-creds.py <aws-account-id>

##### Create virtual environment

```
virtualenv -p /usr/local/bin/python3.6 ~/galileo-babel
source ~/galileo-babel/bin/activate
```

You will need to install the troposhere components:

```yum install libcurl-devel```

```pip install troposphere```

```pip install awacs```

```pip install pytest```

```pip install pycurl```

##### Upload Lambda Function
1. create a bucket to hold the lambda function. e.g```galileo-babel-lambda```. 
2. Execute the script ```deploy.sh``` to build and upload the zip file to the bucket. Make sure to change the name of the bucket.

##### Create the lambda stack

1. Create the stack template for an environment
    
    In the directory  ```<APP_DIRECTORY>/infrastructure/src``` 
    
    Type the following:```python -m babel.devenvironment --lambda-function-bucket <s3-bucket-containing-lambda-function-zipped> --environment <env> --aws-accountId <aws-account-id> --region <aws-region>```

    NOTE: 
    1. When you first run this, if the bucket does not exist it will create one. The name of the bucket created is extactly the same name as the lambda.
    2. When you delete the stack if there is data in the bucket then it will not attempt to delete the bucket.
    3. When you try to create the stack if the bucket already exist then the cloudformation script will not include the bucket creation component.
3. Register Function with Galileo Babel.
    
    Follow the instructions within the following confluence page:
    https://confluence.dev.bbc.co.uk/display/mediatools/Galileo+Babel+User+Guide
   
##### Test the lambda function

To test the lambda function execute the following command: 

    In the directory  ```<APP_DIRECTORY>/infrastructure``` 

```pytest tests/test_galileobabel.py```

Note: Make sure to change the name of the function in  ```setup.cfg```.

#### Development ####
After making changes to the lambda peform the  following operations in order:
1. "deploy.sh" This is used to put new code in to the bucket
2. "update.sh" This is used to update the lambda to use the new code in the bucket

### Versioning ####
Currently the alias always points to the latest version. The details regarding alias, publish and versions still needs to be worked out.


