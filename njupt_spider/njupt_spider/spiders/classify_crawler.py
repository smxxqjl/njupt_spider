# -*- coding: utf-8 -*-
import scrapy
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from njupt_spider.items import NjuptSpiderItem
from njupt_spider.MongoDB_Driver import MongoDB_Driver
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
    db = MongoDB_Driver('10.20.100.5', 27017, '南京邮电大学'.decode('utf8'))
    # You can not declear a constant value in python, just don't change it
    DictReadFileName = 'DictReadFileName'
    count = 0
    fp = file('text', 'wb')
    name = 'classify_crawler'
    allowed_domain = ['njupt.edu.cn']
    start_urls = [
            'http://www.njupt.edu.cn/'
            ]

    def __init__(self):
        dispatcher.connect(self.testInend, signals.spider_idle)
        with open(self.DictReadFileName, 'wb') as fp:
                self.mostNewsDictRead = pickle.dump(self.DictReadFileName, fp)

    def testInend(self):
        print "This is a message after all have been done"
        for key, item in self.mostNewsDict.iteritems():
            print type(item)
            print item['depart'] + ' ' + item['section'] + item['title'] + ' ' + str(item['timestamp'])
    def parse(self, response):
        #Determine if previous least recent data is stored by check the file existence
        #if so read it
        count = 3
        if (os.path.isfile(self.DictReadFileName)):
            print 'Yessss -------------'
            self.firstCrawl = False
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
        depart = depart.replace('南京邮电大学'.decode('utf8'), '')
        # This remains doubt but still quiet accurate so far 
        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        for url in more_list:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.thirdparse, meta={'depart': depart})

    #This fuction makes a duplicate request to get the depart name, we keep this duplicate to approach simplicty
    def thirdparse(self, response):
        print 'Third parse' + response.url
        section = response.xpath('//title/text()').extract()[0]
        section = section.strip()
        section = section.replace('南京邮电大学'.decode('utf8'), '')
        print 'section++++++++' + section
        depart = response.meta['depart'] + section
        depart = depart.strip()
        depart = ''.join(unicode(depart.encode('utf8'), 'utf-8').splitlines())
	'''
        if firstCrawl == True:
            yield scrapy.Request(response.url, callback=self.shadowFirstCrawlparse, 
                    dont_filter=True,meta={'depart': depart, 'baseurl', response.url}, 'itemnum': 0)
        else:
            yield scrapy.Request(response.url, callback=self.shadowCrawlparse, 
                    dont_filter=True,meta={'depart':depart,'baseurl':response.url,'itemnum': 0})
        '''
        if self.firstCrawl or depart.encode('utf8') not in self.mostNewsDictRead:
            print 'init'
            #Add new feature to make a dict of least recent news dictionary 
            #Following code get the least recent news it's simple copy of part of fourthparse code
            #-------------------------------------------------------------------------
            item = dict()
            if len(response.xpath('//td[@class="postTime"]')) >= 5:
                for news in response.xpath('//td[@class="postTime"]'):
                    item['date'] = news.xpath('text()').extract()[0]
                    url = news.xpath('../td/a/@href').extract()[0]
                    item['title'] = news.xpath('../td/a/font/text()').extract()[0]
                    item['url'] = response.urljoin(url)
                    outputstring = item['title']+response.meta['depart']+';'
                    outputstring = outputstring.encode('utf8')
                    #delete all magic line break in string, the world comes in peace
                    outputstring = ''.join(unicode(outputstring, 'utf-8').splitlines())
                    #self.fp.write(outputstring+'\n')
                    #yield item  
                    break
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
                                if len(news.xpath('.//a/font')) != 0:
                                    item['title'] = news.xpath('.//a/font/text()').extract()[0]
                                else:
                                    item['title'] = news.xpath('.//a/text()').extract()[0]
                                item['date'] = '2000-01-02'
                                item['url'] = response.urljoin(news.xpath('.//a/@href').extract()[0])
                                break
                            print 'This is url' + response.url
                            break
            item['timestamp'] = 2000
            item['depart'] =  response.meta['depart']
            item['section'] = section
            if 'title' in item:
                try:
                    self.mostNewsDict[depart] = item
                except:
                    print response.url + " no news is found"
                #---------------------------------------------------------------------------
                yield scrapy.Request(response.url, callback=self.fourthparse, 
                        dont_filter=True,meta={'depart': depart, 'timestamp': 2000, 'falsedepart': response.meta['depart'], 
                            'section': section})
        else:
            print response.meta['depart']
            print section
            print 'go on and on'
            yield scrapy.Request(response.url, callback=self.fourthAfterparse, 
                    dont_filter=True,meta={'depart': depart, 'falsedepart': response.meta['depart'], 
                        'section': section})

    def shadowCrawlparse(self, response):
        pass

    def shadowFirstCrawlparse(self, response):
        if len(response.xpath('//td[@class="postTime"]')) >= 5:
            pagenum = len(response.xpath('//td[@class="postTime"]'))
        else:
            gotNews = False
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

    def fourthAfterparse(self, response):
        depart = response.meta['depart']
        count = 0
        checkname = self.mostNewsDictRead[response.meta['depart'].encode('utf8')]['title']
        lasttimeStamp = self.mostNewsDictRead[response.meta['depart'].encode('utf8')]['timestamp']

        if len(response.xpath('//td[@class="postTime"]')) >= 5:
            for news in response.xpath('//td[@class="postTime"]'):
                if news.xpath('../td/a/font/text()').extract()[0].encode('utf8') == checkname:
                    break
                count = count + 1
            for news in response.xpath('//td[@class="postTime"]'):
                item = dict()
                print '-------------------------------------------------------------------'
                if count == 0:
                    break
                item['depart'] = response.meta['falsedepart']
                item['date'] = news.xpath('text()').extract()[0]
                url = news.xpath('../td/a/@href').extract()[0]
                item['title'] = news.xpath('../td/a/font/text()').extract()[0]
                item['url'] = response.urljoin(url)
                item['timestamp'] = lasttimeStamp + count
                item['section'] = response.meta['section']
                outputstring = item['title']+response.meta['depart'].strip()+';'
                if depart.encode('utf8') not in self.mostNewsDict:
                    print "---------------------------------------------------------------------"
                    self.mostNewsDict[depart.encode('utf8')] = item
                self.db.db_insert(item['depart'], item)
                outputstring = outputstring.encode('utf8')
                outputstring = ''.join(unicode(outputstring, 'utf-8').splitlines())
                count = count - 1
        else:
            gotNews = False
            for region in response.xpath('//*'):
                if len(region.xpath('li|tr')) >= 5:
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
                            if len(news.xpath('.//a/font')) != 0:
                                title = news.xpath('.//a/font/text()').extract()[0]
                            elif len(news.xpath('.//a/text()').extract()) != 0:
                                title = news.xpath('.//a/text()').extract()[0]
                            else:
                                continue
                            if title.encode('utf8') == checkname:
                                break
                            count += 1
                        for news in newslist:
                            item = dict()
                            if count == 0:
                                break
                            if len(news.xpath('.//a/font')) != 0:
                                item['title'] = news.xpath('.//a/font/text()').extract()[0]
                            elif len(news.xpath('.//a/text()').extract()) != 0:
                                item['title'] = news.xpath('.//a/text()').extract()[0]
                            else:
                                continue
                            item['date'] = '2000-01-02'
                            item['url'] = response.urljoin(news.xpath('.//a/@href').extract()[0])
                            item['depart'] = response.meta['falsedepart']
                            item['section'] = response.meta['section']
                            item['timestamp'] = count + self.mostNewsDictRead[depart.encode('utf8')]['timestamp']
                            count -= 1
                            if depart.encode('utf8') not in self.mostNewsDict:
                                self.mostNewsDict[depart.encode('utf8')]= item
                            yield scrapy.Request(item['url'], callback=self.timeparse, meta={'item': item})
                        print 'This is url' + response.url
                        break;
            if gotNews == False:
                print 'No news is found on' + response.url

    def fourthparse(self, response):
        # Flag to show if this is the last page got unget news
        count = 0
        if len(response.xpath('//td[@class="postTime"]')) >= 5:
            for news in response.xpath('//td[@class="postTime"]'):
                item = dict()
                item['depart'] = response.meta['falsedepart']
                item['date'] = news.xpath('text()').extract()[0]
                url = news.xpath('../td/a/@href').extract()[0]
                item['title'] = news.xpath('../td/a/font/text()').extract()[0]
                item['url'] = response.urljoin(url)
                item['timestamp'] = response.meta['timestamp'] - count
                item['section'] = response.meta['section']
                outputstring = item['title']+response.meta['depart']+ str(item['timestamp']) +';'
                self.db.db_insert(item['depart'], item)
                outputstring = outputstring.encode('utf8')
                #delete all magic line break in string, the world comes in peace
                outputstring = ''.join(unicode(outputstring, 'utf-8').splitlines())
                #self.fp.write(outputstring+'\n')
                #yield item  
                count += 1
        else:
            gotNews = False
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
                            item = dict()
                            if len(news.xpath('.//a/font')) != 0:
                                item['title'] = news.xpath('.//a/font/text()').extract()[0]
                            elif len(news.xpath('.//a/text()').extract()) != 0:
                                item['title'] = news.xpath('.//a/text()').extract()[0]
                            else:
                                continue
                            item['date'] = '2000-01-02'
                            item['url'] = response.urljoin(news.xpath('.//a/@href').extract()[0])
                            item['depart'] = response.meta['falsedepart']
                            item['timestamp'] = response.meta['timestamp'] - count
                            item['section'] = response.meta['section']
                            yield scrapy.Request(item['url'], callback=self.timeparse, meta={'item': item})
                            count += 1
                            #yield item
                        break;
            if gotNews == False:
                print 'No news is found on' + response.url

        for sel in response.xpath('//a'):
            if len(sel.xpath('@title').extract()) != 0 and "下一页".decode('utf8') in sel.xpath('@title').extract()[0]:
                if len(sel.xpath('@href')) != 0:
                    nexturl = sel.xpath('@href').extract()[0]
                    nexturl = response.urljoin(nexturl)
                    yield scrapy.Request(nexturl, callback=self.fourthparse
                            , meta={'depart': response.meta['depart'], 'timestamp': response.meta['timestamp'] - count,
                                'falsedepart': response.meta['falsedepart'], 'section': response.meta['section']})

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
        self.db.db_insert(item['depart'], item)
