# -*- coding: utf-8 -*-
import scrapy
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from njupt_spider.MongoDB_Driver import MongoDB_Driver

class departCrawler(scrapy.Spider):
    # each element is a dict has a key depart and sectionlist
    # holds all section
    name = 'depart_crawler'
    departDict = dict()
    db = MongoDB_Driver('180.209.64.38', 40020, '南京邮电大学'.decode('utf8'))

    allowed_domain = ['njupt.edu.cn']
    start_urls = [
            'http://www.njupt.edu.cn'
            ]
    def __init__(self):
        dispatcher.connect(self.toMongo, signals.spider_idle)

    def toMongo(self):
        for key, value in self.departDict.iteritems():
            self.db.db_insert('departments', value)
    
    def parse(self, response):
        with open('urlset') as fp:
            nexturls = fp.read().splitlines()
            for url in nexturls:
                yield scrapy.Request(url, callback=self.secondparse)

    def secondparse(self, response):
        depart = response.xpath('//title/text()').extract()[0]
        #Erase annoyed space and newline
        depart = depart.strip()
        departDict = dict()
        departDict['department'] = depart
        departDict['sectionList'] = list()
        self.departDict[depart] = departDict

        more_list = response.xpath('//div[@align="right"]/a/@href').extract()
        for url in more_list:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.thirdparse, meta={'depart': depart})

    def thirdparse(self, response):
        section = response.xpath('//title/text()').extract()[0]
        section = section.strip()
        self.departDict[response.meta['depart']]['sectionList'].append(section)
