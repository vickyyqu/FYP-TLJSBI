# mywebcrawler/spiders/bestarfan_spider.py

## History
# 29/01: Created the base scraper
# 02/02: Finished the scraper, have yet to test it
# 08/02: Polished scraper

## Last modified: Thu 08 Feb, Regine

import scrapy
from datetime import datetime
from scrapy import Selector
import time

class ParisilkSpider(scrapy.Spider):
    name = "parisilk"
    allowed_domains = ["www.parisilk.com"]
    start_urls = [
        "https://www.parisilk.com/index.php?route=product/search&search=washing%20machine"
    ]
    date = datetime.now().date()
    custom_settings = {
        "FEED_URI": f"s3://raw-data-fyp/Parisilk/{date}_parisilk.json",
        "FEED_FORMAT": "json",
        'ROBOTSTXT_OBEY': False,
        # 'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'https://www.parisilk.com',
            'Referer': 'https://www.parisilk.com',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
    }
    def returningOneItem(self, item_intermediary):
        itemStarts = 2
        brand_intermediary = item_intermediary[0]
        isBrand = self.checkBrand(brand_intermediary)
        
        if isBrand:
            isProblematic = self.problematicBrands(brand_intermediary)

            if isProblematic:
                brand = " ".join(item_intermediary[:2]) # 0 1
                model_num = item_intermediary[2]
                
                modelProblemNum = self.problematicModelNums(model_num)
                if modelProblemNum == 1:
                    model_num = item_intermediary[3]

                elif modelProblemNum == 2:
                    model_num = " ".join(item_intermediary[2:4])
                
                itemStarts = 4

            else:
                brand = brand_intermediary
                model_num = item_intermediary[1]

                modelProblemNum = self.problematicModelNums(model_num)
                if modelProblemNum == 1:
                    model_num = item_intermediary[2]
                    

                elif modelProblemNum == 2:
                    model_num = " ".join(item_intermediary[1:3])

                itemStarts = 3

        else:
            brand = ""
            model_num =  brand_intermediary
            
            modelProblemNum = self.problematicModelNums(model_num)
            if modelProblemNum == 1:
                model_num = item_intermediary[1]

            elif modelProblemNum == 2:
                model_num = " ".join(item_intermediary[:2])


        item = " ".join(item_intermediary[itemStarts:])

        return brand, model_num, item

    def problematicModelNums(self, modelNum):
        if modelNum == "":
            return 1
            model_num = second_item_intermediary[2]
            itemStarts = 3

        elif len(modelNum) < 5 or ((modelNum[:2] == "FV") and (len(modelNum) < 6)):
            return 2
            model_num = " ".join(second_item_intermediary[2:4])
            itemStarts = 4

        return 0

    def problematicBrands(self, brand):
        problematic = ["Rommelsbacher", "EF", "Candy", "Delonghi"]

        if brand in problematic:
            return True

        return False

    def checkBrand(self, brand):
        if brand == "1550":
            pass
        
        else:
            for chr in brand:
                if chr.isnumeric():
                    return False
        return True

    def parse(self, response):

        base_url = "https://www.parisilk.com/index.php?route=product/search&search="
        items_list = [
                    'washing%20machine',
                    "refrigerator",
                    "top%20load%20washing%20machine",
                    "front%20load%20washing%20machine",
                    "standing%20cooker",
                    "induction%20cooker",
                    "tv",
                    "dryer",
                    "fan", 
                    "ovens", 
                    "water%20purifier", 
                    "air%20con",
                    "vacuum%20cleaner",
                    "coffee%20maker%20machine",
                    "air%20purifier",
                    "digital%20door%20lock",
                    "airfryer%20deep%20fryer"
                  ]
        
        maxPageNum = 1  
        pagination_num = response.xpath("//div[@class='pagination']").css("a::text").extract()
        
        for page in pagination_num:
            if page.isdigit() and int(page) > maxPageNum:
                maxPageNum = int(page)
                print(maxPageNum)

        for item in items_list:
            base_item_url = base_url + str(item) + "&page="

            for page_num in range(1, maxPageNum + 1):
                url = base_item_url + str(page_num)
                print(url)
                yield scrapy.Request(url, callback=self.parse_page)


    def parse_page(self, response):
        # for ref https://www.parisilk.com/index.php?route=product/search&search=washing+machine&page=5
        url_string = str(response.url)
        category = url_string.split("=")[-2].split("&")[0].replace("%20"," ")
        
        # the website shows product-grid, but while scraping, it is actually product-list
        # because i didn't really figure out how to just go one level lower,
        # i scraped all the div elements and retrieved a list of all the name and price classes

        main_div = response.xpath("//div[@class='product-list']")
        child_nodes = main_div.xpath("./div")
        
        # asking if the div elemenet has class either name or price
        all_nameNodes = child_nodes.xpath("./div[@class='name']")
        all_priceNodes = child_nodes.xpath("./div[@class='price']")
        
        # checking for how many items are being shown on screen
        numItems = len(all_nameNodes)

        # allowing the num to be the index for both name div and price div lists
        for num in range(numItems):
            currName = all_nameNodes[num]
            currPrice = all_priceNodes[num]

            ## Getting the product names
            currName = currName.xpath("a").css("::text").extract()[0]

            # if bundle, then there is a need to split and get the extra item's details
            # bundles are usually indicated right in front, so declaring a separate variable is fine
            
            bundle_checker = currName.split(" ")[0]
            if bundle_checker == "(Bundle)":
                item_set = " ".join(currName.split(" ")[1:]).split(" + ")
                main_item = item_set[0]
                add_on_item = item_set[1]
                

                # Main item breakdown
                main_item_intermediary = main_item.split(" ")
                
                brand, model_num, item = self.returningOneItem(main_item_intermediary)
                # sometimes the first string is not a brand, but instead a model number
                # helper function defined above checks if the string is a brand

                ###################################
                # Second item breakdown
                second_item_intermediary = add_on_item.split(" ")

                bundleBrand, bundleModel, bundleItem = self.returningOneItem(second_item_intermediary)
                hasBundle = True

            # if it is not a bundle, hasBundle = False
            else:
                main_item_intermediary = currName.split(" ")
                
                brand, model_num, item = self.returningOneItem(main_item_intermediary)

                hasBundle = False
                bundleBrand = ""
                bundleModel = ""
                bundleItem = ""

            ## Getting the product prices
            
            div_price_text = currPrice.css("::text").extract()[2]
            oldPrice = float(div_price_text.strip("\n").strip(" ").lstrip("SGD ").replace(',',""))


             
# (Bundle) Electrolux EWF9024P5WB UltimateCare 500 Front Load Washing Machine (9kg) + Electrolux EDH804H5WB UltimateCare 500 Heat Pump Dryer (8kg)
# (Bundle) Electrolux EWF9024P5WB UltimateCare 500 Front Load Washing Machine (9kg) + Electrolux EDH804H5WB UltimateCare 500 Heat Pump Dryer (8kg)
# SGD 2,798.00            

            yield {
                'platform': 'Parisilk',
                'category' : category,
                'brand':  brand,
                'model' : model_num,
                'item' : item,
                'hasBundle?' : hasBundle,
                'bundleBrand': bundleBrand,
                'bundleModel': bundleModel,
                'bundleItem': bundleItem,
                'listedPrice': oldPrice,
                'dateCollected': datetime.now()
            }