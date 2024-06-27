# mywebcrawler/spiders/bestarfan_spider.py

## History
# 16/11: Created the base scraper
# 20/12: Modified for the new qoo10 DOM, unfinished
# 21/12: Finished rebuilding the scraper, needs debugging for output. Added a new output folder in this push
# 22/12: Debugged the overwriting of other json files and got output for qoo10 items for household appliances
# 28/12: Added somewhat dynamic way of updating the start_urls in order to scrape for more items, changed the yield to reflect the common data model. Added custom settings as well
# 05/02: Added the new categories for qoo10

## Last modified: Mon 05 Feb, Regine

import scrapy
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy import Selector
from selenium.webdriver.chrome.options import Options


class qoo10Spider(scrapy.Spider):
    name = 'qoo10'

    ## Update this list of items when attempting to scrape for items
    items_list = [
                    "refrigerator",
                    "top+load+washing+machine",
                    "front+load+washing+machine",
                    "standing+cooker",
                    "induction+cooker",
                    "tv",
                    "dryer",
                    "fan", 
                    "ovens", 
                    "water+purifier", 
                    "air+con",
                    "vacuum+cleaner",
                    "coffee+maker+machine",
                    "air+purifier",
                    "digital+door+lock",
                    "airfryer+deep+fryer"
                  ]
    
    start_urls = []
    base_url = 'https://www.qoo10.sg/s/'
    keywordUrl = ['?keyword=', '&keyword_auto_change=']

    # date = datetime.now().date()
    # addToURI = f"s3://raw-data-fyp/BestDenki/{date}_BestDenki.json"

    # creating the start urls for qoo10
    for item in items_list:
        frontMinus = item.replace('+', '-')
        frontCaps = frontMinus.upper()

        url = base_url + frontCaps + keywordUrl[0] + item + keywordUrl[1]
        start_urls.append(url)

    custom_settings = {
        # "FEED_URI": addToURI,
        # "FEED_FORMAT": "json",
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://www.qoo10.sg',
            'Referer': 'https://www.qoo10.sg',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        },
    }

    def parse(self, response):
        # Add your scraping logic here

        # Use Selenium to open a browser and interact with the page
        driver = webdriver.Chrome()
        driver.get(response.url)

        splitting_url = str(response.url).split("=")[2]
        category = splitting_url.split("&")[0]

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='list-moreview']//button[@id='btn_more_result']")))
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5) 
            try:
                element.click()
            except:
                break

        # reconfiguring the driver to get response from the new html url after expanding more results
        new_html = driver.page_source
        response = Selector(text=new_html)

        ### TO UPDATE WHENEVER QOO10 DOM CHANGES
        total_items = response.xpath("//div[@class='p-item']")
        

        for row in total_items:

            ## Getting main parent node for all the details
            main_information_parent_node = row.xpath('div[@class="p-item__info"]')
            div_list = main_information_parent_node.xpath("div")
            div_brand = div_list[0]
            brand = 'nothing is scraped'

            # getting item brand
            brand_intermediary = div_brand.xpath('div')
            brand = brand_intermediary.xpath('span[@class="label-brand"]').css('::text').extract()

            if brand == [] or brand == 'Daily Deal':
                brand = 'No-brand'

            else:
                brand = ", ".join(brand)

            # item name is under the same parent node as item brand
            item = div_brand.xpath("a").css('::text').extract()[0]

            ## Price
            div_price = div_list[1]

            # checking if there's a discounted price
            if div_price.xpath('div') != []:
                intermediary_div_price = div_price.xpath('div')
                actualprice_del = intermediary_div_price.xpath('del')

                intermediary_currentPrice = div_price.xpath('strong')
                intermediary_currentPrice = intermediary_currentPrice.css('::text').extract()[1]
                currentPrice = float(intermediary_currentPrice.strip('S$'))

                if actualprice_del != []:
                    intermediary_oldPrice = actualprice_del.css('::text').extract()[1]
                    oldPrice = float(intermediary_oldPrice.strip('S$'))

                else:
                    oldPrice = currentPrice

            else:
                intermediary_currentPrice = div_price.xpath('strong').css('::text').extract()[1]
                currentPrice = float(intermediary_currentPrice.strip('S$'))
                oldPrice = currentPrice

            # collecting the discount percentage
            discountPercentage = float((oldPrice - currentPrice) / oldPrice)
                    
            # to get ratings
            main_rating_parent_node = row.xpath('div[@class="p-item__head"]')
            intermediary_rating = main_rating_parent_node.css('span::attr(title)').extract()[0]
            ratings = float(intermediary_rating.strip('Rating:').lstrip('(').rstrip(')')[:-2])

            yield {
                'platform': 'Qoo10',
                'category': category,
                'brand':  brand,
                'model' : item,
                'discountedPrice': currentPrice,
                'listedPrice': oldPrice,
                'discountPercentage': discountPercentage,
                'rating': ratings,
                'dateCollected': datetime.now()
            }

            ####################################################################
            ####################################################################
                
                ### for future reference
            ## Shipment details
            # ship_parent_node = div_list[2].xpath("div[@class='item-delivery']")
            
            # # origin location of item
            # all_span = ship_parent_node.xpath('span')
        
            # itemLocation = 'Nil'
            # shipping_price = 0
            # conditional_shipping = 'Nil'
            # express_condition = 'Nil'
            # quick_delivery = False

            # for span in all_span:
            #     span_class = span.css('::attr(class)').extract_first()

            #     if span_class == 'shp_ntn':
            #         itemLocation = span.css('::text').extract()
            #         itemLocation = ''.join(itemLocation).replace(' /', ', ')

            #     elif span_class == 'ship os free':
            #         pass

            #     elif span_class == 'ship':
            #         intermediary_shippingPrice = span.css('::text').extract()[1]
            #         intermediary_shippingPrice = intermediary_shippingPrice.strip('"').strip('~').strip(' S$')
            #         shipping_price = float(intermediary_shippingPrice)

            #     elif span_class == 'ship qs qs':
            #         express_condition = span.xpath('i').css('::text').extract()[0]

            #     elif span_class == 'shp_qck':
            #         quick_delivery = True

            #     elif span_class == 'ship qp':
            #         intermediary_shippingPrice = span.css('::text').extract()[1]
            #         intermediary_shippingPrice = intermediary_shippingPrice.strip('Qprime S$')
            #         shipping_price = float(intermediary_shippingPrice)

            # shipping_div = ship_parent_node.xpath('div')

            # if shipping_div != []:
            #     intermediary_condition = shipping_div[0].css('::text').extract()[0]
            #     conditional_shipping = intermediary_condition
            
            ####################################################################
            ####################################################################