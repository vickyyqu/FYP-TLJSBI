## History
# 19/12: Created the base scraper, could not retrieve any data
# 20/12: Modified to override robot.txts code under custom_setting
# 21/12: Attempted to use Selenium to click on the next pages, progress made but getting timed out
# 23/12: Fixed the timeout issue, added in code to scroll to the page navigation section and click on the subsequent pages
# 05/01: Edited the code to get the correct brand and model of the product. Testing scraping of other categories. Still facing issues with scraping Washing Machines search
# 06/01: Fixed the issue with scraping Washing Machines search. Scraper working for all categories
# 10/01: Modified to use Scrapy pagination instead of Selenium pagination
# 10/01: Modified to scrape multiple categories in one run and added category name in the output yield
# 13/01: After meeting client and got the green light for each execution to scrape only 1 category, modified code to back to scrape only 1 category
# 05/02: Modified code to accommodate different Courts website layouts for different categories and URLs
# 06/02: Bug fix to handle exception for scraping last page of results

## Last modified: Tuesday 06 Feb, Renee

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
import logging
import re
from selenium.common.exceptions import TimeoutException
from datetime import datetime

class CourtsSpiderSpider(scrapy.Spider):
    name = "courts"
    allowed_domains = ["courts.com.sg"]
    start_urls = ["https://www.courts.com.sg/catalogsearch/result/index/?p=1&q=smart+lock"] #URL scraper will scrape through

    #URLs
    #https://www.courts.com.sg/catalogsearch/result/?p=1&q=TV
    #https://www.courts.com.sg/catalogsearch/result/index/?p=1&q=fridge
    #https://www.courts.com.sg/home-appliances/large-appliances/washing-machines?p=1
    #https://www.courts.com.sg/catalogsearch/result/index/?p=1&q=gas+cooker
    #https://www.courts.com.sg/catalogsearch/result/?p=1&q=Induction+cooker
    
    #https://www.courts.com.sg/catalogsearch/result/?p=1&q=dryer
    #https://www.courts.com.sg/catalogsearch/result/?p=1&q=hood
    #https://www.courts.com.sg/all-ovens?p=1
    #https://www.courts.com.sg/catalogsearch/result/index/?p=1&q=fans
    #https://www.courts.com.sg/catalogsearch/result/index/?p=1&q=water+purifier
    
    #https://www.courts.com.sg/home-appliances/cooling-air-care/air-con?p=1
    #https://www.courts.com.sg/home-appliances/small-appliances/vacuum-cleaner?p=1
    #https://www.courts.com.sg/home-appliances/cooling-air-care/air-treatment?p=1&type1=Air+Purifier
    #https://www.courts.com.sg/catalogsearch/result/index/?p=1&q=smart+lock
    #https://www.courts.com.sg/catalogsearch/result/?type1=Fryer&q=fryer

    
    
    if "catalogsearch" in start_urls[0]:
        category = start_urls[0].split("q=")
        if "+" in category[1]:
            category = category[1].split("+")
            category = category[0] + category[1][0].upper() + category[1][1:]#replace "+" with " " and capitalize the first letter of the second word
        else:
            category = category[1]
    elif "home-appliances" in start_urls[0]:
        if "type" in start_urls[0]:
            category = start_urls[0].split("/")
            category = category[5]
            category = category.split("type1=")[1]
            if '+' in category:
                category = category.split("+")
                category = category[0] + category[1][0].upper() + category[1][1:]
            else:
                category = category
        else:
            category = start_urls[0].split("/")
            category = category[5]
            category = category.split("?")[0]
            if '-' in category:
                category = category.split("-")
                category = category[0] + category[1][0].upper() + category[1][1:]
    else:
        category = start_urls[0].split("/")
        category = category[3]
        category = category.split("?")[0]
        if '-' in category:
            category = category.split("-")
            category = category[1]

    

    date = datetime.now().date()
    addToURI = f"s3://raw-data-fyp/Courts/{date}_{category}_courts.json"
    
    custom_settings = {
        "FEED_URI": addToURI,
        "FEED_FORMAT": "json",
        'ROBOTSTXT_OBEY': False,
        'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Origin': 'https://courts.com.sg/',
                'Referer': 'https://courts.com.sg/',
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
        try:
            #Open the website
            self.driver.get(response.url)

            # Wait for the items to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-container="product-grid"]'))
            )

            #Give the page time to load
            time.sleep(5)

            #extract the title which contains the platform name
            platform = self.driver.find_element(By.XPATH, '//a[@class="logo"]')
            platform = platform.get_attribute('title')

            #category name
            if 'catalogsearch' in response.url:
                category_text = self.driver.find_element(By.XPATH, '//h1[@class="page-title"]/span').text
                category = category_text.split(':')[1].strip()
                category = category[1:-1]
            elif 'home-appliances' in response.url:
                if "type" in response.url:
                    category = self.driver.find_element(By.XPATH, '//div[@data-scope-key="type1"]/ol/li[1]/a//label/span[1]').text
                else:
                    category = self.driver.find_element(By.XPATH, '//h1[@data-content-type="heading"]').text
                    if ':' in category:
                        category = category.split(':')[0].strip()
                    else:
                        category = category.strip()
            else:
                category = self.driver.find_element(By.XPATH, '//li[contains(@class, "item category")]/strong').text

            #Now, we'll scrape the product names and prices
            products = self.driver.find_elements(By.XPATH, '//div[@data-container="product-grid"]')

            for product in products:
                try:
                    sel = Selector(text=product.get_attribute('outerHTML'))
                    product_name = sel.xpath('//h3[contains(@class, "product-item-name")]/a/text()').extract_first()
                    
                    if product_name:
                        product_name = product_name.strip()

                    else:
                        continue
                
                    if '&' in product_name:
                        brand = ' '.join(product_name.split(' ')[0:3])
                        model = ' '.join(product_name.split(' ')[3:])
                    else:
                        brand = product_name.split(' ')[0]
                        model = ' '.join(product_name.split(' ')[1:])

                    final_price = sel.xpath('//span[@data-price-type="finalPrice"]/span/text()').extract_first()
                    final_price_fraction = sel.xpath('//span[@data-price-type="finalPrice"]/span/span/text()').extract_first()

                    final_price = f"{final_price}{final_price_fraction}" if final_price and final_price_fraction else final_price or final_price_fraction
                    final_price_float = float(''.join(filter(str.isdigit, final_price))) / 100.0

                    listed_price = sel.xpath('//span[@data-price-type="oldPrice"]/span/text()')
                    listed_price_fraction = sel.xpath('//span[@data-price-type="oldPrice"]/span/span/text()')

                    # check if there is a listed price, if there is, get the listed price and calculate the discount percentage
                    if listed_price and listed_price_fraction:
                        listed_price = listed_price.extract_first()
                        listed_price_fraction = listed_price_fraction.extract_first()
                        listed_price = f"{listed_price}{listed_price_fraction}"
                        listed_price_float = float(''.join(filter(str.isdigit, listed_price))) / 100.0

                        discount_percentage = round((1 - final_price_float / listed_price_float) * 100, 2)

                    else: # if there is no listed price, set the listed price to be the same as the final price and set the discount percentage to be 0
                        listed_price_float = final_price_float
                        discount_percentage = 0

                    date_collected = time.strftime("%d/%m/%Y")

                    yield {
                        'Platform': platform,
                        'Category': category,
                        'Brand': brand,
                        'Model': model,
                        'Discounted Price': final_price_float,
                        'Listed Price': listed_price_float,
                        'Discount Percentage': discount_percentage,
                        'Date Collected': date_collected
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

        # MAX_PAGE = 30
        try:
            next_page_arrow = self.driver.find_element(By.XPATH, '//li[@class="item pages-item-next"]')
        except NoSuchElementException:
            # Handle the case when the next page button is not present
            self.log("Next page button not found. Scraping the remaining information and closing the spider.")

        #SCRAPY Pagination: increment the page number in the URL and yield a new request [10/1/24]
        if next_page_arrow:
            current_page_number = response.url.split("p=")[-1].split("&")[0]
            next_page_number = int(current_page_number) + 1
            next_page_url = re.sub(r"p=\d+", f"p={next_page_number}", response.url)

            # Optionally, check some condition to stop pagination
            # if next_page_number <= MAX_PAGE:
            yield scrapy.Request(url=next_page_url, callback=self.parse)