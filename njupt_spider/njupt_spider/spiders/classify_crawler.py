# -*- coding: utf-8 -*-
import scrapy
from njupt_spider.items import NjuptSpiderItem
import re
import json
import os.path
import pickle

class classifyCrawler(scrapy.Spider):
    firstCrawl = True
    # This two dict stores the data about least reacent read news
    # Difference between the two are the variable 'most NewsDict is created when program is end
    # Another one is readed from last running crawler, which is to say when first crawls, 
    # The most NewsDictRead dict would be empty
    mostNewsDict = dict()
    mostNewsDictRead = dict()
    # You can not declear a constant value in python, just don't change it
    DictReadFileName = 'DictReadFileName'
    count = 0
    fp = file('text', 'wb')
    name = 'classify_crawler'
    allowed_domain = ['njupt.edu.cn']
    start_urls = [
            'http://www.njupt.edu.cn/'
            ]

    def parse(self, response):
        #Determine if previous least recent data is stored by check the file existence
        #if so read it
        if (os.path.isfile(self.DictReadFileName)):
            firstCrawl = False
            with open(self.DictReadFileName, 'rb') as fp:
                self.mostNewsDictRead = pickle.load(fp)

        with open('urlset') as fp:
            nexturls = fp.read().splitlines()
            for url in nexturls:
                yield scrapy.Request(url, callback=self.secondparse)

    def secondparse(self, response):
        #Search for news block in html generally by guess
        depart = response.xpath('//title/text()').extract()[0]
        self.count += 1
        depart = depart.strip()
        print self.count
        print depart
        # This remains doubt but still quiet accurate so far 
        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        for url in more_list:
            url = response.urljoin(url)
            #yield scrapy.Request(url, callback=self.thirdparse, meta={'depart': depart})

    #This fuction makes a duplicate request to get the depart name, we keep this duplicate to approach simplicty
    def thirdparse(self, response):
        print 'Third parse' + response.url
        depart = response.xpath('//title/text()').extract()[0]
        yield scrapy.Request(response.url, callback=self.fourthparse, dont_filter=True,meta={'depart': response.meta['depart'] + depart})

    def fourthparse(self, response):
        # Flag to show if this is the last page got unget news
        theLastPage = False

        if len(response.xpath('//td[@class="postTime"]')) >= 5:
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

        if theLastPage == False:
            for sel in response.xpath('//a'):
                if len(sel.xpath('@title').extract()) != 0 and "下一页".decode('utf8') in sel.xpath('@title').extract()[0]:
                    if len(sel.xpath('@href')) != 0:
                        nexturl = sel.xpath('@href').extract()[0]
                        nexturl = response.urljoin(nexturl)
                        yield scrapy.Request(nexturl, callback=self.fourthparse, meta={'depart': response.meta['depart']})

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
