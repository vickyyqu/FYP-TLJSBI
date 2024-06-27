import os
import json
import requests
import pandas as pd
from urllib.parse import quote
from datetime import datetime
import boto3

def lambda_handler(event, context):
    print("CALLING INTEREST FOR PRODUCT CATEGORIES......")
    categories = [
        "Refridgerator",
        "Fridge",
        "Washing machine",
        "Gas cooker",
        "Stovetop",
        "Induction cooker",
        "Television",
        "TV",
        "Dryer",
        "Fans",
        "Oven",
        "Microwave",
        "Cooker Hood",
        "Water purifier",
        "Air conditioner",
        "Air con",
        "Vacuum",
        "Coffee maker",
        "Coffee machine",
        "Air purifier",
        "Smart lock",
        "Air fryer"
    ]

    unsuccessful_calls = []

    for each in categories:
        call_google_trends(each, unsuccessful_calls)
        call_google_trends(each, unsuccessful_calls)

    if len(unsuccessful_calls) > 0:
        print("Calling unsuccessful queries again.......")
        for each in unsuccessful_calls:
            call_google_trends(each, unsuccessful_calls)
    
    return { 
        'statusCode': '200',
        'body':  json.dumps('Google trends raw data successfully stored in S3')      
    }

def call_google_trends(query, unsuccessful_calls):
    date_key = 'today 5-y'

    try:
        params = {
            'api_key': 'nydDNGgplCGWiXB3FcQGwAUBQi0nIBCy',
            'geo': 'SG',
            "engine": "google_trends",
            "device": "desktop",
            "q": query,
            "date": date_key
        }

        query_string = "&".join([f"{key}={quote(str(value))}" for key, value in params.items()])
        url = f"/v1?{query_string}"

        print(f"CALLING API for {query}......")
        response = requests.get(f"https://serpapi.webscrapingapi.com{url}")
        response.raise_for_status()

        print(response)

        json_data = response.json()
        label = query.replace(" ", "_")

        json_data = response.json()

        s3 = boto3.client('s3', region_name='us-east-1')
        s3_bucket_name = 'fyp-google-trends'
        key = f"raw/{label}_results.json"

        # s3.put_object(Bucket=s3_bucket_name, Key=key, Body=json_data)

        json_string = json.dumps(json_data)
        json_bytes = json_string.encode('utf-8')
        s3.put_object(Bucket=s3_bucket_name, Key=key, Body=json_bytes)

        print("Success!")
        return json_data

    except Exception as e:
        unsuccessful_calls.append(query)
        print("API call failed.")
        print("Error message:", str(e))
