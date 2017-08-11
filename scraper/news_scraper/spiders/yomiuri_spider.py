# -*- coding: utf-8 -*-
import re
import time
from datetime import datetime
import logging
import numpy as np
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import YomiuriItem

class YomiuriSpider(CrawlSpider):
    name = 'yomiuri'

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'ROBOTSTXT_OBEY': False
    }
    
    allowed_domains = ['www.yomiuri.co.jp',
                       'yomidr.yomiuri.co.jp']

    start_urls = ['http://www.yomiuri.co.jp/',
                  'https://yomidr.yomiuri.co.jp/']
    
    rules = [Rule(LinkExtractor(allow=['http://www.yomiuri.co.jp/.+/[0-9]{8}-']),
                  callback='parse_articles',
                  follow=True),
             Rule(LinkExtractor(allow=['http://www.yomiuri.co.jp/stream/?']),
                  callback='parse_streams',
                  follow=True),
             Rule(LinkExtractor(allow=['https://yomidr.yomiuri.co.jp/article/[0-9]{8}-'],
                                deny=['https://yomidr.yomiuri.co.jp/(byoin-no-jitsuryoku|iryo-sodan|seminar-event)/.+', '\?catname=(iryo-sodan|seminar-event_event-forum|exercise_murofushi-yuka|tobyoki_ichibyo-sokusai|column_hon-yomidoku-do|iryo-taizen)$']),
                  callback='parse_medical',
                  follow=True),
             Rule(LinkExtractor())]

    def parse_medical(self, response):
        url = response.url
        item = YomiuriItem()
        item['URL'] = url
        item['title'] = ''
 
        if response.xpath('//*[@name="xyomidr:category"]/@content').extract_first() == 'ニュース':
            try:
                item['title'] = response.xpath('//title/text()').extract_first().replace('\u3000', ' ')
                item['category'] = 'medical'
                item['content'] = re.sub('[\n\r\u3000]', '<br>', ''.join(response.xpath('//*/div[@class="edit-area"]/p[@itemprop="articleBody"]//text()').extract()))
                item['publication_datetime'] = datetime.strptime(response.xpath('//*/header[@class="blog-header"]//time/text()').extract_first(),
                                                                 '%Y年%m月%d日')
                item['scraping_datetime'] = datetime.now()
                
            except:
                item['title'] = ''

        if len(item['title']) != 0:
            self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
                
        return item
        
    def parse_articles(self, response):
        url = response.url
        item = YomiuriItem()
        item['URL'] = url
        item['ID'] = re.search('(.+)/(.+?)\.html', url).group(2)
        item['category'] = re.search('http://www.yomiuri.co.jp/(.+?)/'+item['ID'], url).group(1)
        item['title'] = response.xpath('//*/div[@class="article text-resizeable"]/article/h1/text()').extract_first().replace('\u3000', ' ')
        item['content'] = re.sub('[\n\r\u3000]', '<br>', ''.join(response.xpath('//*/div[@class="article text-resizeable"]/article/*[@itemprop="articleBody"]//text()').extract()))
        try:
            item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="date-upper"]/time/text()').extract_first(),
                                                             '%Y年%m月%d日 %H時%M分')
        except ValueError:
            item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="date-upper"]/time/text()').extract_first(),
                                                             '%Y年%m月%d日')
        item['scraping_datetime'] = datetime.now()

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        
        return item
        
    def parse_streams(self, response):
        url = response.url

        item['ID'] = re.search('/\?id=(.+)', response.xpath('head/link[@rel="canonical"]/@href').extract_first()).group(1)
        item['category'] = 'stream'
        item['title'] = response.xpath('//*/p[@class="movieTitle"]/text()').extract_first().replace('\u3000', '')   
        content_check = response.xpath('//*/p[@class="detailText typeB"]//text()').extract()
        if content_check:
            item['content'] = content_check
        else:
            item['content'] = response.xpath('//*/p[@class="detailText"]//text()').extract()
        item['publication_datetime'] = datetime.strptime(response.xpath('//*/p[@style="display:none"]/text()').extract_first(),
                                                         '%Y年%m月%d日')
        item['scraping_datetime'] = datetime.now()

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        
        return item
        
