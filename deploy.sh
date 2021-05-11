rm GalileoBabel.zip
zip GalileoBabel.zip galileo_babel_s3.py 
aws s3 cp GalileoBabel.zip s3://galileo-babel-lambda
