import os

import scrapy

class SubdomainCrawler(scrapy.Spider):
    if not os.path.exists('data'):
        os.mkdir('data')

    name = 'subdomain_crawler'
    allowed_domain = ['www.google.com', 'njupt.edu.cn']
    start_urls = ['https://www.google.com/webhp?hl=en#hl=en&q=+site:njupt.edu.cn+njupt.edu.cn&start=0/']

    subdomain_set = set()

    def parse(self, response):
        url_list = response.xpath('//*[@id="rso"]').extract()
        print len(url_list)
        print response.body
        for url in url_list:
            print url
