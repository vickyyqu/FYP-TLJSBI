import sys
import transform_json
import transformed_json

def handler(event, context):
    # Run the Scrapy spider

    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }