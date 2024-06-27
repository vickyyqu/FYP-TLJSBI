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
from scrapy import Selector
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

class BestarFanSpider(scrapy.Spider):
    name = 'bestdenki'
    allowed_domains = ['www.bestdenki.com.sg']
    start_urls = [
                # "https://www.bestdenki.com.sg/home-appliances/fridge/normal-fridge.html", ## Fridge
                # "https://www.bestdenki.com.sg/home-appliances/washer.html", ## Washer Dryer
                # "https://www.bestdenki.com.sg/kitchen-cooking-appliances/cookers/burner.html", ## Gas cooker
                # "https://www.bestdenki.com.sg/kitchen-cooking-appliances/steamboat-induction-cooker.html", ## Induction cooker
                # "https://www.bestdenki.com.sg/tv-audio/tv.html", ## TV
                # "https://www.bestdenki.com.sg/fans-air-care/fans.html", ## Fans
                # "https://www.bestdenki.com.sg/kitchen-cooking-appliances/oven.html", ## Oven
                # "https://www.bestdenki.com.sg/kitchen-cooking-appliances/cookers/cookerhood.html", ## Hood
                # "https://www.bestdenki.com.sg/aircon-air-care/air-con.html", ## Air con
                # "https://www.bestdenki.com.sg/home-appliances/vacuum.html", ## Vacuum
                # "https://www.bestdenki.com.sg/kitchen-cooking-appliances/coffee-machine.html", ## Coffee machine
                # "https://www.bestdenki.com.sg/instantsearch/result/?q=digital+lock", ## Smart lock
                "https://www.bestdenki.com.sg/kitchen-cooking-appliances/toaster-fryers.html" ## Toaster Fryer
                ]
    
    category = "Toaster Fryer"
    label = category.replace(' ', '_')
    date = datetime.now().date()
    addToURI = f"s3://raw-data-fyp/BestDenki/{label}_links_BestDenki.json"

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

        items = None
        next_page_element = None

        try:
            items = response.xpath('.//li[contains(@class, "product-item-info") or contains(@class, "product-item")]')

        except Exception as e:
            logging.error("Error retrieving products")
            logging.error(f"Error processing URL: {response.url}")
            logging.error(f"Error details: {e}")

        try:
            next_page_element = response.xpath('.//li[contains(@class, "pages-item-next")]//a/@href').get()

        except Exception as e:
            pass

        logging.info(f"Site URL: {response.url}")
        logging.info(f"No. of items: {str(len(items))}")

        if items:
            for item in items:
                try:
                    prod_link = item.xpath('.//a/@href').get()

                    if "https" in prod_link:
                        yield {
                            'prod_url': prod_link,
                            'site_url': response.url,
                            'category': self.category
                        }

                except Exception as e:
                    logging.error("Error retrieving product URL")
                    logging.error(f"Error processing URL: {response.url}")
                    logging.error(f"Error details: {e}")

        else:
            logging.error("Product item info not found")
            logging.error(f"Error processing URL: {response.url}")


        if next_page_element:
            next_page_url = response.urljoin(next_page_element)
            yield scrapy.Request(url=next_page_url, callback=self.parse)