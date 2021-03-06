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
    # Two dict are used for news diff control
    # One for storing the last readed latest news(mostnewsDictRead from the file)
    # One for storing latest news readed this time(mostNewsDict)
    mostNewsDict = dict()
    mostNewsDictRead = dict()
    unhandlefp = file('unhandleurl', 'w')

    # Connect to Mongo Database
    db = MongoDB_Driver('180.209.64.38', 40020, '南京邮电大学'.decode('utf8'))

    # You can not declear a constant value in python, just don't change it
    DictReadFileName = 'DictReadFileName'
    name = 'classify_crawler'
    allowed_domain = ['njupt.edu.cn']
    start_urls = [
            'http://www.njupt.edu.cn/'
            ]

    def __init__(self):
        dispatcher.connect(self.testInend, signals.spider_idle)

    def testInend(self):
        # Using pickle.dump to write a dict to a file which will over write the 
        # original
        with open(self.DictReadFileName, 'wb') as fp:
            pickle.dump(self.mostNewsDict, fp)
        print type(self.mostNewsDict)
        for key, item in self.mostNewsDict.iteritems():
            print item['depart'] + ' ' + item['section'] + item['title'] + ' ' + str(item['timestamp'])

    def parse(self, response):
        # This value is for debugging
        testurl = 2;

        #Determine if previous least recent data is stored by check the file existence
        #if so read it
        if (os.path.isfile(self.DictReadFileName)):
            self.firstCrawl = False
            with open(self.DictReadFileName, 'rb') as fp:
                self.mostNewsDictRead = pickle.load(fp)

        with open('urlset') as fp:
            nexturls = fp.read().splitlines()
            for url in nexturls:
                yield scrapy.Request(url, callback=self.secondparse)
            #yield scrapy.Request('http://rsc.njupt.edu.cn/', callback=self.secondparse)

    def secondparse(self, response):
        #Search for news block in html generally by guess
        depart = response.xpath('//title/text()').extract()[0]
        depart = depart.strip()
        depart = depart.replace('南京邮电大学'.decode('utf8'), '')
        if 'zs.njupt' in response.url:
            more_list = response.xpath('//div[@class="more"]/a/@href').extract()
        elif 'tdxy.njupt' in response.url:
            more_list = response.xpath('//*[@id="news"]/div[1]/span/a/@href').extract()
        elif 'bc.njupt' in response.url:
            more_list = response.xpath('//a[@id="more"]/@href').extract()
        elif 'kjc.njupt' in response.url:
            more_list = list()
            more_list.append(response.xpath('//*[@id="right"]/div[2]/div[1]/div/span[2]/a/@href'))
            more_list.append(response.xpath('//*[@id="dynamic"]/span[2]/a/@href'))
        else: 
            more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        if len(more_list) == 0:
            print response.url + 'no department'
            self.unhandlefp.write(response.url+'\n')
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
        print depart
        if self.firstCrawl or depart not in self.mostNewsDictRead:
            # Determine if this department is crawled firstly
            # It's worth noting that the firstcrawl parameter in scrapy.Request does not always save 
            # the same value as self.firstCrawl does. Though the cralwer may run
            # several times, but this section in the website has not crawled before now
            yield scrapy.Request(response.url, callback=self.njuptGeneralScheme, 
                dont_filter=True,meta={'depart': depart, 'timestamp': 2000, 'falsedepart': response.meta['depart'], 
                    'section': section, 'firstCrawl': True, 'gotStamp': True, 'backurl': response.url})
        else:
            yield scrapy.Request(response.url, callback=self.njuptGeneralScheme, 
                    dont_filter=True,meta={'depart': depart, 'falsedepart': response.meta['depart'], 
                        'section': section, 'firstCrawl': self.firstCrawl, 'backurl': response.url})

    def njuptGeneralScheme(self, response):
        if 'gotStamp' in response.meta:
            gotStamp = response.meta['gotStamp']
        else:
            gotStamp = False
        firstCrawl = response.meta['firstCrawl']
        count = 0
        gotNews = False
        depart = response.meta['depart']
        if not firstCrawl:
            depart = response.meta['depart']
            checkname = self.mostNewsDictRead[response.meta['depart']]['title']
            lasttimeStamp = self.mostNewsDictRead[response.meta['depart']]['timestamp']

        if len(response.xpath('//td[@class="postTime"]')) >= 5:
            gotNews = True
            if not firstCrawl:
                for news in response.xpath('//td[@class="postTime"]'):
                    if news.xpath('../td/a/font/text()').extract()[0] == checkname:
                        break
                    count = count + 1
                if count == 0:
                    self.mostNewsDict[depart] = self.mostNewsDictRead[depart]
            for news in response.xpath('//td[@class="postTime"]'):
                item = dict()
                if not firstCrawl and count == 0:
                    break
                item['depart'] = response.meta['falsedepart']
                item['date'] = news.xpath('text()').extract()[0]
                url = news.xpath('../td/a/@href').extract()[0]
                item['title'] = news.xpath('../td/a/font/text()').extract()[0]
                item['url'] = response.urljoin(url)
                item['section'] = response.meta['section']
                if not firstCrawl:
                    item['timestamp'] = lasttimeStamp + count
                    if depart not in self.mostNewsDict:
                        self.mostNewsDict[depart] = item
                    count = count - 1
                else:
                    if gotStamp and count == 0:
                        if 'title' in item:
                            self.mostNewsDict[depart] = item
                    item['timestamp'] = response.meta['timestamp'] - count
                    count = count + 1
                self.db.db_insert(item['depart'], item)
        else:
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
                        if not firstCrawl:
                            for news in newslist:
                                if len(news.xpath('.//a/font')) != 0:
                                    title = news.xpath('.//a/font/text()').extract()[0]
                                elif len(news.xpath('.//a/text()').extract()) != 0:
                                    title = news.xpath('.//a/text()').extract()[0]
                                else:
                                    continue
                                if (not firstCrawl) and title == checkname:
                                    break
                                count += 1
                        if not firstCrawl and count == 0:
                            self.mostNewsDict[depart] = self.mostNewsDictRead[depart]
                        for news in newslist:
                            item = dict()
                            if not firstCrawl and count == 0:
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
                            if not firstCrawl:
                                item['timestamp'] = count + self.mostNewsDictRead[depart]['timestamp']
                                count -= 1
                            else:
                                if gotStamp and count == 0:
                                    if 'title' in item:
                                        self.mostNewsDict[depart] = item
                                item['timestamp'] = response.meta['timestamp'] - count
                                count = count + 1

                            if not firstCrawl and depart not in self.mostNewsDict:
                                self.mostNewsDict[depart]= item
                            yield scrapy.Request(item['url'], callback=self.timeparse, meta={'item': item})
                        break;
        '''
        if firstCrawl:
            for sel in response.xpath('//a'):
                if len(sel.xpath('@title').extract()) != 0 and "下一页".decode('utf8') in sel.xpath('@title').extract()[0]:
                    if len(sel.xpath('@href')) != 0:
                        nexturl = sel.xpath('@href').extract()[0]
                        nexturl = response.urljoin(nexturl)
                        yield scrapy.Request(nexturl, callback=self.njuptGeneralScheme
                                , meta={'depart': response.meta['depart'], 'timestamp': response.meta['timestamp'] - count,
                                    'falsedepart': response.meta['falsedepart'], 'section': response.meta['section'],
                                'firstCrawl': response.meta['firstCrawl']})
        '''
        if not gotNews:
            self.unhandlefp.write(response.meta['backurl'] + '\n');


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
