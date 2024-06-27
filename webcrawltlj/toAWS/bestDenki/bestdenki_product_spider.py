# mywebcrawler/spiders/bestarfan_spider.py
## History
# 21/12 Added multi-page scraper to scrape brand information + added more start_urls to scrape up to page 5 
# 24/12 Added "platform", "dateCollected", "model", "sku" scrapped fields
# 29/12 Multi-page scraper

## Created by: Vicky
## Last modified: Thur 29 Dec, Vicky
## Description: Scrape bestdenki.com and collect information about product name, original price, listed price, brand name, description for the categories: home appliances and kitchen cooking appliances

import random
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import logging
import requests
import json
from scrapy import Selector
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import boto3

class BestarFanSpider(scrapy.Spider):
    name = 'bestdenkiproduct'
    allowed_domains = ['www.bestdenki.com.sg']

    serial_no = random.randint(1,1000)

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

    def __init__(self, *args, **kwargs):
        arg_urls= kwargs.get('urls', [])
        arg_urls = arg_urls.split(",")
        file_name = arg_urls[0]
        print("FILENAME HERE")
        print(file_name)

        bucket_name = 'raw-data-fyp'
        # file_name = 'BestDenki/2024-02-05_Vacuum_links_BestDenki.json'
        s3 = boto3.client('s3')

        file_response = s3.get_object(Bucket= bucket_name, Key = file_name)

        prod_urls = []
        data = file_response['Body'].read() .decode( 'utf-8')
        data = json.loads(data)
        print(type(data))


        for row in data:
            # Check if the row contains 'prod_url' key
            if 'prod_url' in row:
                # Append the 'prod_url' value to the list
                prod_urls.append(row['prod_url'])

        # print(prod_urls)
        self.start_urls = prod_urls
        # print("URLS HERE")
        # print(self.start_urls)

    # def start_requests(self):
    #     # Read URLs from the JSON file
    #     json_file_path = "output/bestdenki/product_links_bestdenki.json"
    #     with open(json_file_path, 'r') as file:
    #         data = json.load(file)
    #         for row in data:
    #             if 'prod_url' in row:
    #                 yield scrapy.Request(url=row['prod_url'], callback=self.parse)

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


    # def __init__(self):

    #     chrome_options = Options()
    #     # Uncomment the next two lines if you don't want a browser window to open
    #     chrome_options.add_argument("--headless")
    #     chrome_options.add_argument("--disable-gpu")
    #     self.driver = webdriver.Chrome(options=chrome_options)


    # def parse(self, response):

    #     def remove_commas(input_string):
    #         return input_string.replace(',', '')
        
    #     def get_float(n):
    #         n = remove_commas(n)
    #         temp = n.split("$")
    #         return float(temp[-1])
        
    #     # Open the website
    #     self.driver.get(response.url)

    #     # Wait for the items to load
    #     WebDriverWait(self.driver, 5).until(
    #         EC.presence_of_all_elements_located((By.XPATH, './/section[@id="maincontent"]'))
    #     )
        
    #     new_html = self.driver.page_source
    #     sel = Selector(text=new_html)

        
    #     try:
    #         name = sel.xpath('.//h1[@class="product-name"]').css('::text').get()
    #         final_price = sel.xpath('.//div//span[@class="special-price"]//span//span//span[@class="price"]').css('::text').get()
    #         old_price_element = sel.xpath('.//div//span[@class="old-price"]//span//span//span[@class="price"]')

    #         if old_price_element:
    #             org_price = old_price_element.css('::text').get()
    #         else:
    #             org_price = final_price


    #         brand = sel.xpath('normalize-space(.//div[@class="brand-name"])').get()
    #         cleaned_brand = re.sub(r'\bBRAND\b', '', brand, flags=re.IGNORECASE).strip()

    #         # sku = sel.xpath('.//span[@itemprop="sku"]').css('::text').get()
    #         model = sel.xpath('.//div[@class="webmodeldescription"]').css('::text').get()
    #         prod_name = name.strip().replace('\n', '').replace('\t', '')

    #         yield {
    #             'name': prod_name,
    #             'brand': cleaned_brand,
    #             'model': model,
    #             'discountedPrice': get_float(final_price),
    #             'listedPrice': get_float(org_price),
    #             'platform': "Best Denki",
    #             'dateCollected': datetime.now()
    #         }

    #         logging.info(f"Success!")
    #         logging.info(f"Product scraped: {prod_name}")

    #     except Exception as e:
    #         # Log the error along with the URL that caused it
    #         logging.error("Error retrieving product details")
    #         logging.error(f"Error processing URL: {response.url}")
    #         logging.error(f"Error details: {e}")
    

