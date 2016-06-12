# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from bayes_test import bayes_test
import scrapy


class BayesSpiderSpider(scrapy.Spider):
    spesuffix = file('spesuffix', 'r').read().splitlines()
    name = "bayes_spider"
    allowed_domains = ["njupt.edu.cn",
            "nuaa.edu.cn"]
    start_urls = (
            'http://www.njupt.edu.cn/',
            )

    def getfullpath(self, curpath):
        lastname = curpath.xpath('local-name()')[0].extract()
        lasttext = curpath.extract()
        returnpath = ''
        
        # Loop until at the top of tree
        while len(curpath.xpath('..')) != 0:
            curpath = curpath.xpath('..')[0]
            childtags = curpath.xpath('./' + lastname)
            tagorder = 1
            for tag in childtags:
                # tagorder indicates the order of tag in this layer e.g. tr[5]
                # ps. the tagorder starts from 1
                if tag.extract() == lasttext:
                    lastname = curpath.xpath('local-name()')[0].extract()
                    remname = tag.xpath('local-name()')[0].extract()
                    returnpath = '/' + remname + '[' + str(tagorder) +']' + returnpath
                    break;
                tagorder = tagorder + 1
            lasttext = curpath.extract()
        returnpath = '/' + curpath.xpath('local-name()').extract()[0] + returnpath
        return returnpath

    def parse(self, response):
        # Read the urlset which is the department address of the website
        with open('urlset') as fp:
            nexturls = fp.read().splitlines()
            for url in nexturls:
                baseurl = url.split('/')[2]
                yield scrapy.Request(url, callback=self.secondparse, meta={'depth': 1, 'baseurl': baseurl})
    
    def secondparse(self, response):
        atags = response.xpath('//a')
        print 'tag num is' + str(len(atags))
        print 'The base url is' + response.meta['baseurl']

        for atag in atags:
            try:
                href = atag.xpath('@href').extract()[0]
            except:
                print atag
                print 'is out of range'
            url = response.urljoin(href)
            ### Rule to filter url
            if response.meta['baseurl'] not in url:
                continue
            for suffix in self.spesuffix:
                if href.endswith(suffix):
                    print "This url in not goint to visit"
                    continue
            if response.meta['depth'] == 1:
                depart = response.xpath('//title/text()').extract()[0]
                depart = depart.replace('南京邮电大学'.decode('utf8'), '')
                yield scrapy.Request(url, callback=self.secondparse, meta={'depth': 2, 
                    'depart': depart, 'baseurl': response.meta['baseurl']})
            elif response.meta['depth'] == 2:
                section = response.xpath('//title/text()').extract()[0]
                section = section.replace('南京邮电大学'.decode('utf8'), '')
                yield scrapy.Request(url, callback=self.thirdparse, meta={'path': atag,
                    'depart': response.meta['depart'], 'section': section, 'backurl': response.url})
            else:
                # This branch should never be reach just in case
                return

    #Here should be the core part of this crawl scheme
    def thirdparse(self, response):
        isnews = bayes_test(response.body, 0.9)
        if isnews:
            newspath = self.getfullpath(response.meta['path'])
            print newspath
            with open('newsxpath', 'a') as fp:
                fp.write(response.meta['backurl'] + newspath + '\n')
        else:
            return
