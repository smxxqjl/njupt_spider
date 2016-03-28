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
        title = response.xpath('//title/text()').extract()[0]
        status_list = list()
        status_list.append(title)
        callback = lambda response:self.secondparse(response, status_list)
        for url in depart_list:
            yield scrapy.Request(url, callback=callback)

    def secondparse(self, response, status_list):
        #Search for news block in html generally by guess
        title = response.xpath('//title/text()').extract()[0]
        if len(status_list) != 1:
            status_list.pop()
        status_list.append(title)
        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        print '-------------'
        for string in status_list:
            print string
        print '--------------'
        callback = lambda response:self.thirdparse(response, status_list)
        for url in more_list:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=callback)

    def thirdparse(self, response, status_list):

        title = response.xpath('//title/text()').extract()[0]
        callback = lambda response:self.thirdparse(response, status_list)
        for sel in response.xpath('//a'):
            if len(sel.xpath('@title').extract()) != 0 and "下一页".decode('utf8') in sel.xpath('@title').extract()[0]:
                nexturl = sel.xpath('@href').extract()[0]
                nexturl = response.urljoin(nexturl)
                yield scrapy.Request(nexturl, callback=callback)

        for news in response.xpath('//td[@class="postTime"]'):
            item = NjuptSpiderItem()
            item['date'] = news.xpath('text()').extract()[0]
            url = news.xpath('../td/a/@href').extract()[0]
            item['title'] = news.xpath('../td/a/font/text()').extract()[0]
            item['url'] = response.urljoin(url)
            print item['title'] + str(len(status_list))
            outputstring = item['date']+';'+item['title']+';'+item['url']+';'
            for string in status_list:
                outputstring = outputstring + string + ';'
            outputstring = outputstring + title
            outputstring = outputstring.encode('utf8')
            #delete all magic line break in string, the world comes in peace
            outputstring = ''.join(unicode(outputstring, 'utf-8').splitlines())
            self.fp.write(outputstring+'\n')
            yield item  
