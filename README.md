### 南京邮电大学新闻抓取爬虫
使用scrapy框架， 抓取南京邮电大学主要部门的新闻咨询， 并保存信息于远程mongodb服务器。 根目录后输入 `scrapy crawl classify_crawler` 开始运行， 爬虫会读取njupt_spider/urlset中的网址进行抓取， 主要代码在njupt_spider/njupt_spider/spiders/classify_crawler.py中。
