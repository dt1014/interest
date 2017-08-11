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

from news_scraper.items import SankeiItem

class SankeiSpider(CrawlSpider):
    name = 'sankei'
    allowed_domains = ['www.sankei.com']

    start_urls = ['http://www.sankei.com/',
                  'http://www.sankei.com/photo/']
    
    # 初めのページのみをリンク抽出、parse_multple_articlesを適用、次々とページを辿りながらパースする
    rules = [Rule(LinkExtractor(allow=['http://www.sankei.com/photo/(movie|story|daily)/news/\d+?/.+?\.html$']),
                  callback='parse_photo',
                  follow=True),
             Rule(LinkExtractor(allow=['http://www.sankei.com/.+?/print/\d+?/.+?\.html$']),
                  callback='parse_print',
                  follow=True),
             Rule(LinkExtractor(allow=['http://www.sankei.com/.+?/news/\d+?/.+?-n1\.html$']),
                  callback='parse_multiple_articles',
                  follow=True),
             Rule(LinkExtractor(deny=['http://www.sankei.com/.+?/photos/\d+?/.+?\.html',
                                      'http://www.sankei.com/english/news/.*\.html',
                                      'http://www.sankei.com/english/print/.*\.html'])),
             Rule(LinkExtractor(allow=['http://www.sankei.com/photo/(movie|story|daily)/.*']))]
    
    def parse_photo(self, response):
        url = response.url
        item = SankeiItem()
        item['URL'] = url
        item['ID'] = re.search('http://www.sankei.com/.+?/.+?/\d+?/(.+)-', url).group(1)
        item['category'] = re.search('http://www.sankei.com/(.+?)/', url).group(1)
        item['page_count'] = 1
        item['title'] = response.xpath('//*/span[@id="__v_content_title__"]//text()').extract_first().replace('\u3000', ' ')
        item['content'] = re.sub('[\n\r\u3000]', '<br>', '<br>'.join(response.xpath('//*/div[@class="clearfix"]/p//text()').extract()))
        if '/story/' in url or '/movie/' in url:
            item['publication_datetime'] = datetime.strptime(response.xpath('//*/span[@class="addition"]/time/text()').extract_first(),
                                                             '%Y.%m.%d %H:%M')
        else:
            item['publication_datetime'] = datetime.strptime(response.xpath('//*/article[@class="articlePhoto"]/h2/text()').extract_first(),
                                                             '%Y.%m.%dのニュース')
        item['scraping_datetime'] = datetime.now()

        return item
            
    def parse_print(self, response):
        url = response.url
        item = SankeiItem()
        item['URL'] = url
        item['ID'] = re.search('http://www.sankei.com/.+?/.+?/\d+?/(.+)-', url).group(1)
        item['category'] = re.search('http://www.sankei.com/(.+?)/', url).group(1)
        item['page_count'] = 1
        item['title'] = response.xpath('//*/article[@class="modPrint"]/h1/text()').extract_first().replace('\u3000', ' ')
        item['content'] = '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*/article[@class="modPrint"]/p//text()').extract()])
        item['publication_datetime'] = datetime.strptime(response.xpath('//*/article[@class="modPrint"]/time/text()').extract_first(),
                                                         '%Y.%m.%d %H:%M')
        item['scraping_datetime'] = datetime.now()
        return item
        
    def parse_multiple_articles(self, response):

        next_url = response.xpath('//*/p[@class="pageNextsubhead"]//@href').extract()

        if len(next_url) == 0:
            yield self.parse_article(response)
    
        else:
            next_url = re.search('.+/', response.url).group(0) + next_url[0].split('/')[-1]
            request = Request(next_url, callback=self.parse_multiple_articles)
            item = self.parse_article(response)
            request.meta['item'] = item
            yield request
    
    def parse_article(self, response):

        if not 'item' in response.meta.keys():
            item = self.get_item(response)
            item['page_count'] = 1
            self.logger.info('first scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        else:
            item = self.add_item(response)
            item['page_count'] += 1
            self.logger.info('scraped and added from <%s> published in %s' % (response.url, item['publication_datetime']))

        return item
            
    def get_item(self, response):
        
        url = response.url
        item = SankeiItem()
        item['URL'] = url
        item['ID'] = re.search('http://www.sankei.com/.+?/.+?/\d+?/(.+)-', url).group(1)
        item['category'] = re.search('http://www.sankei.com/(.+?)/', url).group(1)
        try:
            item['title'] = response.xpath('//*/article[@class="clearfix"]/h1/text()').extract_first().replace('\u3000', ' ')
        except:
            item['title'] = response.xpath('//*/section[@class="articleText clearfix"]//h1/text()').extract_first().replace('\u3000', ' ')
            
        item['content'] = '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*/div[@class="fontMiddiumText"]/p//text()').extract()])
        item['publication_datetime'] = datetime.strptime(response.xpath('//*/span[@id="__r_publish_date__"]//text()').extract_first(),
                                                         '%Y.%m.%d %H:%M')
        
        item['scraping_datetime'] = datetime.now()
        
        return item
  
    def add_item(self, response):
        item = response.meta['item']
        item['content'] += '<br>' + '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*/div[@class="fontMiddiumText"]/p//text()').extract()])
        return item
