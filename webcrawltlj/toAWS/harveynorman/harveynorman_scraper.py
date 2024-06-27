## History
# 16/12: Created the base scraper
# 19/12: Successfully scraping singular pages
# 29/12: Had to change code due to Harvey Norman changing an element in their website.
# 05/01: Added custom headers to harvey scraper
# 11/01: Caitlin successfully incorporating pagination
# 13/01: Experimenting with headless as current scraper doesn't scrape successfully on headless mode
# 12/02: Headless chrome works now
# 21/02: Added multi-links and fixed category scraping

## Last modified: Tuesday 21 Feb, Justin

import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.chrome.service import Service
import random
import re
import time

date = datetime.now().date()
category = str(random.randint(1, 1000))
addToURI = f"s3://raw-data-fyp/Harvey/{date}_{category}_harvey.json"

custom_settings = {
    "FEED_URI": addToURI,
    "FEED_FORMAT": "json",
    'ROBOTSTXT_OBEY': False,
    'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://www.harveynorman.com.sg',
            'Referer': 'https://www.harveynorman.com.sg/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',   
            'Sec-Fetch-Site': 'cross-site',
        },
    }


class HarveySpider(scrapy.Spider):
    name = "harvey"
    allowed_domains = ["www.harveynorman.com.sg"]
    # start_urls = ['https://www.harveynorman.com.sg/home-appliances/kitchen-appliances-en/fridges/page-1/']
    custom_settings = custom_settings
    # date = datetime.now().date()
    # addToURI = f"s3://raw-data-fyp/{date}_harvey.json"

    # custom_settings = {
    #     "FEED_URI": addToURI,
    #     "FEED_FORMAT": "json",
    #     'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    #     'DEFAULT_REQUEST_HEADERS': {
    #         'Accept': '*/*',
    #         'Accept-Encoding': 'gzip, deflate, br',
    #         'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    #         'Origin': 'https://www.harveynorman.com.sg',
    #         'Referer': 'https://www.harveynorman.com.sg/',
    #         'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    #         'Sec-Ch-Ua-Mobile': '?1',
    #         'Sec-Ch-Ua-Platform': '"Android"',
    #         'Sec-Fetch-Dest': 'empty',
    #         'Sec-Fetch-Mode': 'cors',   
    #         'Sec-Fetch-Site': 'cross-site',
    #     },
    # }

    def __init__(self, *args, **kwargs):
        self.start_urls = kwargs.get('urls', [])
        self.start_urls = self.start_urls.split(",")
        print("STARTURL 0:", end="")
        print(self.start_urls[0])

        service = Service(executable_path=r'/opt/chromedriver')
        # Uncomment the next two lines if you don't want a browser window to open
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36")
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
        # Uncomment the next two lines if you don't want a browser window to open
    
        self.driver.get(response.url)
        WebDriverWait(self.driver, 10)

        close_expression = "//div[@class='ins-editable ins-element-editable']/a[text()='NO, I WANT TO CONTINUE SHOPPING']"


        # wait = WebDriverWait(driver, 5)
        # closeButt = wait.until(EC.presence_of_element_located((By.XPATH, close_expression)))

        # closeButt.click()

        new_html = self.driver.page_source
        response_html = Selector(text=new_html)
    
        breadcrumbs = response_html.xpath("//ul[contains(@class, 'nav-breadcrumbs')]")
        li_elements = breadcrumbs.xpath(".//li").getall()
        last_li = li_elements[-1]

        start_index = last_li.find("<span>") + len("<span>")
        end_index = last_li.find("</span>")

        category = last_li[start_index : end_index]


        # Lists to store product titles and prices
        
        productForms = response_html.xpath("//form[contains(@name,'product_form')]").getall()

        # titles = driver.find_elements(By.XPATH, "//a[@class='product-title']")
        # prices = driver.find_elements(By.XPATH, "//span[@id='sec_discounted_price_60196']")
        # print("PRODUCT FORMS")
        # print(productForms)

        for item in productForms:
        # Extracting text content from HTML

            selector = Selector(text=item)

            titleElement = selector.xpath("//a[@class='product-title']")
            title = titleElement.xpath("text()").get()

            discountedPriceElement = selector.xpath("//span[contains(@id, 'sec_discounted_price')]")
            discounted_price = discountedPriceElement.xpath("text()").get()
            discounted_price = float(discounted_price.split('>', 1)[-1].rsplit('<', 1)[0].replace(',', ''))

            productBrandElement = selector.xpath("//a[contains(@class, 'btn-wishlist')]")
            product_brand = productBrandElement.xpath("@data-product-brand").get()


            priceBeforeElement = selector.xpath("//span[contains(@id, 'sec_list_price')]")
            if bool(priceBeforeElement):
                priceBefore = priceBeforeElement.xpath("text()").get()
            else:
                priceBefore = str(discounted_price)
            priceBefore = float(priceBefore.split('>', 1)[-1].rsplit('<', 1)[0].replace(',', ''))

            discountPercentage = round(((priceBefore - discounted_price) / priceBefore) * 100 , 2)
                
            platform = "Harvey Norman"
            date = datetime.now().date()

            yield {
                'platform': platform,
                'category':category,
                'brand': product_brand,
                'model': title,
                'discountedPrice': discounted_price,
                'listedPrice': priceBefore,
                'discountPercentage': discountPercentage,
                'dateCollected': date
            }

        #SCRAPY Pagination: increment the page number in the URL and yield a new request [11/1/24]
        next_page = response.xpath('//a[@data-ca-event="ce.ajax_pagination"]')
        href = next_page.get('href')
        current_page_number = response.url.split("page-")[-1].split("/")[0]

        if current_page_number.isdigit() and href:
            next_page_number = int(current_page_number) + 1
            next_page_url = re.sub(r"page-\d+", f"page-{next_page_number}", response.url)

            yield scrapy.Request(url=next_page_url, callback=self.parse)

        