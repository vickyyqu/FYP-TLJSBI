# mywebcrawler/spiders/bestarfan_spider.py
## History
# 21/12 Added multi-page scraper to scrape brand information + added more start_urls to scrape up to page 5 
# 24/12 Added "platform", "dateCollected", "model", "sku" scrapped fields
# 29/12 Multi-page scraper

## Created by: Vicky
## Last modified: Thur 29 Dec, Vicky
## Description: Scrape bestdenki.com and collect information about product name, original price, listed price, brand name, description for the categories: home appliances and kitchen cooking appliances

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import logging
import json
from scrapy import Selector
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

class BestarFanSpider(scrapy.Spider):
    json_file_path = "output/bestdenki/product_links_bestdenki.json"
    prod_urls = []

    with open(json_file_path, 'r') as file:
        data = json.load(file)

        for row in data:
            if 'prod_url' in row:
                prod_urls.append(row['prod_url'])

    name = 'bestdenkiproduct'
    allowed_domains = ['www.bestdenki.com.sg']
    start_urls = prod_urls
    
    date = datetime.now().date()
    addToURI = f"s3://raw-data-fyp/BestDenki/{date}_BestDenki.json"

    custom_settings = {
        "FEED_URI": addToURI,
        "FEED_FORMAT": "json",
        'ROBOTSTXT_OBEY': False,
        'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # 'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'www.bestdenki.com.sg',
            'Referer': 'www.bestdenki.com.sg',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
    }

    def parse(self, response):
        def remove_commas(input_string):
            return input_string.replace(',', '')

        def get_float(n):
            n = remove_commas(n)
            temp = n.split("$")
            return float(temp[-1])

        try:
            name = response.xpath('.//h1[@class="product-name"]').css('::text').get()
            final_price = response.xpath('.//div//span[@class="special-price"]//span//span//span[@class="price"]').css('::text').get()
            old_price_element = response.xpath('.//div//span[@class="old-price"]//span//span//span[@class="price"]')

            if old_price_element:
                org_price = old_price_element.css('::text').get()
            else:
                org_price = final_price

            brand = response.xpath('normalize-space(.//div[@class="brand-name"])').get()
            cleaned_brand = re.sub(r'\bBRAND\b', '', brand, flags=re.IGNORECASE).strip()

            model = response.xpath('.//div[@class="webmodeldescription"]').css('::text').get()
            prod_name = name.strip().replace('\n', '').replace('\t', '')

            yield {
                'name': prod_name,
                'brand': cleaned_brand,
                'model': model,
                'discountedPrice': get_float(final_price),
                'listedPrice': get_float(org_price),
                'platform': "Best Denki",
                'dateCollected': datetime.now()
            }

            logging.info(f"Success!")
            logging.info(f"Product scraped: {prod_name}")

        except Exception as e:
            # Log the error along with the URL that caused it
            logging.error("Error retrieving product details")
            logging.error(f"Error processing URL: {response.url}")
            logging.error(f"Error details: {e}")


