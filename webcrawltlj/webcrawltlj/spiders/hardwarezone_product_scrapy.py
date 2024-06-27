# 15/03: Created hardwarezone_product to scrape from external ad link

## Last modified: Wednesday 15 Mar, Renee

import scrapy
import json
import logging


class HardwarezoneProductSpider(scrapy.Spider):
    # json_file_path = "output/hardwarezone/external_ad_links.json"
    # ext_ad_links = []

    # with open(json_file_path, 'r') as file:
    #     data = json.load(file)

    #     for row in data:
    #         if 'externalURL' in row:
    #             ext_ad_links.append(row['externalURL'])

    name = "hardwarezone_product_scrapy"
    allowed_domains = ["www.adsensecustomsearchads.com"]
    # start_urls = ext_ad_links
    start_urls = ["https://www.adsensecustomsearchads.com/cse_v2/ads?adsafe=low&cx=011134908705750190689%3Adaz50x-t54k&fexp=72519171%2C72519168%2C20606%2C17301383%2C17301421%2C17301422%2C17301431%2C17301434%2C17301435%2C71847096&client=google-coop&q=site%3Acom.sg%2Ftech-news-%20gas%20hob&r=m&sct=ID%3Df19be26c8b1c758c%3AT%3D1710470188%3ART%3D1710470188%3AS%3DALNI_MaFZdO7cinul_wF13o5RS_ZXIE8ng&sc_status=6&hl=en&ivt=0&type=0&oe=UTF-8&ie=UTF-8&client_gdprApplies=0&format=p4&ad=p4&nocache=7811710470218001&num=0&output=uds_ads_only&source=gcsc&v=3&bsl=10&pac=0&u_his=7&u_tz=480&dt=1710470218002&u_w=1440&u_h=900&biw=1333&bih=713&psw=1333&psh=794&frm=0&uio=-&drt=0&jsid=csa&jsv=614655379&rurl=https%3A%2F%2Fwww.hardwarezone.com.sg%2Fsearch%2Fnews%2Fgas%2Bhob"]

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

    def parse(self, response):
        try:
            # Print the response body to inspect the HTML content
            print(response.body)

            # Find all ad listings
            ad_listing_elements = response.xpath('//div[contains(@class, "clicktrackedAd_js")]')

            # Print out the ad_listing_elements to see if any elements are found
            print(ad_listing_elements.getall())

            for element in ad_listing_elements:
                ad_title = element.xpath('.//div[1]/a/text()').get()  # Extract text from the element
                ad_url = element.xpath('.//div[1]/a/@href').get()    # Extract the value of the href attribute

                yield {
                    'ad_title': ad_title,
                    'ad_url': ad_url
                }

        except Exception as e:
            # Log the error along with the URL that caused it
            logging.error("Error retrieving product details")
            logging.error(f"Error processing URL: {response.url}")
            logging.error(f"Error details: {e}")