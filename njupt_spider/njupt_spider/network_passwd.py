# -*- coding: utf-8 -*-
import scrapy


class NetworkPasswdSpider(scrapy.Spider):
    name = "network_passwd"
    allowed_domains = ["192.168.168.168", "www.taobao.com"]
    start_urls = (
        'http://www.192.168.168.168/',
    )

    def parse(self, response):

