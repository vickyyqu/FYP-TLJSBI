# Original MDS scraper, scrapes items (manually insert url)

## History
# 24/12: Created the scraper, including pagination with Selenium 
# 8/1: Modified from Selenium pagination to Scrapy pagination 

## Last modified: Mon 8 Jan, Caitlin

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
import logging
from datetime import date
import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from datetime import datetime


class MegaDiscountStoreSpider(scrapy.Spider):
    name = 'megadiscountstore'
    allowed_domains = ['megadiscountstore.com.sg']
    start_urls = ['https://megadiscountstore.com.sg/collections/vacuum-cleaner?page=1']

    ## to scrape
    # scrapy crawl megadiscountstore -o output/MDS/080224_refrigerator_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_top-load-washing-machine_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_front-load-washing-machine_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_standing-cooker_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_induction-cooker_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_tv_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_dryer_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_fan_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_ovens_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_water-purifier_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_air-con_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_vacuum-cleaner_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_coffee-maker-machine_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_air-purifier_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_digital-door-lock_mds.json -t json
    # scrapy crawl megadiscountstore -o output/MDS/080224_airfryer-deep-fryer_mds.json -t json

    # refrigerator ; top-load-washing-machine ; front-load-washing-machine ; standing-cooker ; induction-cooker ; tv ; dryer ; fan ; ovens ; water-purifier ; air-con ; vacuum-cleaner ; coffee-maker-machine ; air-purifier ; digital-door-lock ; airfryer-deep-fryer
    
    date = datetime.now().strftime('%d%m%y')
    addToURI = f"s3://raw-data-fyp/MDS/{date}_refrigerator_MDS.json"

    custom_settings = {
        "FEED_URI": addToURI,
        "FEED_FORMAT": "json",
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://megadiscountstore.com.sg/',
            'Referer': 'https://megadiscountstore.com.sg/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        },
    }

    def __init__(self):
        chrome_options = Options()
        # Uncomment the next two lines if you don't want a browser window to open
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)

        
    def parse(self, response):
        next_page = response.xpath('//a[contains(@class, "pagination__next")]')
        current_page_number = response.url.split("page=")[-1].split("&")[0]

        try:
            self.driver.get(response.url)

            # Wait for the items to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@data-product-id]'))
            )

            # Give the page time to load
            time.sleep(5)

            
            # Identify product items list
            products = self.driver.find_elements(By.XPATH, '//div[contains(@class, "product-block") and @data-product-id]')


            for product in products:
                
                try:
                    sel = Selector(text=product.get_attribute('outerHTML'))

                    pattern = r'/([^/]+)/page-{}'.format(current_page_number)
                    extracted = re.search(pattern, response.url)
                    if extracted:
                        result = extracted.group(1).replace('-', ' ')
                        category = result
                    else: 
                        category = None
                    
                    match = re.search(r'collections/([\w-]+?)(?=\?|$)', response.url)
                    if match:
                        category = match.group(1).replace('-', ' ')
                    else: 
                        category = 'No category'

                    brand = sel.xpath('//div[contains(@class, "vendor")]/text()').extract_first()

                    model = sel.xpath('//div[contains(@class, "product-block__title")]/text()').extract_first()

                    # Convert discounted price to a float, with a check for empty strings
                    discountedPriceText = sel.xpath('//span[contains(@class, "product-price__amount--on-sale")]/text()').extract_first()

                    if discountedPriceText:
                        discountedPrice = float(re.sub(r'[^\d.]', '', discountedPriceText))
                        discountedPrice = round(discountedPrice, 2)

                    else:
                        discountedPrice = None

                    # Convert listed price to a float, with a check for empty strings
                    listedPriceText = sel.xpath('//span[contains(@class, "product-price__compare")]/text()').extract_first()
                    
                    if listedPriceText:
                        listedPrice = float(re.sub(r'[^\d.]', '', listedPriceText))
                        listedPrice = round(listedPrice, 2)

                    else:
                        listedPriceText = sel.xpath('//span[contains(@class, "product-price__amount")]/text()').extract_first()
                        listedPrice = float(re.sub(r'[^\d.]', '', listedPriceText))
                        listedPrice = round(listedPrice, 2)

                    # Get today's date
                    dateCollected = date.today()

                    if brand: 
                        yield {
                            'platform': 'Mega Discount Store',
                            'category': category,
                            'brand': brand,
                            'model': model,
                            'discounted price': discountedPrice,
                            'listed price': listedPrice,
                            'date collected': dateCollected
                        }


                except Exception as e:
                    # Log the error along with the URL that caused it
                    logging.error(f"Error processing URL: {response.url}")
                    logging.error(f"Error details: {e}")
                    yield {
                        'url': response.url,
                        'error': str(e),
                    }

        except Exception as e:
                logging.error(f"Error processing product: {e}")



        #SCRAPY Pagination: increment the page number in the URL and yield a new request [7/1/24]
       
        if current_page_number.isdigit() and next_page:
            next_page_number = int(current_page_number) + 1
            next_page_url = re.sub(r"page=\d+", f"page={next_page_number}", response.url)

            # Optionally, check some condition to stop pagination
            # if next_page_number <= MAX_PAGE:
            yield scrapy.Request(url=next_page_url, callback=self.parse)