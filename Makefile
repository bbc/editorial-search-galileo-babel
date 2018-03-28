.PHONY: release build

# PLEASE CHANGE THE COMPONENT NAME
COMPONENT="EDITORIAL-SEARCH-GALILEO-BABEL"

clean:
	rm -rf GalileoBabel.zip 

# Note: we remove the boto3 and botocore folders because they're provided by
# default by the AWS lambda environment

# Installing python-virtualenv won't work for CentOS7 - it's broken for python3
# So, we install it from pip3, for which there isn't an RPM.

build: 
	zip GalileoBabel.zip galileo_babel_s3.py

release: clean build
	cosmos-release lambda --lambda-version=`cosmos-release generate-version $(COMPONENT)` "./GalileoBabel.zip" $(COMPONENT)
