import boto3
import json
from botocore.config import Config

# This function modifies the JSON object as described
def modify_json(json_data):
    modified_data = json.loads(json_data)

    # Convert all strings to uppercase
    modified_data = {k: v.upper() if isinstance(v, str) else v for k, v in modified_data.items()}

    # Convert all numbers to float
    modified_data = {k: float(v) if isinstance(v, (int, float)) else v for k, v in modified_data.items()}

    return json.dumps(modified_data)

# Lambda function handler
def main(event, context):
    object_context = event["getObjectContext"]
    s3_url = object_context["inputS3Url"]
    request_route = object_context["outputRoute"]
    request_token = object_context["outputToken"]
    
    # Get the JSON object from S3
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    response = s3.get_object(Bucket='test-cleaning-scraped', Key='230124_inductionCooker_courts.json')
    original_object = response['Body'].read().decode('utf-8')

    # Modify the JSON object
    transformed_object = modify_json(original_object)

    # Write the modified object back to S3 Object Lambda
    s3.write_get_object_response(
        Body=transformed_object,
        RequestRoute=request_route,
        RequestToken=request_token)

    # Return the status code  
    return {'status_code': 200}