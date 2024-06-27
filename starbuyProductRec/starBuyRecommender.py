## History
# 26/03: Created the Star Buy recommender which should combine all the json files and insights and create a list of items and their prices to sell. Have not tested.
# 28/03: Tested and will output two json files, one is for the popular Star Buy and another is the rising Star Buy
# 01/04: April Fools! Jk it's tested and working
# 02/04: Added change to replace spacings with _ and to ensure that there is a starbuy for a popular brand even if first 5 is unavaiable. Added a bug fix where categories with spacing will return empty list

## Last modified: Tuesday 2 Apr, Regine

import json
from datetime import datetime, date
import boto3
import pandas as pd

s3_client = boto3.client('s3')

date = datetime.now().date()
date_collected = str(date)

def createJsonOutput(starBuy, typeCheck):
    starBuyJson = json.dumps(starBuy[0])

    if typeCheck == "popular":
        star_buy_recommendation_output_path = date_collected + "_bestStarBuyRecommendation"

        # Add to s3 bucket
        s3_client.put_object(Bucket='fyp-interest-forecasts', Key=f'starbuy_products/{star_buy_recommendation_output_path}.json', Body=starBuyJson)
        
    else:
        star_buy_recommendation_output_path = date_collected + "_risingStarBuyRecommendation"

        # Add to s3 bucket
        s3_client.put_object(Bucket='fyp-interest-forecasts', Key=f'starbuy_products/{star_buy_recommendation_output_path}.json', Body=starBuyJson)


# Define a function to truncate the date strings
def truncate_date(date_str):
    if len(date_str) > 10:
        return date_str[:10]
    else:
        return date_str

def getOutput(baseDataframe, scrapedDataDF, mostPopular):
    # Sort DataFrame by "popularity" column
    highestBrandsinCat = baseDataframe.sort_values(by="popularity", ascending=False)
    mostPopular = mostPopular.replace("_", "").upper()

    # Get the top 5 brands in the category
    topBrandsinCat = list(highestBrandsinCat.index)
    filteredtoPopCat_scrapedData = scrapedDataDF[scrapedDataDF['commparing_category'] == mostPopular]
    filteredSorted_scrapedData = filteredtoPopCat_scrapedData.sort_values(by='dateCollected', ascending=False)
    dateList = filteredSorted_scrapedData['dateCollected']
    
    # Apply the function to each value in the Series
    dateList = dateList.apply(truncate_date)
    latestDate = dateList.max()

    # Get latest scraped data
    latestDate_filteredtoPopCat_scrapedData = filteredSorted_scrapedData[filteredSorted_scrapedData['dateCollected'] == latestDate]
    
    # Create a boolean mask to identify rows with brands not in top5BrandsinCat
    # then filter out the rows using the boolean mask
    mask = latestDate_filteredtoPopCat_scrapedData['brand'].isin(topBrandsinCat)
    filtered_df = latestDate_filteredtoPopCat_scrapedData[mask]
    # Sort the filtered dataframe from lowest to highest pricing, then get top 5 (if there is more than 5)

    filtered_df_sorted = filtered_df.sort_values(by="discountedPrice", ascending=True).head(5)
    filtered_data = filtered_df_sorted.to_dict(orient="records")

    return filtered_data

#################### Getting popular values and results ####################

def main():
# Get sorted_results data from s3
    sorted_results = s3_client.get_object(Bucket='fyp-interest-forecasts', Key="starbuy_categories/sorted_results.json")
    decoded_results = sorted_results.get('Body').read().decode('utf-8')
    sorted_results = pd.read_json(decoded_results).transpose()

    table_name= "FYP-TLJ-Daily"
    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb') 

    # Scan the table to get all items
    response = dynamodb.scan(TableName=table_name)
    scrapedDataDF = pd.DataFrame(response['Items'])

    for column in scrapedDataDF.keys():
        try:
            transformed_values = [entry['S'] for entry in scrapedDataDF[column].values]
            scrapedDataDF[column] = transformed_values

        except:
            transformed_values = [float(entry['N']) for entry in scrapedDataDF[column].values]
            scrapedDataDF[column] = transformed_values

        finally:
            continue

    scrapedDataDF['category'] = scrapedDataDF['category'].str.replace(" ", "_")
    scrapedDataDF['commparing_category'] = scrapedDataDF['category'].str.replace("_", "")

    mostPopularCategory = ''

    categoryList = []
    for key, value in sorted_results.iterrows():
        for key2, value2 in value.items():
            if type(value2) == str:
                categoryList.append(value2)

    popCat_df = ''
    for cat in categoryList:
        mostPopularCategory = cat.replace(" ", "_")

        try:
            toFind = "RedditHwZAnalysis/" + date_collected + "_df_" + mostPopularCategory + ".json"
            toFindResults = s3_client.get_object(Bucket='cleaned-data-fyp', Key=toFind)
            content = toFindResults['Body'].read()
            content_str = content.decode('utf-8')
            popCat_df = pd.read_json(content_str).transpose()
            break
        except:
            continue

    popularItems = getOutput(popCat_df, scrapedDataDF, mostPopularCategory)

    #################### Getting rising values and results ####################

    # Get sorted_results data from s3
    risingJsonData = s3_client.get_object(Bucket='fyp-interest-forecasts', Key="starbuy_categories/categories_results.json")
    decoded_results = risingJsonData.get('Body').read().decode('utf-8')
    risingDf = pd.read_json(decoded_results).transpose()
    risingDf_sorted = risingDf.sort_values(by="perc_increase", ascending=False)
    risingCategory_list = risingDf_sorted.index.tolist()

    popCat_df = ''
    cat = ''
    for cat in risingCategory_list:
        cat = cat.replace(" ", "_")
        
        try:
            toFind = "RedditHwZAnalysis/" + date_collected + "_df_" + cat + ".json"
            toFindResults = s3_client.get_object(Bucket='cleaned-data-fyp', Key=toFind)
            content = toFindResults['Body'].read()
            content_str = content.decode('utf-8')
            popCat_df = pd.read_json(content_str).transpose()
            break
        except:
            continue

    risingItems = getOutput(popCat_df, scrapedDataDF, cat)

    def createJsonOutput(starBuy, typeCheck):
        starBuyJson = json.dumps(starBuy)

        if typeCheck == "popular":
            star_buy_recommendation_output_path = date_collected + "_bestStarBuyRecommendation"

            # Add to s3 bucket
            s3_client.put_object(Bucket='fyp-interest-forecasts', Key=f'starbuy_products/{star_buy_recommendation_output_path}.json', Body=starBuyJson)
            
        else:
            star_buy_recommendation_output_path = date_collected + "_risingStarBuyRecommendation"

            # Add to s3 bucket
            s3_client.put_object(Bucket='fyp-interest-forecasts', Key=f'starbuy_products/{star_buy_recommendation_output_path}.json', Body=starBuyJson)


    createJsonOutput(popularItems, "popular")
    createJsonOutput(risingItems, "rising")

