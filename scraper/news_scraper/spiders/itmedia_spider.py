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

from news_scraper.settings import DOWNLOAD_DELAY
from news_scraper.items import ITMediaItem

class ITMediaSpider(CrawlSpider):
    name = 'itmedia'
    allowed_domains = ['www.itmedia.co.jp',
                       'mag.executive.itmedia.co.jp',
                       'marketing.itmedia.co.jp',
                       'techfactory.itmedia.co.jp']

    themes = ['news', 'business', 'enterprise', 'smartjapan', 'mobile', 'pcuser', 'lifestyle']
    
    start_urls = ['http://www.itmedia.co.jp/',
                  'http://mag.executive.itmedia.co.jp/',
                  'http://marketing.itmedia.co.jp/',
                  'http://techfactory.itmedia.co.jp/']
    start_urls += ['http://www.itmedia.co.jp/%s'%x for x in themes]
    
    rules = [Rule(LinkExtractor(allow=['http://.*itmedia\.co\.jp/.*'],
                                deny=['http://.*/articles/\d{4}/\d{2}/news.*\.html'])),
             Rule(LinkExtractor(allow=['http://.*/articles/\d{4}/\d{2}/news\d+\.html']),
                  callback='parse_multiple_articles',
                  follow=True)]
             # Rule(LinkExtractor(allow=['http://techtarget.itmedia.co.jp/.*'],
             #                    deny=['http://techtarget.itmedia.co.jp/tt/news/\d{4}/\d{2}/news.*\.html'])),
             # Rule(LinkExtractor(allow=['http://techtarget.itmedia.co.jp/tt/news/\d{4}/\d{2}/news\d+\.html']),
             #      callback='parse_multiple_articles',
             #      follow=True)]

    def parse_multiple_articles(self, response):

        member_restriction = response.xpath('//*/div[@id="CmsMembersControl"]//text()').extract()
        next_url = response.xpath('//head/link[@rel="next"]/@href').extract()

        if len(member_restriction) > 0:
            item = ITMediaItem()
            item['URL'] = response.url
            yield item
        
        if len(next_url) == 0:
            yield self.parse_article(response)
    
        else:
            next_url = re.search('^.*\.co\.jp', response.url).group(0) + next_url[0]
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
        item = ITMediaItem()
        item['URL'] = url
        item['ID'] = url.split('articles/')[-1].split('.html')[0].replace('/', '-')
        item['category'] = url.split('.jp/')[-1].split('/articles')[0]
        item['title'] = response.xpath('//title/text()').extract_first().replace('\u3000', ' ')
        item['introduction'] = ''.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@id="cmsAbstract"]//text()').extract()])
        item['content'] = '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@class="inner"]//p//text()').extract()])

        for update in response.xpath('//*[@id="update"]//text()').extract():
            try:
                item['publication_datetime'] = datetime.strptime(re.sub(' |\u3000', '', update),
                                                                 '%Y年%m月%d日%H時%M分UPDATE')
                break
            except ValueError:
                continue
                
        item['scraping_datetime'] = datetime.now()
        
        return item
  
    def add_item(self, response):
        item = response.meta['item']
        item['content'] += '<br>' + '<br>'.join([x.replace('\u3000', ' ') for x in response.xpath('//*[@class="inner"]//p//text()').extract()])
        return item
