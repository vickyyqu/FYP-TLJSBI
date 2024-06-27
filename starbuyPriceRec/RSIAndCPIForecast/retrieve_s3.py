import boto3
import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np
from io import StringIO
from dateutil.relativedelta import relativedelta
from datetime import datetime
from prophet import Prophet

s3 = boto3.client('s3', region_name='us-east-1')  

def read_s3_data(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(data))
    return df

def main():
    bucket_name = 'fyp-cpi-rpi-data'

    folder_name = "CPI"
    file_name = "CPI_data.csv"
    column_name = "CPI"  
    full_key_name = f'{folder_name}/{file_name}'
    
    # Cleaning data, creating DF
    df = pd.DataFrame()

    df_raw = read_s3_data(bucket_name, full_key_name)
    df_raw['Date'] = pd.to_datetime(df_raw['Date'], format='%Y-%m-%d')  

    df = df.join(df_raw.rename(columns={'value': column_name}), how='outer')
    df = df.dropna()


    # Forecasting with Prophet
    m = Prophet()
    df = df.rename(columns={'Date': 'ds', 'CPI': 'y'})
    m.fit(df)
    
    last_date = df['ds'].max()
    months_to_end_2025 = (2025 - last_date.year) * 12 + (12 - last_date.month)
    future = m.make_future_dataframe(periods=months_to_end_2025, freq='M')
    forecast = m.predict(future)
    forecast = forecast[forecast['ds'] >= datetime(2022, 1, 1)]


    # Monthly ranking
    df['month'] = df['ds'].dt.month
    df['year'] = df['ds'].dt.year

    rank_df = df.groupby(['year', 'month'])['y'].sum().reset_index()

    rank_df['rank'] = rank_df.groupby('year')['y'].rank(method='max', ascending=True)
    rank_df = rank_df.sort_values(by=['year', 'rank'], ascending=[True, True])

    avg_rank = rank_df.groupby("month").mean()["rank"]
    last_date = df['ds'].max()
    months_to_end_2025 = (2025 - last_date.year) * 12 + (12 - last_date.month)
    total_months = len(df) + months_to_end_2025
    repeats = total_months // 12 + (total_months % 12 > 0)
    forecast_rank = np.tile(avg_rank, repeats)[:total_months]

    df["rank"] = df.apply(lambda row: rank_df.loc[(rank_df["year"]==row["year"]) & (rank_df["month"]==row["month"]), "rank"].values[0], axis=1)


    # Forecasting with Exogenous variables
    train_size = int(len(df) * 0.8)
    train, val = df[:train_size], df[train_size:]

    m = Prophet(changepoint_prior_scale=0.1, seasonality_prior_scale=1.0)
    m.add_regressor('rank')
    m.fit(df)

    last_date = df['ds'].max()
    months_to_end_2025 = (2025 - last_date.year) * 12 + (12 - last_date.month)
    future = m.make_future_dataframe(periods=months_to_end_2025, freq='M')
    # future = m.make_future_dataframe(freq='M', periods=12, include_history=False)
    future['rank'] = forecast_rank[:len(future)]

    forecast = m.predict(future)
    forecast = forecast[forecast['ds'] >= datetime(2022, 1, 1)]

    forecast['Percent Change to Lowest'] = ((forecast['yhat_lower'] - forecast['yhat']) / forecast['yhat']) * 100
    # The percentage change to the highest price from the forecasted price
    forecast['Percent Change to Highest'] = ((forecast['yhat_upper'] - forecast['yhat']) / forecast['yhat']) * 100

    forecast_summary = pd.DataFrame({
        'Date': forecast['ds'],  # Include the 'ds' column which contains dates
        'Forecasted Price': forecast['yhat'],
        'Lowest Price': forecast['yhat_lower'],
        'Highest Price': forecast['yhat_upper'],
        'Percent Change to Lowest': forecast['Percent Change to Lowest'],
        'Percent Change to Highest': forecast['Percent Change to Highest']
    })

    forecast_summary.reset_index(drop=True, inplace=True)
    csv_buffer = StringIO()
    forecast_summary.to_csv(csv_buffer, index=True)

    s3.put_object(Bucket='fyp-pricing-forecasts', Key='CPI_forecast_results.csv', Body=csv_buffer.getvalue().encode('utf-8'))

    return {
        'statusCode': 200,
        'body': json.dumps('Forecasting completed and results stored in S3.')
    }


if __name__ == "__main__":
    # Call the lambda_handler function and print its return value
    response = main()
    print(response)