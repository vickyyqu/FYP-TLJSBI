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
from selenium.webdriver.chrome.service import Service
import random

date = datetime.now().date()
num = random.randint(1,1000)
addToURI = f"s3://raw-data-fyp/MDS/{date}_{num}_MDS.json"

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
class MegaDiscountStoreSpider(scrapy.Spider):
    name = 'megadiscountstore'
    allowed_domains = ['megadiscountstore.com.sg']
    # start_urls = ['https://megadiscountstore.com.sg/collections/refrigerator?page=1']
    custom_settings = custom_settings


    # ALL URLS {
    # "urls": [
    #     "https://megadiscountstore.com.sg/collections/refrigerator?page=1",
    #     "https://megadiscountstore.com.sg/collections/top-load-washing-machine?page=1",
    #     "https://megadiscountstore.com.sg/collections/front-load-washing-machine?page=1",
    #     "https://megadiscountstore.com.sg/collections/standing-cooker?page=1",
    #     "https://megadiscountstore.com.sg/collections/induction-cooker?page=1",
    #     "https://megadiscountstore.com.sg/collections/tv?page=1",
    #     "https://megadiscountstore.com.sg/collections/dryer?page=1",
    #     "https://megadiscountstore.com.sg/collections/fan?page=1",
    #     "https://megadiscountstore.com.sg/collections/ovens?page=1",
    #     "https://megadiscountstore.com.sg/collections/water-purifier?page=1",
    #     "https://megadiscountstore.com.sg/collections/air-con?page=1",
    #     "https://megadiscountstore.com.sg/collections/vacuum-cleaner?page=1",
    #     "https://megadiscountstore.com.sg/collections/coffee-maker-machine?page=1",
    #     "https://megadiscountstore.com.sg/collections/air-purifier?page=1",
    #     "https://megadiscountstore.com.sg/collections/digital-door-lock?page=1",
    #     "https://megadiscountstore.com.sg/collections/airfryer-deep-fryer?page=1"
    # ]
    # }

    # First Batch{
    # "urls": [
    #     "https://megadiscountstore.com.sg/collections/refrigerator?page=1",
    #     "https://megadiscountstore.com.sg/collections/top-load-washing-machine?page=1",
    #     "https://megadiscountstore.com.sg/collections/front-load-washing-machine?page=1",
    #     "https://megadiscountstore.com.sg/collections/standing-cooker?page=1",
    #     "https://megadiscountstore.com.sg/collections/induction-cooker?page=1",
    #     "https://megadiscountstore.com.sg/collections/tv?page=1",
    #     "https://megadiscountstore.com.sg/collections/dryer?page=1",
    #     "https://megadiscountstore.com.sg/collections/fan?page=1"
    # ]
    # }


    #   Second Batch{
    # "urls": [
    #     "https://megadiscountstore.com.sg/collections/ovens?page=1",
    #     "https://megadiscountstore.com.sg/collections/water-purifier?page=1",
    #     "https://megadiscountstore.com.sg/collections/air-con?page=1",
    #     "https://megadiscountstore.com.sg/collections/vacuum-cleaner?page=1",
    #     "https://megadiscountstore.com.sg/collections/coffee-maker-machine?page=1",
    #     "https://megadiscountstore.com.sg/collections/air-purifier?page=1",
    #     "https://megadiscountstore.com.sg/collections/digital-door-lock?page=1",
    #     "https://megadiscountstore.com.sg/collections/airfryer-deep-fryer?page=1"
    # ]
    # }


    

    def __init__(self, *args, **kwargs):
        self.start_urls = kwargs.get('urls', [])
        self.start_urls = self.start_urls.split(",")
        print("STARTURL 0:", end="")
        print(self.start_urls[0])

        service = Service(executable_path=r'/opt/chromedriver')
        # Uncomment the next two lines if you don't want a browser window to open
        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-first-run')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument("--remote-debugging-port=9222")
        self.driver = webdriver.Chrome(service=service, options=options)

        
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





        #SELENIUM Pagination [20/31/23]
        # try:
        #     WebDriverWait(self.driver, 10).until(
        #         EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "pagination__next")]'))
        #     )
        #     next_page = WebDriverWait(self.driver, 20).until(
        #         EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "pagination__next")]')))
            
        #     if next_page:
        #         try:
        #             next_page.click()
        #             yield scrapy.Request(self.driver.current_url, callback=self.parse)
                
        #         except StaleElementReferenceException:
        #             # If the element goes stale, this block will catch it
        #             # Handle the exception, possibly by re-running this method or by returning the data collected so far
        #             return

        # except StaleElementReferenceException:
        #     # Element is stale, so re-find the element on the page and try clicking again
        #     next_page = WebDriverWait(self.driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "pagination__next")]'))
        #     )
        #     next_page.click()
        
        # except NoSuchElementException:
        #     self.driver.quit()  # No more pages, quit the driver