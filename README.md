# Editorial Search - Galileo Babel

This is the lambda function used to put galileo babel notifications into a bucket.



##### Create virtual environment

```
virtualenv -p /usr/local/bin/python3.6 ~/galileo-babel
source ~/galileo-babel/bin/activate
```

You will need to install the troposhere components:

 ```pip install troposphere```

```pip install awacs```

```pip install pytest```

##### Upload Lambda Function
1. create a bucket called ```galileo-babel-lambda```. This is the bucket used to hold the lambda
2. Execute the script ```deploy.sh``` to build and upload the zip file to the bucket

##### Create the lambda stack

1. Create aws credentials
    
    In the ```iSite2-Vagrant/scripts``` of your sandbox
    Type the following:```./fetch-aws-creds.py <AWS_ACCOUNT_NUMBER>```
   
2. Create the stack template for an environment
    
    In the directory  ```<APP_DIRECTORY>/infrastructure/src``` 
    
    Type the following:```python -m babel.devenvironment --lambda-function-bucket galileo-babel-lambda --environment <env>```

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
