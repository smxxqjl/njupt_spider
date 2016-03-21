import scrapy

import os

class classifyCrawler(scrapy.Spider):
    if not os.path.exists('data'):
        os.mkdir('data')
    name = 'classify_crawler'
    allowed_domain = ['njupt.edu.cn']
    start_urls = [
            'http://www.njupt.edu.cn/s/1/t/1/p/1/c/4/d/29/list.htm'
            ]

    def parse(self, response):
        depart_list = response.xpath('//*[@id="Map"]/area/@href').extract()
        for url in depart_list:
            yield scrapy.Request(url, callback=self.secondparse)

    def secondparse(self, response):
        title = response.xpath('//title/text()').extract()[0]
        print title
        if not os.path.exists('title'):
            os.mkdir(title)
        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        for url in more_list:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.thirdparse)

    def thirdparse(self, response):
        for news in response.xpath('//td[@class="postTime"]'):
            date = news.xpath('/td/text()').extract()[0]
            news = news.xpath('..')
            url = news.xpath('//a/@href').extract()[0]
