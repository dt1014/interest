# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from itertools import takewhile
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import GigazineItem

N = 10000

class GigazineSpider(CrawlSpider):
    name = 'gigazine'
    allowed_domains = ['gigazine.net']
    start_urls = ['http://gigazine.net/']
    date_list = list(takewhile(lambda x: x > datetime(2005, 7, 1), map(lambda x: datetime.today()-timedelta(weeks=x)*4, range(0, N))))
    start_urls += ['http://gigazine.net/news/%s/%02d/%02d/'%(x.year, int(x.month), int(x.day)) for x in date_list]

    rules = [Rule(LinkExtractor(allow=['http://gigazine.net/.*'],
                                deny=['http://gigazine.net/news/\d{8}.*'])),
             Rule(LinkExtractor(allow=['http://gigazine.net/news/\d{8}.*']),
                                callback='parse_articles',
                                follow=True)]
                            
    def parse_articles(self, response):
        url = response.url
        item = GigazineItem()
        item['URL'] = url
        item['ID'] = url.split('http://gigazine.net/news/')[1].replace('/', '')
        item['tag'] = ' '.join(response.xpath('//*/div[@class="items"]/p/a//text()').extract())
        item['title'] = response.xpath('//title/text()').extract_first().replace('\u3000', ' ')
        item['content'] = ''.join([x for x in response.xpath('//*[@class="preface"]//text()').extract()])
        item['publication_datetime'] = datetime.strptime(re.sub(' |\u3000', '', response.xpath('//*/time[@class="yeartime"]//text()').extract()[0]),
                                                         '%Y年%m月%d日%H時%M分%S秒')
        item['scraping_datetime'] = datetime.now()
        
        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))

        return item
  
