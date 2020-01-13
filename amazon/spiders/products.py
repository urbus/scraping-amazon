# -*- coding: utf-8 -*-
from scrapy import Spider, Request


class ProductsSpider(Spider):
    name = 'products'
    allowed_domains = ['amazon.com']
    start_urls = ['https://www.amazon.com']

    def __init__(self, sponsored=None, *args, **kwargs):
        super(ProductsSpider, self).__init__(*args, **kwargs)
        # Get sponsored products?
        if sponsored:
            self.asin_selector = '//*[starts-with(@id,"result_")]/@data-asin'
        else:
            self.asin_selector = '//*[starts-with(@id,"result_") and not(contains(@class, "AdHolder"))]/@data-asin'

    def parse(self, response):
        action = response.xpath('//*[@class="nav-searchbar"]/@action').extract_first()
        category = response.xpath('//select/option/@value').extract()[0]
        url_search = '{}?url={}&field-keywords={}'.format(action,
                                                          category,
                                                          '+'.join(self.keyword.split(' ')))
        absolute_url = response.urljoin(url_search)
        yield Request(absolute_url, callback=self.parse_list)

    def parse_list(self, response):
        results = response.css('.s-result-item')
        for asin in results:
            asi = asin.css("::attr(data-asin)").extract_first()
            absolute_url = '{}/dp/{}'.format(self.start_urls[0], asi)
            yield Request(absolute_url, callback=self.parse_product)

        next_page = response.css('.a-last > a ::attr(href)').extract_first()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield Request(next_page_url, callback=self.parse_list)

    def parse_product(self, response):
        title = response.xpath('//*[@id="productTitle"]/text()').extract_first().strip()
        vendor = response.xpath('//*[@id="bylineInfo"]/text()').extract_first().strip()
        stars = response.xpath('//a/i[contains(@class, "a-icon-star")]/span/text()').extract_first()
        customer_reviews = response.xpath('//a[@id="acrCustomerReviewLink"]/span/text()').extract_first().split(' ')[0]
        price = response.xpath('//*[@id="priceblock_ourprice"]/text()').extract_first()
        yield {'Product': title,
               'Vendor': vendor,
               'Stars': stars,
               'Customer Reviews': customer_reviews,
               'Price': price}

               #"/gp/offer-listing/B00NQGP3SO"
