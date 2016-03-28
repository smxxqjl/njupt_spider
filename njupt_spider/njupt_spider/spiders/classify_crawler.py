# -*- coding: utf-8 -*-
import scrapy
from njupt_spider.items import NjuptSpiderItem
import os
import json
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

class classifyCrawler(scrapy.Spider):
    fp = file('text', 'wb')
    name = 'classify_crawler'
    allowed_domain = ['njupt.edu.cn']
    start_urls = [
            'http://www.njupt.edu.cn/s/1/t/1/p/1/c/4/d/29/list.htm'
            ]

    def parse(self, response):
        # This is the indexpage parsing, to get the most subdomain of njupt
        depart_list = response.xpath('//*[@id="Map"]/area/@href').extract()
        for url in depart_list:
            yield scrapy.Request(url, callback=self.secondparse)

    def secondparse(self, response):
        #Search for news block in html generally by guess
        title = response.xpath('//title/text()').extract()[0]
        print title
        print response.url
        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        for url in more_list:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.thirdparse)

    def thirdparse(self, response):

        for news in response.xpath('//td[@class="postTime"]'):
            item = NjuptSpiderItem()
            item['date'] = news.xpath('text()').extract()[0]
            url = news.xpath('../td/a/@href').extract()[0]
            item['title'] = news.xpath('../td/a/font/text()').extract()[0]
            item['url'] = response.urljoin(url)
            print item['title']
            self.fp.write(item['date']+';'+item['title']+';'+item['url']+'\n')
            yield item

        for sel in response.xpath('//a'):
            if len(sel.xpath('@title').extract()) != 0 and "下一页".decode('utf8') in sel.xpath('@title').extract()[0]:
                nexturl = sel.xpath('@href').extract()[0]
                nexturl = response.urljoin(nexturl)
                yield scrapy.Request(nexturl, callback=self.thirdparse)
