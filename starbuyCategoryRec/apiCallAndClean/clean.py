import json
import csv
import pandas as pd
from datetime import datetime
from urllib.parse import quote
import os
import boto3


def lambda_handler(event, context):

    categories = {
        "fridge": ["Refridgerator", "Fridge"],
        "washing machine": ["Washing machine"],
        "gas cooker": ["Gas cooker", "Stovetop"],
        "induction cooker": ["Induction cooker"],
        "tv": ["Television", "TV"],
        "dryer": ["Dryer"],
        "fans": ["Fans"],
        "oven": ["Oven", "Microwave"],
        "hood": ["Cooker Hood"],
        "water purifier": ["Water purifier"],
        "air con": ["Air con"],
        "vacuum": ["Vacuum"],
        "coffee machine": ["Coffee maker", "Coffee machine"],
        "air purifier": ["Air purifier"],
        "smart lock": ["Smart lock"],
        "air fryer": ["Air fryer"]
    }

    for category, queries in categories.items():
        clean_all_data(category, queries)
    
    return { 
        'statusCode': '200',
        'body':  json.dumps('Google trends data successfully cleaned and stored in S3.')      
    }


def clean_all_data(category, queries):
    s3 = boto3.client('s3', region_name='us-east-1')
    s3_bucket_name = 'fyp-google-trends'
    label = category.replace(" ", "_")

    try:
        cleaned = []
        for query in queries:
            raw_label = query.replace(" ", "_")
            key = f"raw/{raw_label}_results.json"
            
            response = s3.get_object(Bucket=s3_bucket_name, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))

            clean_data = clean_trend_data(data, label)
            cleaned += clean_data

        df = pd.DataFrame(data=cleaned)
        df['timestamp'] = df['timestamp'].dt.floor('D')
        grouped_df = df.groupby(df['timestamp'].dt.floor('D'))["search_count"].mean().reset_index()
        clean_df = impute_rank_data(grouped_df)
        csv_output = []
        
        for i in range(len(clean_df)):
            csv_output.append({
                "title": cleaned[i]["title"],
                "timestamp": clean_df.at[i, "timestamp"],
                "search_count": clean_df.at[i, "search_count"],
                "rank": clean_df.at[i, "rank"],
                "date_collected": cleaned[i]["date_collected"]
            })

        csv_df = pd.DataFrame(data=csv_output)
        csv_data = csv_df.to_csv(index=False)
        key = f"clean/{label}_results.csv"
        s3.put_object(Bucket=s3_bucket_name, Key=key, Body=csv_data)

    except Exception as e:
        print(f"Error occurred cleaning data for {query}: {str(e)}")


def clean_trend_data(data, label):
    cleaned = []

    try:
        interest = data["results"]["interest_over_time"]

        for entry in interest:
            result = {
                "title": data["search_information"]["query_displayed"][0],
                "timestamp": datetime.utcfromtimestamp(int(entry["time"])),
                "search_count": entry["value"][0],
                "date_collected": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            cleaned.append(result)

    except Exception as e:
        print(f"API OUTPUT ERROR: {str(e)}")

    return cleaned


def impute_rank_data(df):

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    weekly_df = df[["timestamp", "search_count"]].resample('W-Mon', on="timestamp").mean().reset_index()
    imputed_df = df.merge(weekly_df, on="timestamp", how='left', suffixes=('_original', '_weekly'))
    imputed_df['search_count_imputed'] = imputed_df['search_count_original'].combine_first(imputed_df['search_count_weekly'])
    df = imputed_df.drop(['search_count_original','search_count_weekly'], axis=1)
    df.rename(columns={'search_count_imputed': 'search_count'}, inplace=True)

    # create ranks for each month in each year
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year
    grouped_df = df.groupby(['year', 'month'])['search_count'].sum().reset_index()
    grouped_df['rank'] = grouped_df.groupby('year')['search_count'].rank(method='max', ascending=True)
    rank_df = grouped_df.sort_values(by=['year', 'rank'], ascending=[True, True])

    # add ranks to agg_data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["rank"] = df.apply(lambda row: rank_df.loc[(rank_df["year"]==row["year"]) & (rank_df["month"]==row["month"]), "rank"].values[0], axis=1)

    return df
