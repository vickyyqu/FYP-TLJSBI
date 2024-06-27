# mywebcrawler/spiders/bestarfan_spider.py

import scrapy

class BestarFanSpider(scrapy.Spider):
    name = 'bestarfan'
    start_urls = ['https://www.tlj-home.com/collections/bestarfan']

    def parse(self, response):
        # Add your scraping logic here
        total_items = response.xpath("//li[@class='grid__item']")
        count = 0

        for itemInfo in total_items:
            title_list = itemInfo.xpath("//h3[@class='card__heading h5']")
            title = title_list[count].xpath("a").xpath("text()").get().strip()

            price_list = itemInfo.xpath("//div[@class='price__regular']")
            price = price_list[count].xpath("span[@class='price-item price-item--regular']").xpath("text()").get().strip()
            count += 1
            
            atomePrice_list = itemInfo.xpath("//div[@class='CGduNjlE atome-price-divider atome-widget']")
            atomePrice = atomePrice_list[count].xpath("span[@class='xxSenlkE atome-price']").xpath("text()")

            yield {
                'Product_Name': title,
                'Price': price,
                # 'Atome_Num_Payments': num_payments,
                'Atome_Price': atomePrice
            }
        


        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)
