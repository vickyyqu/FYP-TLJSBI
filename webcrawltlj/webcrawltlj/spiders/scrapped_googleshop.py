## History
# 26/02: Created the base scraper

## Last modified: Tuesday 26 Feb, Regine

import scrapy


class GoogleshopSpider(scrapy.Spider):
    name = "googleshop"
    allowed_domains = ["shopping.google.com"]
    start_urls = ["https://www.google.com/search?tbm=shop&hl=en-GB&psb=1&ved=2ahUKEwj1vd33gc6EAxUTxzwCHZIzBnYQu-kFegQIABAJ&q=ceiling+fan&oq=cei&gs_lp=Egtwcm9kdWN0cy1jYyIDY2VpKgIIADIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgARIzzpQuAVYiS9wA3gAkAEAmAGeAaABgwSqAQMyLjO4AQPIAQD4AQGoAgA&sclient=products-cc"]

    custom_settings = {
        
        'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': '*/*',
            'ROBOTSTXT_OBEY': True,
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Origin': 'http://shopping.google.com/',
            'Referer': 'http://shopping.google.com/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        }
    }

    def parse(self, response):
        base_url = "https://www.google.com/search?tbm=shop&hl=en-GB&psb=1&ved=2ahUKEwj1vd33gc6EAxUTxzwCHZIzBnYQu-kFegQIABAJ&q="
        closing_url = "&oq=cei&gs_lp=Egtwcm9kdWN0cy1jYyIDY2VpKgIIADIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgARIzzpQuAVYiS9wA3gAkAEAmAGeAaABgwSqAQMyLjO4AQPIAQD4AQGoAgA&sclient=products-cc"
        print(f'ARE WE GETTING ANYTHING')
        print(response)
        print(response.text)


        url_string = str(response.url)
        
        category = url_string.split('=')[5].split("&")[0].replace("+"," ")
        main_div = response.xpath("//div[@class='EDblX GpHuwc']")
        # main_div = response.xpath("//div[@class='ljqwrc']")
        print(main_div)

        for segment in main_div:
            item_name =  segment.xpath("h3").css("::text").extract()
            price_str = segment.xpath("div[@class='hn9kf']").xpath("span").css('b::text').extract()
            platform_advertising = segment.xpath("div[@class='sh-np__seller-container']").css("::aria-label").extract()
            price = float(price_str)

        yield {
            'advertising_platform': platform_advertising,
            'item': item_name,
            'category': category,
            'price': price
        }

        # items_list = [
        #             'washing+machine',
        #             # "refrigerator",
        #             # "top+load+washing+machine",
        #             # "front+load+washing+machine",
        #             # "standing+cooker",
        #             # "induction+cooker",
        #             # "tv",
        #             # "dryer",
        #             # "fan", 
        #             # "ovens", 
        #             # "water+purifier", 
        #             # "air+con",
        #             # "vacuum+cleaner",
        #             # "coffee+maker+machine",
        #             # "air+purifier",
        #             # "digital+door+lock",
        #             # "airfryer+deep+fryer"
        #           ]
        
        # for item in items_list:
        #     complete_url = base_url + item + closing_url
        #     print(complete_url)
        #     yield scrapy.Request(complete_url, callback=self.main_parse)

    # def main_parse(self, response):
    #     url_string = str(response.url)
        
    #     category = url_string.split('=')[5].split("&").replace("+"," ")
    #     main_div = response.xpath("//div[@class='EDblX GpHuwc']")
    #     # main_div = response.xpath("//div[@class='ljqwrc']")
    #     print(main_div)

    #     for segment in main_div:
    #         item_name =  segment.xpath("h3").css("::text").extract()
    #         price_str = segment.xpath("div[@class='hn9kf']").xpath("span").css('b::text').extract()
    #         platform_advertising = segment.xpath("div[@class='sh-np__seller-container']").css("::aria-label").extract()
    #         price = float(price_str)

    #     yield {
    #         'advertising_platform': platform_advertising,
    #         'item': item_name,
    #         'category': category,
    #         'price': price
    #     }
        
        
