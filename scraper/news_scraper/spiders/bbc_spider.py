# -*- coding: utf-8 -*-
import re
from datetime import datetime
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import BBCItem

class BBCSpider(CrawlSpider):
    name = 'bbc'
    allowed_domains = ['www.bbc.com']
    start_urls = ['http://www.bbc.com/japanese',
                  'http://www.bbc.com/japanese/features_and_analysis']

    rules = [Rule(LinkExtractor(allow=['http://www.bbc.com/japanese/.*'],
                                deny=['http://www.bbc.com/japanese/\d+',
                                      'http://www.bbc.com/japanese/features-and-analysis-\d+'])),
             Rule(LinkExtractor(allow=['http://www.bbc.com/japanese/\d+',
                                       'http://www.bbc.com/japanese/features-and-analysis-\d+']),
                                callback='parse_articles',
                                follow=True)]
                            
    def parse_articles(self, response):
        url = response.url
        item = BBCItem()
        item['URL'] = url
        m = re.search('(features-and-analysis-\d+|\d+)', url)
        if m:
            item['ID'] = m.group(0)
        else:
            item['ID'] = ''
            self.logger.error('Cannot parse ID from url: <%s>', url)

        item['title'] = response.xpath('//title/text()').extract_first().replace('\u3000', ' ')
        item['introduction'] = ''.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@class="story-body__introduction"]//text()').extract()])
        item['content'] = '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@class="story-body__inner"]/p//text()').extract()])
        if len(item['content']) == 0:
            item['content'] = '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@class="story-body"]/p//text()').extract()])
        
        item['publication_datetime'] = response.xpath('//*[@class="date date--v2"]//text()').extract()[0]
        item['publication_datetime'] = datetime.strptime(item['publication_datetime'],
                                                         '%Y年%m月%d日')    
        item['scraping_datetime'] = datetime.now()
        
        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))

        return item
  
