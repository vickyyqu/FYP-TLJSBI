import sys
import api
import clean
import forecast


def handler(event, context):
    # api.lambda_handler(event, context)
    # clean.lambda_handler(event, context)
    forecast.lambda_handler(event, context)

    return { 
        'statusCode': '200',  
        'body': 'Lambda function invoked for google trends function',        
    }