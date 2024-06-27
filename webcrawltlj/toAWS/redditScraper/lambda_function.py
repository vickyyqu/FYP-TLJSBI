import sys
import redditHardware_scraperAnalysis

def handler(event, context):
    redditHardware_scraperAnalysis.main()
    return { 
        'statusCode': '200',
        'body': 'Lambda function invoked',        
    }
