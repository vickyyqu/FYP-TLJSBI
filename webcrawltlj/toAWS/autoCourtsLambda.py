import sys

def handler(event, context):
    # Extract URLs from the Lambda event
    if 'urls' in event:
        urls = event['urls']
        # Convert a single URL to a list
        if not isinstance(urls, list):
            urls = [urls]
    else:
        # Provide default URLs if not provided in the event
        urls = [
            "https://www.courts.com.sg/home-appliances/small-appliances/electric-cooking?p=1&type1=Fryer",
            # Add more URLs as needed
        ]

    # Run the Scrapy spider with each URL
    import subprocess
    for url in urls:
        curr_url = [url, "test"]
        subprocess.run(["scrapy", "runspider", "courts_spider.py", "-a", f"urls={','.join(curr_url)}"])

    return { 
        'statusCode': '200',
        'body': 'Lambda function invoked',        
    }
