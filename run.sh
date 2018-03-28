python3.4 -m virtualenv galileo-babel
source galileo-babel/bin/activate
pip install troposphere
pip install awacs
pip install pytest
pip install pycurl
pip install boto3
cd infrastructure/src/
python -m babel.devenvironment --lambda-function-bucket galileo-babel-lambda --environment dev --aws-accountId 195048873603 --region eu-west-2
