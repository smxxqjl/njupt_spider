# -*- coding: utf-8 -*-
import scrapy


class TestSpiderSpider(scrapy.Spider):
    name = "test_spider"
    allowed_domains = ["njupt.edu.cn",
            "nuaa.edu.cn"]
    start_urls = (
            'http://www.njupt.edu.cn/',
            )

    def parse(self, response):
        ptags = response.xpath('//p')
        print ptags[0]
        print ptags[0].extract()
        print '---------------------------------'
        newpath = ptags[0].xpath('..')
        print newpath.extract()[0]
