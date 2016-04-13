# -*- coding: utf-8 -*-
import scrapy


class TestSpiderSpider(scrapy.Spider):
    name = "test_spider"
    allowed_domains = ["http://www.njupt.edu.cn"]
    start_urls = (
        'http://www.http://www.njupt.edu.cn/',
    )

    def parse(self, response):
        pass
