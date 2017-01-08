# -*- coding: utf-8 -*-
import re
from datetime import datetime
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import NewsItem

class ReutersSpider(CrawlSpider):
    name = 'reuters'
    allowed_domains = ['jp.reuters.com']
    start_urls = ['http://jp.reuters.com/investing/currencies',
                  'http://jp.reuters.com/news',
                  'http://jp.reuters.com/topNews',
                  'http://jp.reuters.com/news/global-economy',
                  'http://jp.reuters.com/news/world',
                  'http://jp.reuters.com/news/business',
                  'http://jp.reuters.com/news/technology',
                  'http://jp.reuters.com/news/archive/']
    start_urls += ['http://jp.reuters.com/search/news?sortBy=&dateRange=&blob=%d'%x for x in range(2000, 2016)]
    
    def process_for_multi_pages(value):

        url_logger = logging.getLogger('url_process')
        
        if 'http://internal.jp.reuters.com/' in value:
            temp = 'http://jp.reuteres.com/' + value.split('/', 3)[3]
            url_logger.info('replace domain: <%s> to <%s>' % (value, temp))
            value = temp
            
        if 'http://jp.reuters.com/article/' in value:
            if '?sp=true' in value:
                return value
            else:
                return value.split('?pageNumber=')[0] + '?sp=true'
        else:
            return value
    
    rules = [Rule(LinkExtractor(deny=['http://jp.reuters.com/(%s).*$' % '|'.join(['video', 'info', 'tools', 'article', 'investing'])])),
             Rule(LinkExtractor(allow=['http://jp.reuters.com/(%s)/$' % '|'.join(['investing', 'investing/news'])])),
             Rule(LinkExtractor(allow=['http://jp.reuters.com/article.*'],
                                deny=['^.*\?pageNumber=([2-9]|[1-9][0-9]).*$', '^.*\?sp=true.+$'],
                                process_value=process_for_multi_pages),
                  callback='parse_articles',
                  follow=True)]

    
    def parse_articles(self, response):
        url = response.url
        item = NewsItem()
        item['URL'] = url
        m = re.search('idJP(.*?)\?', url)
        if m:
            item['ID'] = 'JP' + m.group(1)
        else:
            m = re.search('idJP(.*)$', url)
            if m:
                item['ID'] = 'JP' + m.group(1)
            else:
                item['ID'] = None
                self.logger.error('Cannot parse ID from url(%s)', url)
        item['category'] = response.xpath('//*[@class="article-section"]/text()').extract()[0]
        item['title'] = response.xpath('//h1[@class="article-headline"]/text()').extract()[0].replace('\u3000', ' ')
        item['content'] = ''.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@id="articleText"]//p/text()').extract()])
        item['publication_datetime'] = response.xpath('//*[@class="article-header"]//*[@class="timestamp"]/text()').extract()[0]
        item['scraping_datetime'] = datetime.now().strftime('%Y年 %m月 %d日 %H:%m JST')

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        
        print('****************************************')
        print('url     : ', item['URL'])
        print('id      : ', item['ID'])
        print('category: ', item['category'])
        print('title   : ', item['title'])
        
        return item
