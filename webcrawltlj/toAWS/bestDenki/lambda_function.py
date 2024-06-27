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
            'https://raw-data-fyp.s3.amazonaws.com/BestDenki/2024-02-05_Vacuum_links_BestDenki.json',
            # Add more URLs as needed
        ]

    # Run the Scrapy spider with each URL
    import subprocess
    for url in urls:
        curr_url = [url, "test"]
        subprocess.run(["scrapy", "runspider", "bestdenki_product_spider.py", "-a", f"urls={','.join(curr_url)}"])

    return { 
        'statusCode': '200',
        'body': 'Lambda function invoked',        
    }
