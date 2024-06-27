import sys


def handler(event, context):
    # Run the Scrapy spider
    import subprocess
    subprocess.run(["scrapy", "runspider", "parisilk.py"])
    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }