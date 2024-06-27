import sys
import webcrawltlj.toAWS.CDMConverters.courtsCDM.courtsCDM_converter as courtsCDM_converter


def handler(event, context):
    singstat.main(event, context)
    retrieve_S3.main()

    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }