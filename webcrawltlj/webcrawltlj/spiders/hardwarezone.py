# 14/03: Created base scraper for hardwarezone
# 15/03: Attempted to get base elem to scrape advertisement data
# 15/03: Modified scraper to find external ad links, using dunamic start_urls

## Last modified: Wednesday 15 Mar, Renee


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

class HardwarezoneSpider(scrapy.Spider):
    name = "hardwarezone"
    allowed_domains = ["www.hardwarezone.com.sg"]

    categories = ['washer', 'dryer', 'induction+hob', 'gas+hob', 'fridge', 'TV', 'oven', 'air+conditioner', 'hood', 'fan', 'vacuum+cleaner', 'smart+lock', 'airfryer', 'air+purifier', 'water+purifier', 'water+heater', 'coffee+machine']
    base_url = "https://www.hardwarezone.com.sg/search/products/"
    start_urls = []
    for category in categories:
        start_urls.append(base_url + category)

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'ROBOTSTXT_OBEY': False,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://www.hardwarezone.com.sg/',
            'Referer': 'https://www.hardwarezone.com.sg/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
    }

    def __init__(self):
        chrome_options = Options()
        # Uncomment the next two lines if you don't want a browser window to open
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito")
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def parse(self, response):
        print(self)
        print("=======================")
        try:
            # Open the website
            self.driver.get(response.url)
            time.sleep(5)

            ## To see the dom, uncomment this section
            # html_source = self.driver.page_source

            # # Print the HTML source code (you can also save it to a file if needed)
            # print(html_source)

            iframe_element = self.driver.find_element(By.XPATH, "//iframe[@id='master-1']")
            print(iframe_element)
            ad_ext_url = iframe_element.get_attribute('src')
            
            # Wait for the items to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="___gcse_0"]'))
            )
            
            # main_div = response.xpath("//div[@id='cse']")

            yield {
                'externalURL': ad_ext_url,
            }

        except Exception as e:
            logging.error(f"Error processing product: {e}")
            yield {
                'url': response.url,
                'error': str(e),
            }

    