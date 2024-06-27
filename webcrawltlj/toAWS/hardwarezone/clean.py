import pandas as pd
import numpy as np
import re
import boto3
import json
from io import BytesIO
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def lambda_handler(event, context):

    s3 = boto3.client('s3', region_name='us-east-1')
    s3_bucket_name = 'cleaned-data-fyp'
    ### Might need to change depending on the file name saved for the output of hardwarezone scraper
    key = f"raw/ad_info.json"

    response = s3.get_object(Bucket=s3_bucket_name, Key=key)
    data = json.loads(response['Body'].read().decode('utf-8'))
    df = pd.DataFrame(data=data)
    df.dropna(subset=["title"], inplace=True)
    df.drop(columns=['error'], inplace=True)

    cleaned_brands = list(pd.read_csv('cleaned_brands.csv')["brand"])

    def clean_string(text):
        words = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word.lower() not in stop_words]
        cleaned_words = [re.sub(r'[^a-zA-Z]', '', word) for word in words]
        cleaned_words = [word for word in cleaned_words if word]
        cleaned_text = ' '.join(cleaned_words)
        
        return cleaned_text

    df["cleaned_title"] = df["title"].apply(clean_string)
    df["cleaned_desc"] = df["description"].apply(clean_string)

    def find_brand(texts, brands=cleaned_brands):
        brand_dict = {}
        for brand in cleaned_brands:
            brand_dict[brand.split(" ")[0].upper()] = brand.upper()
        
        print(brand_dict)
        
        out = []
        for each in texts:
            brand = "NA"

            for ch in each.split(" "):
                if ch.upper() in brand_dict:
                    brand = brand_dict[ch.upper()]
            
            out.append(brand)
        return out

    df["brand_text"] = find_brand(list(df["cleaned_title"]))
    df["brand_desc"] = find_brand(list(df["cleaned_desc"]))

    key = f"clean/results.csv"
    csv_data = df.to_csv(index=False)
    s3.put_object(Bucket=s3_bucket_name, Key=key, Body=csv_data)

