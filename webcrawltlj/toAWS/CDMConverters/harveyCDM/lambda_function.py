import sys
import harveyCDM_converter


def handler(event, context):
    singstat.main(event, context)
    retrieve_S3.main()

    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }