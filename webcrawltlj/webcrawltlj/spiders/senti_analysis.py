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

## Purpose: Get sentiment analysis
def get_senti_analysis(sentiment_collection, sentence, brand_cat, max_length=512):
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

    sentiment_collection[brand_cat][sentiment] += 1

    return sentiment_collection