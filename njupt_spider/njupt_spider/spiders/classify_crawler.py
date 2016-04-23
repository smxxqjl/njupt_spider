# -*- coding: utf-8 -*-
import scrapy
from njupt_spider.items import NjuptSpiderItem
import re
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

    # This function is abolished we get subdomain from search engine as showed in another parse function
    '''
    def parse(self, response):
        # This is the indexpage parsing, to get the most subdomain of njupt
        depart_list = response.xpath('//*[@id="Map"]/area/@href').extract()
        title = response.xpath('//title/text()').extract()[0]
        status_list = list()
        status_list.append(title)
        callback = lambda response:self.secondparse(response, status_list)
        for url in depart_list:
            yield scrapy.Request(url, callback=callback)
    '''
    def parse(self, response):
        #yield scrapy.Request('http://gdgc.njupt.edu.cn/', callback=self.secondparse)
        with open('urlset') as fp:
            nexturls = fp.read().splitlines()
            for url in nexturls:
                yield scrapy.Request(url, callback=self.secondparse)

    def secondparse(self, response):
        #Search for news block in html generally by guess
        depart = response.xpath('//title/text()').extract()[0]
        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        for url in more_list:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.thirdparse, meta={'depart': depart})

    def thirdparse(self, response):
        print 'Third parse' + response.url
        depart = response.xpath('//title/text()').extract()[0]
        yield scrapy.Request(response.url, callback=self.fourthparse, dont_filter=True,meta={'depart': response.meta['depart'] + depart})

    def fourthparse(self, response):
        for sel in response.xpath('//a'):
            if len(sel.xpath('@title').extract()) != 0 and "下一页".decode('utf8') in sel.xpath('@title').extract()[0]:
                if len(sel.xpath('@href')) != 0:
                    nexturl = sel.xpath('@href').extract()[0]
                    nexturl = response.urljoin(nexturl)
                    yield scrapy.Request(nexturl, callback=self.fourthparse, meta={'depart': response.meta['depart']})

        if len(response.xpath('//td[@class="postTime"]')) >= 3:
            for news in response.xpath('//td[@class="postTime"]'):
                item = NjuptSpiderItem()
                item['date'] = news.xpath('text()').extract()[0]
                url = news.xpath('../td/a/@href').extract()[0]
                item['title'] = news.xpath('../td/a/font/text()').extract()[0]
                item['url'] = response.urljoin(url)
                outputstring = item['title']+response.meta['depart']+';'
                print outputstring
                outputstring = outputstring.encode('utf8')
                #delete all magic line break in string, the world comes in peace
                outputstring = ''.join(unicode(outputstring, 'utf-8').splitlines())
                #self.fp.write(outputstring+'\n')
                #yield item  
        else:
            gotNews = False
            count = 0
            for region in response.xpath('//*'):
                if len(region.xpath('li|tr')) >= 5:
                    # Get the region has a lot info repetitive
                    newslist = region.xpath('li|tr')
                    for news in newslist:
                        if len(news.xpath('.//a/@href').extract()) == 0:
                            continue
                        newurl = news.xpath('.//a/@href').extract()[0]
                        if 'info' in news.xpath('.//a/@href').extract()[0]:
                            gotNews = True
                            break
                    newslist = region.xpath('li|tr')
                    if gotNews:
                        for news in newslist:
                            item = NjuptSpiderItem()
                            if len(news.xpath('.//a/font')) != 0:
                                item['title'] = news.xpath('.//a/font/text()').extract()[0]
                            else:
                                item['title'] = news.xpath('.//a/text()').extract()[0]
                            item['date'] = '2000-01-02'
                            item['url'] = response.urljoin(news.xpath('.//a/@href').extract()[0])
                            item['depart'] = response.meta['depart']
                            yield scrapy.Request(item['url'], callback=self.timeparse, meta={'item': item})
                            #yield item
                        print 'This is url' + response.url
                        break;
            if gotNews == False:
                print 'No news is found on' + response.url

        #This is a parser for the news has no time in the newslist after this operation, the news will be written out
    def timeparse(self, response):
        item = response.meta['item']
        datelist = re.findall('\d{4}[-/]\d{2}[-/]\d{2}', response.body)
        if len(datelist) == 0:
            print 'No date info is found'
            return
        elif len(datelist) > 1:
            print 'Multiple date info is found extract the first one, warning!'
        item['date'] = datelist[0]
        print item['depart'] + item['title']
