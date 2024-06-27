## History
# 26/03: Created the Star Buy recommender which should combine all the json files and insights and create a list of items and their prices to sell. Have not tested.
# 28/03: Tested and will output two json files, one is for the popular Star Buy and another is the rising Star Buy

## Last modified: Thursday 28 Mar, Regine

import json
from datetime import datetime, date
import boto3
import pandas as pd

# Define a function to truncate the date strings
def truncate_date(date_str):
    if len(date_str) > 10:
        return date_str[:10]
    else:
        return date_str

def getOutput(baseDataframe, scrapedDataDF, mostPopular):
    # Sort DataFrame by "popularity" column
    highestBrandsinCat = baseDataframe.sort_values(by="popularity", ascending=False)

    # Get the top 5 brands in the category
    top5BrandsinCat = list(highestBrandsinCat.head(5).index)

    filteredtoPopCat_scrapedData = scrapedDataDF[scrapedDataDF['category'] == mostPopular.upper()]
    filteredSorted_scrapedData = filteredtoPopCat_scrapedData.sort_values(by='dateCollected', ascending=False)

    dateList = filteredSorted_scrapedData['dateCollected']
    
    # Apply the function to each value in the Series
    dateList = dateList.apply(truncate_date)
    latestDate = dateList.max()

    # Get latest scraped data
    latestDate_filteredtoPopCat_scrapedData = filteredSorted_scrapedData[filteredSorted_scrapedData['dateCollected'] == latestDate]

    # Create a boolean mask to identify rows with brands not in top5BrandsinCat
    # then filter out the rows using the boolean mask
    mask = latestDate_filteredtoPopCat_scrapedData['brand'].isin(top5BrandsinCat)
    filtered_df = latestDate_filteredtoPopCat_scrapedData[mask]

    # Sort the filtered dataframe from lowest to highest pricing, then get top 5 (if there is more than 5)
    filtered_df_sorted = filtered_df.sort_values(by="discountedPrice", ascending=True).head(5)
    filtered_data = filtered_df_sorted.to_dict(orient="records")

    return filtered_data

scrapedDataDF = pd.read_csv("results.csv")

#################### Getting popular values and results ####################

s3_client = boto3.client('s3')

date = datetime.now().date()
date_collected = str(date)

# Get sorted_results data from s3
sorted_results = s3_client.get_object(Bucket='fyp-interest-forecasts/starbuy_categories', Key="sorted_results.json")

sorted_results = pd.read_json(sorted_results)

for entry in sorted_results:
    mostPopular = entry[0]
    try:
        toFind = date_collected + "_df_" + mostPopular + ".json"
        bucket_name = "cleaned-data-fyp"
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        for page in pages:
            for obj in page['Contents']:
                new_files.append(obj['Key'])

        toFindResults = s3_client.get_object(Bucket='cleaned-data-fyp/', Key=toFind)
        popCat_df = pd.read_json(toFindResults).transpose()
        break
    except:
        continue

popularItems = getOutput(popCat_df, scrapedDataDF, mostPopular)

#################### Getting rising values and results ####################

# Get sorted_results data from s3
risingJsonData = s3_client.get_object(Bucket='fyp-interest-forecasts/starbuy_categories', Key="categories_results.json")

risingDf = pd.read_json(risingJsonData).transpose()
risingDf_sorted = risingDf.sort_values(by="perc_increase", ascending=False)
risingCategory_list = risingDf_sorted.index.tolist()

popCat_df = ''
cat = ''
for cat in risingCategory_list:
    cat = cat.replace(" ", "")
    try:
        toFind = date_collected + "_df_" + cat + ".json"
        toFindResults = s3_client.get_object(Bucket='cleaned-data-fyp/RedditHwZAnalysis', Key=toFind)
        popCat_df = pd.read_json(toFindResults).transpose()
        break
    except:
        continue

risingItems = getOutput(popCat_df, scrapedDataDF, cat)

def createJsonOutput(cleanedData, typeCheck):

    starBuyJson = pd.to_json(cleanedData)

    if typeCheck == "popular":
        star_buy_recommendation_output_path = date_collected + "_bestStarBuyRecommendation.json"

        # Add to s3 bucket
        s3_client.put_object(Bucket='fyp-interest-forecasts', Key=f'starbuy_products/{star_buy_recommendation_output_path}', Body=starBuyJson)
        
    else:
        star_buy_recommendation_output_path = date_collected + "_risingStarBuyRecommendation.json"

        # Add to s3 bucket
        s3_client.put_object(Bucket='fyp-interest-forecasts', Key=f'starbuy_products/{star_buy_recommendation_output_path}', Body=starBuyJson)


createJsonOutput(popularItems, "popular")
createJsonOutput(risingItems, "rising")