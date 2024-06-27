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
from senti_analysis import get_senti_analysis

def get_brand_and_category(sentiment_collection, brands, sentences, categories):
    with concurrent.futures.ProcessPoolExecutor() as executor:  # Use ProcessPoolExecutor instead of ThreadPoolExecutor
        futures = []  # List to store futures
        
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

                cat = cat.replace(" ", "").lower()
                brand_cat = (brand, cat)
                
                if brand_cat not in sentiment_collection:
                    sentiment_collection[brand_cat] = {"positive": 0, "negative": 0, "neutral": 0}
                
                # Submit task to executor and store future
                future = executor.submit(get_senti_analysis, sentiment_collection, sentences, brand_cat)
                futures.append(future)
        
        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            # Merge sentiment_collection with the result if needed (depends on get_senti_analysis implementation)

    return sentiment_collection