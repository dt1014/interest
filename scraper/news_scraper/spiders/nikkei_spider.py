# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta
from itertools import takewhile
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import NikkeiItem

def process(url):
    m = re.search('http://www.nikkei.com/article/(.+?)/', url)
    if m:
        return m.group(0)
    
class NikkeiSpider(CrawlSpider):
    name = 'nikkei'

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
    }
    
    allowed_domains = ['www.nikkei.com']

    start_urls = ['http://www.nikkei.com/']

    rules = [Rule(LinkExtractor(allow=['http://www.nikkei.com/article/.+'],
                                process_value=process),
                  callback='parse_articles',
                  follow=True),
             Rule(LinkExtractor(deny=['http://www.nikkei.com/lounge/help',
                                      'http://www.nikkei.com/help/',
                                      'http://www.nikkei.com/info/',
                                      'http://www.nikkei.com/etc/accounts/',
                                      'http://www.nikkei.com/pressrelease',
                                      'http://www.nikkei.com/nkd/company/']))]
    
    def parse_articles(self, response):
        url = response.url
        item = NikkeiItem()
        item['URL'] = url
        item['ID'] = re.search('http://www.nikkei.com/article/(.+?)/', url).group(1)
        item['title'] = re.sub('\u3000', ' ', response.xpath('//*/title/text()').extract_first())
        item['content'] = re.sub('[\u3000\r\n]', '<br>', '<br>'.join(response.xpath('//*/div[@itemprop="articleBody"]//text()').extract()))

        templates_datetime = ['%Y/%m/%d %H:%M', '%Y/%m/%d付']
        for template in templates_datetime:
            try:
                item['publication_datetime'] = datetime.strptime(response.xpath('//*/dd[@class="cmnc-publish"]//text()').extract_first(),
                                                                 template)
                break
            except ValueError:
                continue
        item['scraping_datetime'] = datetime.now()
        
        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        return item

        
