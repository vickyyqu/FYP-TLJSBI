import pandas as pd
from sklearn.metrics import mean_squared_error
import numpy as np
import statsmodels.api as sm
from datetime import datetime, timedelta
import os
import json
from io import BytesIO
import itertools
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
import boto3


def lambda_handler(event, context):
    get_forecast()
    forecast_popular_categories()
    
    return { 
        'statusCode': '200',
        'body':  json.dumps('Forecast data successfully cleaned and stored in S3.')      
    }


def build_forecast_model(category):
    # Load dataset from s3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3_bucket_name = 'fyp-google-trends'
    label = category.replace(" ", "_")
    key = f"clean/{label}_results.csv"

    response = s3.get_object(Bucket=s3_bucket_name, Key=key)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['month'] = df['timestamp'].dt.month

    # Assign monthly ranks to the interest dataset
    avg_rank = df.groupby("month")["rank"].mean()
    date = df["timestamp"][len(df)-1]
    forecast_rank = []

    for i in range(52):
        date += timedelta(days=7)
        month = date.month

        forecast_rank.append(avg_rank[month])
    
    # Hyperparameter tuning
    param_grid = {  
        'changepoint_prior_scale': [0.01, 0.1, 0.5],
        'seasonality_prior_scale': [0.1, 1.0, 10.0],
    }
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    best_rmse = float('inf')
    best_m = None

    # Tune and fit model
    for params in all_params:
        m = Prophet(**params)
        m.add_regressor('rank')

        clean_df = df.rename(columns={'timestamp': 'ds', 'search_count': 'y'})
        m.fit(clean_df)

        df_cv = cross_validation(m, initial='365 days', period='180 days', horizon='365 days')
        df_p = performance_metrics(df_cv, rolling_window=1)

        if df_p['rmse'].mean() < best_rmse:
            best_m = m
            best_rmse = df_p['rmse'].mean() 
    
    # Make future dataframe with Prophet and make predictions
    future = best_m.make_future_dataframe(freq='W', periods=52)
    future['rank'] = list(df["rank"]) + forecast_rank

    forecast = best_m.predict(future)

    return forecast, best_rmse, best_m


def get_forecast():
    s3 = boto3.client('s3', region_name='us-east-1')
    s3_bucket_name = 'fyp-interest-forecasts'

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

    # rmses = []
    # models = []
    forecasts = []

    for category in categories.keys():
        forecast, rmse, m = build_forecast_model(category)
        forecasts.append({
            "category": category,
            "rmse": rmse
        })

        label = category.replace(" ", "_")
        key = f"forecast/{label}_results.csv"

        forecast_df = pd.DataFrame(data=forecast)
        forecast_data = forecast_df.to_csv(index=False)

        s3.put_object(Bucket=s3_bucket_name, Key=key, Body=forecast_data)

    key = f"rmses/models_result.csv"
    perf_df = pd.DataFrame(data=forecasts)
    perf_data = perf_df.to_csv(index=False)
    s3.put_object(Bucket=s3_bucket_name, Key=key, Body=perf_data)
    

def forecast_popular_categories():
    # Load dataset from s3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3_bucket_name = 'fyp-interest-forecasts'

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
        "air con": ["Air conditioner", "Air con"],
        "vacuum": ["Vacuum"],
        "coffee machine": ["Coffee maker", "Coffee machine"],
        "air purifier": ["Air purifier"],
        "smart lock": ["Smart lock"],
        "air fryer": ["Air fryer"]
    }

    categories_searches = {}
    final_scores = {}

    for category in categories.keys():
        label = category.replace(" ", "_")
        key = f"forecast/{label}_results.csv"

        response = s3.get_object(Bucket=s3_bucket_name, Key=key)
        data = response['Body'].read()
        df = pd.read_csv(BytesIO(data))
        df["ds"] = pd.to_datetime(df["ds"])

        current_date = datetime.now()
        # get this week start date
        this_week_start = current_date - timedelta(days=current_date.weekday())
        # get next week start date
        next_week_start = current_date + timedelta(days=(6 - current_date.weekday()) + 1)

        df['week_year'] = df['ds'].dt.strftime('%U-%Y')

        # get forecast value for this week
        this_week_df = df[df['week_year'] == this_week_start.strftime('%U-%Y')]
        this_week_df = this_week_df.drop('week_year', axis=1).reset_index()
        this_week_searches = this_week_df.at[0, 'yhat'] / len(categories[category])
        this_week_avg = this_week_df.at[0, 'trend'] / len(categories[category])

        # get forecast value for next week
        next_week_df = df[df['week_year'] == next_week_start.strftime('%U-%Y')]
        next_week_df = next_week_df.drop('week_year', axis=1).reset_index()
        next_week_searches = next_week_df.at[0, 'yhat'] / len(categories[category])
        next_week_avg = next_week_df.at[0, 'trend'] / len(categories[category])

        # get forecasted value relative to the moving average
        relative_forecast = next_week_searches/next_week_avg
        # get percentage increase from the previous week
        perc_increase = (next_week_searches-this_week_searches)/(0.5*(this_week_avg+next_week_avg))

        normalised_searches = {
            "forecast_relative_to_trend": relative_forecast,
            "perc_increase": perc_increase,
            "forecast_value": next_week_searches,
            "final_score": (relative_forecast+perc_increase)*next_week_searches
        }

        categories_searches[category] = normalised_searches
        final_scores[category] = (relative_forecast+perc_increase)*next_week_searches
    
    sorted_categories = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
    rising_categories = [x for x in sorted_categories if categories_searches[x[0]]["forecast_relative_to_trend"] > 1 ]

    sorted_categories_data = json.dumps(sorted_categories, indent=4)
    categories_searches_data = json.dumps(categories_searches, indent=4)

    sorted_key = "starbuy_categories/sorted_results.json"
    s3.put_object(Bucket=s3_bucket_name, Key=sorted_key, Body=sorted_categories_data)

    categories_key = "starbuy_categories/categories_results.json"
    s3.put_object(Bucket=s3_bucket_name, Key=categories_key, Body=categories_searches_data)


    # return rising_categories, categories_searches

