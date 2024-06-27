# 30/03: Created the code for AWS
# 01/04: Debugged the code, it works now

## Last modified: Monday 01 Apr, Regine

clientID = 'TTHvGhN8VYCNdie1uB83vg'
clientSecret = '6FCjvM6iIrthyu7DkM7k__z95sra-g'

import praw
import json
import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import re
import math
import os
import time
import multiprocessing 
from concurrent.futures import ProcessPoolExecutor
import concurrent
import subprocess
import re
import time
from datetime import datetime, date
import boto3

# from reddit_functions import get_submission_info

import subprocess
import re
import time

def get_initial_memory_usage():
    # Use the 'top' command to get initial memory usage
    command = "top -l 1 | grep PhysMem"
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    # Parse the output to extract the memory usage
    match = re.search(r'(\d+)\w+ used', output)
    if match:
        initial_memory_usage = int(match.group(1))
        return initial_memory_usage
    else:
        return None

def run_script():
    # Use subprocess to run your Python script
    # Example: subprocess.run(["python", "your_script.py"])
    pass

def monitor_memory_usage():
    # Use the 'top' command to monitor memory usage periodically
    # For example, you can run it in a loop with a delay
    while True:
        command = "top -l 1 | grep PhysMem"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        print(output)  # Print memory usage information
        time.sleep(5)  # Adjust the delay as needed

def get_final_memory_usage():
    # Use the 'top' command to get final memory usage
    command = "top -l 1 | grep PhysMem"
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    # Parse the output to extract the memory usage
    match = re.search(r'(\d+)\w+ used', output)
    if match:
        final_memory_usage = int(match.group(1))
        return final_memory_usage
    else:
        return None

def calculate_memory_usage_difference(initial_usage, final_usage):
    # Calculate the difference between initial and final memory usage
    memory_usage_difference = final_usage - initial_usage
    return memory_usage_difference

####################################################################################
############################ Sentiment analysis section ############################
####################################################################################

################################# Defined functions ################################

def get_submission_info(submission):
    title = submission.title
    content = submission.selftext
    comments = [comment.body.replace('\n', ' ') for comment in sorted(submission.comments, key=lambda x: x.score, reverse=True)[:30] if isinstance(comment, praw.models.Comment)]
    kudos = submission.score
    upvotes = submission.ups
    submission_date = submission.created_utc
    print('its still running don"t worry')
    content = content.replace('\n', ' ')
    comments_dates = [comment.created_utc for comment in sorted(submission.comments, key=lambda x: x.score, reverse=True)[:30] if isinstance(comment, praw.models.Comment)]

    return {
        'Title': title,
        'Content': content,
        'Top_Comments': comments,
        'Kudos': kudos,
        'Upvotes': upvotes,
        'Submission_Date': submission_date,
        'Comments_Dates': comments_dates
    }

def column_to_list(csv_file, column_index):
    df = pd.read_csv(csv_file, skiprows=1)
    column_list = df.iloc[:, column_index].tolist()

    column_list.remove("GOOGLE")
    
    return column_list

## Purpose: Get sentiment analysis
def get_senti_analysis(sentiment_collection, sentence, brand_cat, sentenceDate, max_length=512):
    brand = brand_cat[0]
    # Initialize BERT tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)  # Positive, neutral and negative sentiments

    # Tokenize and truncate the sentence
    modified_sentence = sentence.lower() 
    tokenized_sentence = tokenizer.encode(modified_sentence, add_special_tokens=True, max_length=max_length, truncation=True)

    # Find indices of brand mentions in the tokenized sentence
    brand_indices = [i for i, token in enumerate(tokenized_sentence) if tokenizer.decode([token]) == brand.lower()]

    # Modify the sentence to focus on the specified brand
    for idx in brand_indices:
        tokenized_sentence[idx] = tokenizer.convert_tokens_to_ids("[MASK]")  # Replace brand mentions with [MASK] token

    # Convert tokenized sentence to PyTorch tensor
    input_ids = torch.tensor([tokenized_sentence])
    sentiment = ''

    # Perform sentiment analysis
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits
        predicted_labels = torch.argmax(logits, dim=1).tolist()

        if predicted_labels[0] == 1:
            sentiment = "positive"
        elif predicted_labels[0] == 0:
            sentiment = "neutral"
        elif predicted_labels[0] == 2:
            sentiment = "negative"

    if sentenceDate == 0:
        sentenceDate = 1
    sentiment_collection[brand_cat][sentiment] += 1 * (1/sentenceDate)

    return sentiment_collection

## Purpose: To get the brand and category of the sentence, then add to the sentiment collection
## Depends on the get_senti_analysis function
def get_brand_and_category(sentiment_collection, brands, sentences, categories, sentenceDate):

    # Convert Unix timestamp to datetime object
    submission_datetime = datetime.fromtimestamp(sentenceDate)

    # Get current datetime
    current_datetime = datetime.now()

    # Calculate the difference
    time_difference = current_datetime - submission_datetime

    # Extract the number of days
    days_since_posted = time_difference.days

    for brand in brands:
        # Tokenize the sentence using regular expressions
        sentence_words = re.findall(r'\b\w+\b', sentences.lower())

        if brand.lower() in sentence_words:
            cat = ""

            for category in categories:
                if category.lower() in sentence_words:
                    cat = category
                    if cat == "Washer":
                        cat = "Washing Machine"

            cat = cat.replace(" ", "_").lower()
            brand_cat = (brand, cat)
            
            if brand_cat not in sentiment_collection:
                sentiment_collection[brand_cat] = {"positive": 0, "negative": 0, "neutral": 0}
            
            sentiment_collection = get_senti_analysis(sentiment_collection, sentences, brand_cat, days_since_posted)

    return sentiment_collection

## Purpose: To get brand and category without adding the sentiment collection code
## Copied from above code
def get_brand_and_category_noSentiment(title, desc, categories, brands):
    brand_cat = ""
    for brand in brands:
        # Tokenize the sentence using regular expressions
        title_words = re.findall(r'\b\w+\b', title.lower())
        description_words = re.findall(r'\b\w+\b', desc.lower())

        if brand.lower() in title_words or brand.lower() in description_words:
            cat = ""

            for category in categories:
                if category.lower() in title_words or category.lower() in description_words:
                    cat = category
                    if cat == "Washer":
                        cat = "Washing Machine"

            cat = cat.replace(" ", "_").lower()
            brand_cat = [brand, cat]

    return brand_cat

sentiment_collection = {}

## Purpose: Normalizing popularity scores
def min_max_scaling(scores):
    print(scores)
    values = scores.values()
    min_score = min(values)
    max_score = max(values)
    if min_score == max_score:
        # Handle the case where all values are the same
        return {brand: 0.5 for brand in scores}  # Assigning 0.5 as a default scaled value

    scaled_scores = {brand: (score - min_score) / (max_score - min_score) for brand, score in scores.items()}
    return scaled_scores

## Purpose: Calculating popularity scores
def get_popular_score(sentiment_dictionary, type_check):
    total_sentiments = {brand: sum(sentiments.values()) for brand, sentiments in sentiment_dictionary.items()}

    # Calculate normalized sentiment scores and popularity score for each brand
    popularity_scores = {}
    for brand, sentiments in sentiment_dictionary.items():
        total = total_sentiments[brand]
        positive_score = sentiments['positive'] / total if total > 0 else 0
        negative_score = sentiments['negative'] / total if total > 0 else 0
        neutral_score = sentiments['neutral'] / total if total > 0 else 0
        
        # Penalize brands with fewer counts using logarithmic scaling
        penalization_factor = math.log10(total + 1)  # Adding 1 to prevent division by zero
        popularity_score = ((positive_score * 0.65) + (neutral_score * 0.15) - (negative_score * 0.2)) * penalization_factor
        if type_check == "general":
            popularity_scores[brand[0]] = popularity_score
        else:
            popularity_scores[brand] = popularity_score

    # Sort brands by popularity score
    sorted_brands = sorted(popularity_scores.items(), key=lambda x: x[1], reverse=True)
    return popularity_scores

################################### End defined functions ###################################

# Iterate through the Reddit dataframe and collect all the sentiment scores
# for its content, title and the top comments

def main():
    initial_memory_usage = get_initial_memory_usage()
    if initial_memory_usage is None:
        print("Failed to retrieve initial memory usage.")
        return

    main2()

    final_memory_usage = get_final_memory_usage()
    if final_memory_usage is None:
        print("Failed to retrieve final memory usage.")
        return
    
    print("Final memory usage:", final_memory_usage, "MB")
    
    # Step 5: Calculate the difference
    memory_usage_difference = calculate_memory_usage_difference(initial_memory_usage, final_memory_usage)
    print("RAM used by the script:", memory_usage_difference, "MB")

# Record the starting time
def main2():
    
    s3_client = boto3.client('s3')
    start_time = time.time()
    reddit = praw.Reddit(
        client_id= clientID,
        client_secret= clientSecret,
        user_agent='reg',
    )

    subreddit = reddit.subreddit('appliances')

    submission_info_list = []
    futures = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for submission in subreddit.search("best", limit=50):
            futures.append(executor.submit(get_submission_info, submission))
        
        first_search_time = time.time()
        print(f"First search time: {first_search_time - start_time}")

        for submission in subreddit.search("good", limit=100):
            futures.append(executor.submit(get_submission_info, submission))

        second_search_time = time.time()
        print(f"Second search time: {second_search_time - first_search_time}")

        for submission in subreddit.search("recommend", limit=100):
            futures.append(executor.submit(get_submission_info, submission))

        third_search_time = time.time()
        print(f"Third search time: {third_search_time - second_search_time}")

        for submission in subreddit.search("worth", limit=100):
            futures.append(executor.submit(get_submission_info, submission))

        fourth_search_time = time.time()
        print(f"Fourth search time: {fourth_search_time - third_search_time}")

        for submission in subreddit.search("advice", limit=100):
            futures.append(executor.submit(get_submission_info, submission))

        fifth_search_time = time.time()
        print(f"Fifth search time: {fifth_search_time - fourth_search_time}")
    
    # Retrieve results as they become available
    for future in concurrent.futures.as_completed(futures):
        submission_info_list.append(future.result())

    df = pd.DataFrame(submission_info_list)
    total_time = time.time() - start_time
    print(f"Total time: {total_time}")
    print(len(submission_info_list))
    # need to add to s3 and get the csv file

    bucket_name = "fyp-interest-forecasts"
    response = s3_client.get_object(Bucket=bucket_name, Key="starbuy_categories/cleaned_brands.csv")
    csv_content = response['Body'].read().decode('utf-8')
    csv_content = csv_content.strip().split('\n')[1:]
    unique_brands = [row.split(',')[1] for row in csv_content]

    unique_categories = [
        "Air Conditioner",
        "Air Fryer",
        "Air Purifier",
        "Bread Maker",
        "Blender",
        "Clothes Steamer",
        "Coffee Machine",
        "Cooktop",
        "Dishwasher",
        "Dryer",
        "Electric Kettle",
        "Espresso Machine",
        "Fan",
        "Food Processor",
        "Griddle",
        "Grill",
        "Hand Mixer",
        "Heater",
        "Humidifier",
        "Ice Cream Maker",
        "Iron",
        "Juicer",
        "Microwave",
        "Oven",
        "Range Hood",
        "Refrigerator",
        "Rice Cooker",
        "Robot Vacuum",
        "Slow Cooker",
        "Smart Doorbell",
        "Smart Lighting",
        "Smart Lock",
        "Smart Thermostat",
        "Sound System",
        "Stand Mixer",
        "Television",
        "Toaster",
        "Vacuum Cleaner",
        "Waffle Maker",
        "Washing Machine",
        "Water Heater",
        "Water Purifier",
        "Washer"
    ]

    sentiment_collection = {}
    sentimentBrand_count = 0

    for idx, row in df.iterrows():
        if row['Top_Comments'] != []:
            commentsThread = row['Top_Comments']
            commentsThreadDates = row['Comments_Dates']
            for i in range(len(commentsThread)):
                get_brand_and_category(sentiment_collection, unique_brands, commentsThread[i], unique_categories, commentsThreadDates[i])
                sentimentBrand_count += 1

        if row['Content'] != "":
            get_brand_and_category(sentiment_collection, unique_brands, row['Content'], unique_categories, row['Submission_Date'])
            sentimentBrand_count += 1

    # To combine the sentiment scores of the same brand to have a general understanding of which brands are more popular
    combined_sentiment_collection = {}
    brands_with_categories = set()
    for key in sentiment_collection.keys():
        brand, category = key
        if category != '':
            brands_with_categories.add(brand)

    for brand, category in sentiment_collection.keys():
        for key in sentiment_collection.keys():
            if key[0] == brand:
                for sentiment in sentiment_collection[key]:
                    if (brand, '') not in combined_sentiment_collection:
                        combined_sentiment_collection[(brand, '')] = {}
                    combined_sentiment_collection[(brand, '')][sentiment] = combined_sentiment_collection[(brand, '')].get(sentiment, 0) + sentiment_collection[key][sentiment]

    nlp_time = time.time() - start_time
    print('nlp is done at ' + str(nlp_time) + ' seconds')

    # Getting hardware zone data

    new_files = []
    all_data = []
    date = datetime.now().date()
    date_collected = str(date)
    prefix = "HardwareZone"
    bucket_name = "cleaned-data-fyp"

    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    for page in pages:
        for obj in page['Contents']:
            new_files.append(obj['Key'])

    # print(new_files)

    for file in new_files[1:]:
        response = s3_client.get_object(Bucket=bucket_name, Key=file)
        data = response['Body'].read().decode('utf-8')
        data = json.loads(data)
        all_data += data

    clean_data = []

    for entry in all_data:
        clean_data.append(entry)

    hardware_df = pd.DataFrame(clean_data)
    df_hardware = hardware_df.drop(columns=['error'])
    df_hardware.dropna(inplace=True)
    df_hardware = df_hardware.reset_index(drop=True)

    hardware_brandCat = []
    brand_cat = ""
    for idx, row in df_hardware.iterrows():
        brand_cat = get_brand_and_category_noSentiment(row['title'], row['description'], unique_categories, unique_brands)

        if brand_cat not in hardware_brandCat and brand_cat != '':
            hardware_brandCat.append(brand_cat)

    ## Purpose: To create a dictionary of brand sentiments based on their category
    df_legend = {}
    found_categories = set()
    for brand_cat, sentiments in sentiment_collection.items():
        brand, category = brand_cat
        
        if category == "":
            continue

        df_name = "df_" + category
        found_categories.add(category)
        
        if df_name not in df_legend:
            df_legend[df_name] = {}
        
        if brand not in df_legend[df_name]:
            df_legend[df_name][brand] = {"positive": sentiments["positive"], "neutral": sentiments["neutral"], "negative": sentiments["negative"]}
        else:
            # If brand already exists, sum up sentiments
            df_legend[df_name][brand]["positive"] += sentiments["positive"]
            df_legend[df_name][brand]["neutral"] += sentiments["neutral"]
            df_legend[df_name][brand]["negative"] += sentiments["negative"]

    dfs = {}

    # Iterate over the dictionary
    for key, value in df_legend.items():
        
        final_df = pd.DataFrame(value).transpose()
        dfs[key] = final_df

    ## Purpose: To get the popularity scores of the brands in each category and scale them
    pop_col_list = []
    for df_name, internal_df in df_legend.items():
        pop_col = get_popular_score(internal_df, "category")
        df_category = df_name[3:]

        pop_col_list.append([pop_col, df_category])

    ## Adding in advertisement data from hardware zone to have more weight in popularity
    for column, category in pop_col_list:
        for brand, cat in hardware_brandCat:
            if cat == category:
                if brand not in column:
                    column[brand] = 0.3

                else:
                    column[brand] += 0.3

    ## Scaling the popularity scores        
    scaled_pop_col_list = []
    for pop_list in pop_col_list:
        scaled_scores = min_max_scaling(pop_list[0])
        scaled_pop_col_list.append(scaled_scores)

    ## Purpose: To add the popularity scores to the dataframes
    for i in range(len(scaled_pop_col_list)):
        target_df = dfs[list(dfs.keys())[i]]
        target_df['popularity'] = pd.Series(scaled_pop_col_list[i], index=target_df.index)

    popularity_time = time.time() - start_time
    print('popularity is done at ' + str(popularity_time) + ' seconds')

    ############################ JSON output section ############################


    ### Ouptut for json file on general popularity of brands
    popular_brands = get_popular_score(combined_sentiment_collection, "general")
    scaled_scores = min_max_scaling(popular_brands)

    # Convert to JSON
    json_data = json.dumps(dict(scaled_scores), indent=4)
    outputLine = date_collected + "_general-popular-brands.json"
    s3_client.put_object(Bucket=bucket_name, Key=f'RedditHwZAnalysis/{outputLine}', Body=json_data)

    # Iterate over the dataframes in the dfs dictionary
    for df_name, final_df in dfs.items():
        # Convert DataFrame to JSON
        json_data = final_df.to_json(orient="index")
        
        # Add to s3 bucket
        s3_client.put_object(Bucket=bucket_name, Key=f'RedditHwZAnalysis/{date_collected}_{df_name}.json', Body=json_data)
        
    # convert found_categories to a json file
    my_list = list(found_categories)

    # Specify the output file path
    output_file_path = date_collected + "_found-categories.json"

    s3_client.put_object(Bucket=bucket_name, Key=f'RedditHwZAnalysis/{output_file_path}', Body=json_data)
    
    final_time = time.time() - start_time
    
    print(f"First search time {first_search_time - start_time}")
    print(f"Second search time {second_search_time - first_search_time}")
    print(f"Third search time {third_search_time - second_search_time}")
    print(f"Fourth search time {fourth_search_time - third_search_time}")
    print(f"Fifth search time {fifth_search_time - fourth_search_time}")
    print(f"Time for stupid nlp {nlp_time}")
    print(f"Time for popularity {popularity_time}")
    print(f"Total time {final_time}")

if __name__ == '__main__':
    main()