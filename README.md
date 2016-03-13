# 爬虫说明文档
南邮官网的爬虫是在python语言下基于scrapy框架下实现的。

从南邮主页开始爬虫查找所有具有href属性的a标签a标签所指向的地址并输出a标签所属的块的文本（也就是被查找a标签的父节点）。特别的，如果两个a标签属于相同的块那么这个块只会被输出一次。在处理完一个页面中的所有a标签后，开始处理之前保存的地址。

主要代码如下:
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
