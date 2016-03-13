# -*- coding: utf-8 -*-
import os

import scrapy


class NoDisrSpiderSpider(scrapy.Spider):
    if not os.path.exists('data'):
        os.mkdir('data')

    name = "no_dis_spider"
    allowed_domains = ["njupt.edu.cn"]
    start_urls = (
        'http://www.njupt.edu.cn/',
    )
    # Store the visited urls.
    url_set = set()
    writetofile = open('data/njupt_data', 'w')

    def parse(self, response):
        self.url_set.add(response.url)
        # Get all the 'a' elements with href attributes
        path_list = response.xpath('//a[@href]')
        lastcontent = ''
        tovisit_urls = set()

        for path in path_list:
            url = response.urljoin(path.xpath('@href').extract()[0])
            print url
            if url not in self.url_set:
                tovisit_urls.add(url)
            content = path.xpath('..').extract()[0]
            # The content and last content value is to deal with one block with multiple href
            # With this The output file may reduce duplicated result
            if content != lastcontent:
                self.writetofile.write(content.encode('utf-8') + '\n\n')
            lastcontent = content

        for url in tovisit_urls:
            yield scrapy.Request(url, callback=self.parse)
