import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")
import requests
import json 
import boto3
from datetime import datetime


def lambda_handler(event, context):

    ### retrieve starbuy products from s3 buckets
    s3 = boto3.client('s3', region_name='us-east-1')
    s3_bucket_name = 'fyp-interest-forecasts'
    file_names = ["bestStarBuyRecommendation.json", "risingStarBuyRecommendation.json"]
    today = datetime.now()
    date_key = today.strftime('%Y-%m-%d')

    final_starbuys = []
    unique_items = []

    for file_name in file_names:
        key = f'starbuy_products/{date_key}_{file_name}'

        response = s3.get_object(Bucket=s3_bucket_name, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))

        if isinstance(data, list):
            for each in data:
                output = get_price_forecast(each, file_name)

                if output['product'] not in unique_items:
                    final_starbuys.append(output)
                    unique_items.append(output['product'])
        else:
            output = get_price_forecast(data, file_name)
            if output['product'] not in unique_items:
                final_starbuys.append(output)
                unique_items.append(output['product'])

    
    outputkey = f"FINAL_starbuys/{date_key}_starbuy_results.json"

    json_string = json.dumps(final_starbuys)
    json_bytes = json_string.encode('utf-8')
    s3.put_object(Bucket=s3_bucket_name, Key=outputkey, Body=json_bytes)

        
    return { 
        'statusCode': '200',
        'body':  json.dumps('Forecast data successfully cleaned and stored in S3.')      
    }


def get_price_forecast(data, file_name):
    product = data["product"]
    brand = data["brand"]
    model = data["modelNumber"]
    category = data["category"]
    res = requests.get(f"https://ir39pxdck8.execute-api.us-east-1.amazonaws.com/exposeAPI/getProductHistory?productKey={product}")
    response = json.loads(res.text)

    cleaned_res = []
    for ele in response:
        item = {}
        for key1, value1 in ele.items():
            for key2, value2 in value1.items():
                item[key1] = value2
        cleaned_res.append(item)

    price_df = pd.DataFrame(cleaned_res)

    # format data
    price_df['brand'] = price_df['brand'].str.upper()
    price_df['modelNumber'] = price_df['modelNumber'].str.upper()
    price_df['discountedPrice'] = pd.to_numeric(price_df['discountedPrice'], errors='coerce')

    # filter data
    model_df = price_df[(price_df['brand'] == brand.upper()) & (price_df['modelNumber'].str.contains(model.upper()))]
    model_df.drop(columns=["platform", "discountPercentage", "category", "listedPrice", "product", "model", "brand", "modelNumber", "scraped"])
    model_df['dateCollected'] = pd.to_datetime(model_df['dateCollected'], format='mixed')
    model_df['dateCollected'] = model_df['dateCollected'].dt.floor('D')
    grouped_df = model_df.groupby(model_df['dateCollected'])["discountedPrice"].mean().reset_index()

    # interpolate daily missing rows 
    grouped_df.set_index('dateCollected', inplace=True)
    grouped_df = grouped_df.resample('D').asfreq()
    imputed_df = grouped_df.interpolate(method='linear')
    imputed_df.reset_index(inplace=True)
    imputed_df = imputed_df.rename(columns={'dateCollected': 'ds', 'discountedPrice': 'y'})

    # forecast
    m = Prophet()
    m.fit(imputed_df)

    future = m.make_future_dataframe(periods=14, freq='D')
    forecast = m.predict(future)

    # get next week's forecasted price
    current_date = datetime.now() 

    # get next week start date
    next_week_start = current_date + timedelta(days=(6 - current_date.weekday()) + 1)

    # get forecast value for next week
    forecast['week_year'] = forecast['ds'].dt.strftime('%U-%Y')
    next_week_df = forecast[forecast['week_year'] == next_week_start.strftime('%U-%Y')]
    predicted_price = round(next_week_df['yhat'].mean(), 2)

    p = int(len(imputed_df)*0.6)
    df_cv = cross_validation(m, initial=f'{p} days', period='3 days', horizon='7 days')
    df_p = performance_metrics(df_cv, rolling_window=1)
    rmse = df_p['rmse'].mean()

    starBuyType = "top"
    if "rising" in file_name:
        starBuyType = "rising"
    
    return {
            "starBuyType": starBuyType,
            "product": product,
            "modelNumber": model,
            "brand": brand,
            "category": category,
            "recPrice": predicted_price,
            "rmse": rmse
        }