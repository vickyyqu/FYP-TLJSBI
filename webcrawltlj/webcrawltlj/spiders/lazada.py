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
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException


class LazadaSpider(scrapy.Spider):
    name = "lazada"
    allowed_domains = ["lazada.sg"]
    start_urls = ["https://www.lazada.sg/tag/fridge/?_keyori=ss&catalog_redirect_tag=true&from=input&page=1&q=fridge&spm=a2o42.home-sg.search.go.654346b5IODXkj"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://lazada.sg/',
            'Referer': 'https://lazada.sg/',
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

       # Open the website
        self.driver.get(response.url)

        # Wait for the items to load
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@data-qa-locator="product-item"]'))
        )

        # Identify product items list
        products = self.driver.find_elements(By.XPATH, '//div[@data-qa-locator="product-item"]')
        try: 
            for i, item in enumerate(products):
                sel = Selector(text=item.get_attribute('outerHTML'))

                try: 
                    prod_link = sel.xpath('.//a/@href').get()

                    if prod_link.startswith('//'):
                        prod_link = 'https:' + prod_link
                    
                    yield response.follow(
                        prod_link,
                        callback=self.parse_product_page,
                    )                
                
                except Exception as e:
                    logging.error("Error retrieving product URL")
                    logging.error(f"Error processing URL: {response.url}")
                    logging.error(f"Error details: {e}")

                    yield {
                        'msg': "Error retrieving product URL",
                        'selector': sel.extract(),
                        'url': response.url,
                        'error': str(e),
                    }
        
        except TimeoutException:
            logging.error("Timed out waiting for page to load")
        except NoSuchElementException:
            logging.error("No element found")

        
        try:
            next_page_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, './/button[contains(@class, "ant-pagination-item-link"])'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
            time.sleep(1)
            next_page_button.click()
            
            # Wait for the next page to load and repeat the process
            WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@data-qa-locator="product-item"]'))
            )

        except (NoSuchElementException, TimeoutException):
            print("No more pages to load or timeout reached.")
            self.driver.quit()  
        
        

    def parse_product_page(self, response):
        try: 
            # Open the website
            self.driver.get(response.url)

            # Wait for the items to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "product-detail")]'))
            )
            
            new_html = self.driver.page_source
            sel = Selector(text=new_html)
                    
            # Extract attributes
            brand = sel.xpath('//a[contains(@class, "brand-link")]/text()').extract_first()
            model = sel.xpath('//h1[contains(@class, "product-badge-title")]/text()').extract_first()

            # Convert discounted price to a float
            discountedPriceText = sel.xpath('//span[contains(@class, "pdp-price_type_normal")]/text()').extract_first()
            if discountedPriceText:
                discountedPrice = float(re.sub(r'[^\d.]', '', discountedPriceText))
                discountedPrice = round(discountedPrice, 2)
            else: 
                discountedPrice = None
            
            # Listed price
            listedPriceText = sel.xpath('//span[contains(@class, "pdp-price_type_deleted")]/text()').extract_first()
            if listedPriceText:
                listedPrice = float(re.sub(r'[^\d.]', '', listedPriceText))
                listedPrice = round(listedPrice, 2)
            else: 
                listedPrice = None
            
            dateCollected = date.today()


            yield {
                'platform': 'Lazada',
                'brand': brand,
                'model': model,
                'discounted price': discountedPrice,
                'listed price': listedPrice,
                'date collected': dateCollected
            }

        except StaleElementReferenceException:
            # Handle the case where the element reference is no longer valid
            self.driver.refresh()

            # print("Encountered a stale element, re-acquiring the list of products")

        except Exception as e:
            # Log the error along with the URL that caused it
            logging.error(f"Error processing URL: {response.url}")
            logging.error(f"Error details: {e}")
            yield {
                'url': response.url,
                'error': str(e),
            }


## LATEST ERROR
    # net::ERR_NAME_NOT_RESOLVED 
    # scraped ~5 items before error
    # latest output in 3jan_lazada