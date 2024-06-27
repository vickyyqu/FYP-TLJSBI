# Conversion of scrapers into Lambda functions

## Set up AWS cli and serverless client
1. Go to https://aws.amazon.com/cli/ and download the package for your operating system
2. Go to https://nodejs.org/ and download LTS
3. Run the following command in your terminal
- npm install -g serverless

## Setting up your scraper and Dockerfiles (To be modified)
1. Add/modify the following codes in your scrapers

date = datetime.now().date()
addToURI = f"s3://raw-data-fyp/{date}_{scraper_name}.json"

custom_settings = {
        "FEED_URI": addToURI,
        "FEED_FORMAT": "json",
    }

2. Create a new file called lambda_function.py

import sys

def handler(event, context):
    # Run the Scrapy spider
    import subprocess
    subprocess.run(["scrapy", "runspider", "{ADD SCRAPER NAME HERE}.py"])
    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }

3. AWS Configure (To be updated)
- note to justin: please use either the user (lambda-creation) or update the ARN to the ARN of your account
- atb i'll try to help in the night lols

4. Run the following command lines

docker buildx build --load --platform linux/amd64 -t {INSERT WEBSITE NAME}-scrapy-lambda:latest .      
* note: do not use any uppercase when tagging images

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 590183683825.dkr.ecr.us-east-1.amazonaws.com/appliance-allstar-fyp

docker tag {INSERT WEBSITE NAME}-scrapy-lambda:latest 590183683825.dkr.ecr.us-east-1.amazonaws.com/appliance-allstar-fyp:latest  

docker push 590183683825.dkr.ecr.us-east-1.amazonaws.com/appliance-allstar-fyp:latest                                         

sls deploy

curl -X POST {INSERT ENDPOINT URL HERE}

* note: please ensure that all your naming conventions are correct

# Documentation
- Regine 22/1 : Created branch and folder, added the files first used on 19/1/2023
- Regine 25/1 : Corrected HV lambda function, created folder to store one scraper, updated README