import sys
import retrieve_s3


def handler(event, context):
    retrieve_s3.main()

    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }