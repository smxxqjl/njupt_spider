# -*- coding: utf-8 -*-
import scrapy


class ZxjspiderSpider(scrapy.Spider):
    fp = file('zxjdata', 'w')
    name = "zxjspider"
    allowed_domains = ["njupt.edu.cn"]
    start_urls = (
        'http://www.njupt.edu.cn/',
    )
    result = list()

    def parse(self, response):
        urldict = dict()
        if 'depth' not in response.meta:
            depth = 1
        else:
            depth = response.meta['depth']
        if depth > 3:
            return
        hreflen = len(response.xpath('//a'))
        total = num = 0
        for href in response.xpath('//a/@href').extract():
            num += 1
            href = response.urljoin(href)
            yield scrapy.Request(href, meta={'depth': depth})
            total += len(href)
        if num != 0:
            average = total / num
        else:
            average = 0
        urldict['url'] = response.url
        urldict['average'] = average
        urldict['depth'] = depth
        urldict['urlnum'] = num
        self.fp.write(response.url + ' ' + str(average) + ' ' + str(depth) + ' ' + str(num) + '\n')
        self.result.append(urldict)
