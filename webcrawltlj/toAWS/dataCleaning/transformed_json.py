import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime

def lambda_handler(event, context):
    # Extract required information from the event
    object_context = event["getObjectContext"]
    # Get the presigned URL to fetch the requested original object 
    # from S3
    s3_url = object_context["inputS3Url"]
    # Extract the route and request token from the input context
    request_route = object_context["outputRoute"]
    request_token = object_context["outputToken"]
    
    # Fetch the JSON file from S3 using the presigned URL
    original_json = fetch_json_from_s3(s3_url)
    if original_json is None:
        return {'status_code': 500, 'error': 'Failed to fetch JSON from S3'}

    # Clean the JSON data
    cleaned_json = clean_json(original_json)

    # Convert the cleaned JSON back to a string
    transformed_object = json.dumps(cleaned_json)

    # Write the transformed JSON back to S3 Object Lambda
    if not write_json_to_s3(transformed_object, request_route, request_token):
        return {'status_code': 500, 'error': 'Failed to write JSON to S3'}

    return {'status_code': 200}

def fetch_json_from_s3(s3_url):
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=s3_url.split('/')[2], Key='/'.join(s3_url.split('/')[3:]))
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        print(f"Error fetching JSON from S3: {e}")
        return None

def clean_json(json_data):
    cleaned_data = []
    for item in json_data:
        # Convert strings to uppercase
        cleaned_item = {key: value.upper() if isinstance(value, str) else value for key, value in item.items()}
        
        # Convert numeric values to floats
        for key in ["Discounted Price", "Listed Price", "Discount Percentage"]:
            if key in cleaned_item:
                cleaned_item[key] = float(cleaned_item[key])
        
        # Parse date string into datetime object
        if "Date Collected" in cleaned_item:
            date_str = cleaned_item["Date Collected"]
            cleaned_item["Date Collected"] = datetime.strptime(date_str, "%d/%m/%Y")
        
        cleaned_data.append(cleaned_item)
    
    return cleaned_data

def write_json_to_s3(json_data, request_route, request_token):
    try:
        s3 = boto3.client('s3')
        response = s3.write_get_object_response(
            Body=json_data,
            RequestRoute=request_route,
            RequestToken=request_token)
        # Wait until the operation completes
        s3.meta.client.wait_until('object_exists', Bucket=response['Payload']['Bucket'], Key=response['Payload']['Key'])
        return True
    except ClientError as e:
        print(f"Error writing JSON to S3: {e}")
        return False
                               