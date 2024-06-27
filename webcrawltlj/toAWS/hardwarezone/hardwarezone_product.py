# 15/03: Created hardwarezone_product_spider to scrape from external ad link

## Last modified: Wednesday 15 Mar, Renee


import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
import logging
import re


class HardwarezoneProductSpider(scrapy.Spider):
    json_file_path = "output/hardwarezone/external_ad_links.json"
    ext_ad_links = []

    with open(json_file_path, 'r') as file:
        data = json.load(file)

        for row in data:
            if 'externalURL' in row:
                ext_ad_links.append(row['externalURL'])

    name = "hardwarezone_product"
    allowed_domains = ["www.adsensecustomsearchads.com"]
    start_urls = ext_ad_links
    # start_urls = ["https://www.adsensecustomsearchads.com/cse_v2/ads?adsafe=low&cx=011134908705750190689%3Adaz50x-t54k&fexp=72519171%2C72519168%2C20606%2C17301383%2C17301421%2C17301422%2C17301437%2C17301440%2C17301441%2C71847096&client=google-coop&q=site%3Acom.sg%2Fproduct-%20-site%3Acom.sg%2Fproduct-guide%20-site%3Acom.sg%2Fproduct-feature%20-site%3Acom.sg%2Fproduct-news%20hood&r=m&sct=ID%3D8c298d3bf24359bf%3AT%3D1710484935%3ART%3D1710484935%3AS%3DALNI_MYZ6gSHYZQufm0QSQnma-djtq9MSg&sc_status=6&hl=en&ivt=0&type=0&oe=UTF-8&ie=UTF-8&client_gdprApplies=0&format=p4&ad=p4&nocache=9711710484983069&num=0&output=uds_ads_only&source=gcsc&v=3&bsl=10&pac=0&u_his=10&u_tz=480&dt=1710484983069&u_w=1440&u_h=900&biw=1200&bih=642&psw=1200&psh=796&frm=0&uio=-&drt=0&jsid=csa&jsv=614655379&rurl=https%3A%2F%2Fwww.hardwarezone.com.sg%2Fsearch%2Fproducts%2Fhood"]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'ROBOTSTXT_OBEY': False,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://www.adsensecustomsearchads.com/',
            'Referer': 'https://www.adsensecustomsearchads.com/',
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
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito") 
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        try:
            # Open the website
            self.driver.get(response.url)
            time.sleep(5)

            #Open the website
            self.driver.get(response.url)

            # Wait for the items to load
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@data-ad-container="1"]'))
            )

            #Give the page time to load
            time.sleep(5)

            ad_listings_container = self.driver.find_element(By.XPATH, '//div[@data-ad-container="1"]')

            # find all individual ad listings within the container
            ad_listings = ad_listings_container.find_elements(By.XPATH, '//div[contains(@class, "clicktrackedAd")]')
            print(ad_listings)

            #find index of "products" in URL
            url = response.url
            #find the index of "products" in the URL
            index = url.find("products")
            category = url[index + 11:].strip().replace("%2B", " ").upper()


            for ad in ad_listings:
                sel = Selector(text=ad.get_attribute('outerHTML'))
                ad_title = sel.xpath('.//div[1]/a/text()').extract_first()
                ad_url = sel.xpath('.//div[1]/a/@href').extract_first()
                ad_description = sel.xpath('.//span[contains(@class, "styleable-description")]/text()').extract_first()
                yield {
                    'title': ad_title,
                    'description': ad_description,
                    'url': ad_url,
                    'category': category
                }

        except Exception as e:
            logging.error(f"Error processing product: {e}")
            yield {
                'url': response.url,
                'error': str(e),
            }
