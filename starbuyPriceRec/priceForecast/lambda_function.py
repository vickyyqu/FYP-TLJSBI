import sys
import final_starbuy

def handler(event, context):
    final_starbuy.lambda_handler(event, context)

    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }