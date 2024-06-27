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
from reddit_functions import get_submission_info

# Record the starting time
start_time = time.time()

reddit = praw.Reddit(
    client_id= clientID,
    client_secret= clientSecret,
    user_agent='reg',

)

subreddit = reddit.subreddit('appliances')

if __name__ == '__main__':
    submission_info_list = []

    count = 0
    max_submissions = 800
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for submission in subreddit.search("best", limit=max_submissions):
            futures.append(executor.submit(get_submission_info, submission))
            count += 1
            if count >= max_submissions:
                break
        
        # Retrieve results as they become available
        for future in concurrent.futures.as_completed(futures):
            submission_info_list.append(future.result())

df = pd.DataFrame(submission_info_list)
print(df)
# df.to_json('raw_redditData.json', orient='records')