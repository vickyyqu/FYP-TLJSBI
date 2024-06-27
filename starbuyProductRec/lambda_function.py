import sys
import starBuyRecommender

def handler(event, context):
    # starBuyRecommender.truncate_date()
    # starBuyRecommender.getOutput()
    # starBuyRecommender.createJsonOutput()
    starBuyRecommender.main()
    
    return { 
        'statusCode': '200',
        'body': 'Lambda function invoked',        
    }
