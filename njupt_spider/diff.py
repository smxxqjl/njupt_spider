        depart = response.meta['depart']
        count = 0
        checkname = self.mostNewsDictRead[response.meta['depart']]['title']
        lasttimeStamp = self.mostNewsDictRead[response.meta['depart']]['timestamp']

        if len(response.xpath('//td[@class="postTime"]')) >= 5:
            for news in response.xpath('//td[@class="postTime"]'):
                if news.xpath('../td/a/font/text()').extract()[0] == checkname:
                    break
                count = count + 1
            if count == 0:
                self.mostNewsDict[depart] = self.mostNewsDictRead[depart]
            for news in response.xpath('//td[@class="postTime"]'):
                item = dict()
                if count == 0:
                    break
                item['depart'] = response.meta['falsedepart']
                item['date'] = news.xpath('text()').extract()[0]
                url = news.xpath('../td/a/@href').extract()[0]
                item['title'] = news.xpath('../td/a/font/text()').extract()[0]
                item['url'] = response.urljoin(url)
                item['timestamp'] = lasttimeStamp + count
                item['section'] = response.meta['section']
                if depart not in self.mostNewsDict:
                    self.mostNewsDict[depart] = item
                self.db.db_insert(item['depart'], item)

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
                            if title == checkname:
                                break
                            count += 1
                        if count == 0:
                            self.mostNewsDict[depart] = self.mostNewsDictRead[depart]
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
                            item['timestamp'] = count + self.mostNewsDictRead[depart]['timestamp']
                            count -= 1
                            if depart.encode('utf8') not in self.mostNewsDict:
                                self.mostNewsDict[depart.encode('utf8')]= item
                            yield scrapy.Request(item['url'], callback=self.timeparse, meta={'item': item})
                        break;
