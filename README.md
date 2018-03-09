# Editorial Search - Galileo Babel

This is the lambda function used to put galileo babel notifications into a bucket.

#### Install Python 3.6

If you do not have python 3.6 installed on your sandbox follow the instructions below.

```
wget http://python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
tar xf Python-3.6.3.tar.xz
./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
make && make altinstall
```
If you get the following error:
```
ln: creating hard link `libpython3.6m.so' => `libpython3.6m.so.1.0': Operation not permitted
```

Then change line 610 of the ```Makefile```

From ```$(LN) -f $(INSTSONAME) $@; \```  to  ```$(LN) -fs $(INSTSONAME) $@; \```


##### Create virtual environment

```
virtualenv -p /usr/local/bin/python3.6 ~/galileo-babel
source ~/galileo-babel/bin/activate
```

You will need to install the troposhere components:

 ```pip install troposphere```

```pip install awacs```

##### Upload Lambda Function
1. create a bucket called ```galileo-babel-lambda```
2. Execute the script ```deploy.sh``` to build and upload the zip file to the bucket

##### Create the lamba stack

1. Create aws credentials
    
    In the ```iSite2-Vagrant/scripts``` of your sandbox
    Type the following:```./fetch-aws-creds.py <AWS_ACCOUNT_NUMBER>```
   
2. Create the stack template for an environment
    
    In the directory  ```<APP_DIRECTORY>/infrastructure``` 
    
    Type the following:```python -m babel.devenvironment --lambda-function-bucket galileo-babel-lambda --environment <env>```

3. Register Function with Galileo Babel.
    
    Follow the instructions within the following confluence page:
    https://confluence.dev.bbc.co.uk/display/mediatools/Galileo+Babel+User+Guide
   
##### Test the lambda function

To test the lambda function execute the following script ```test-lambda.sh```

Note: Make sure to change the name of the function.
