# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta
from itertools import takewhile
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import AFPItem

def process(url):
    m = re.search('(http://www.afpbb.com/articles/(.+?))(\?|$)', url)
    if m:
        return m.group(1)
    
class AFPSpider(CrawlSpider):
    name = 'afp'

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
    }
    
    allowed_domains = ['www.afpbb.com']

    start_urls = ['http://www.afpbb.com/']

    rules = [Rule(LinkExtractor(allow=['http:\/\/www\.afpbb\.com\/articles\/.+'],
                                process_value=process),
                  callback='parse_articles',
                  follow=True),
             Rule(LinkExtractor(deny=['http:\/\/www\.afpbb\.com\/articles\/.+']))]

    def parse_articles(self, response):
        url = response.url
        item = AFPItem()
        item['URL'] = url
        item['ID'] = re.search('http://www.afpbb.com/articles/(.+)', url).group(1)
        item['category'] = re.search('(.+?)/', item['ID']).group(1)
        item['title'] = re.sub('\u3000', ' ', response.xpath('//*/title/text()').extract_first())

        content_templates = ['//*/div[@class="article-body clear"]//text()',
                             '//*/div[@class="body-txt"]//text()']
        for template in content_templates:
            check = re.sub('[\u3000\r\n]', '<br>', '<br>'.join(response.xpath(template).extract()))
            if len(check) > 0:
                item['content'] = check
                break

        pubdate_templates = [('//*/header[@id="signage"]//p[@class="day"]/text()', '%Y年%m月%d日 %H:%M\u3000'),
                             ('//*/div[@class="day"]/text()', '%Y年%m月%d日 %H:%M\u3000'),]
        for template1, template2 in pubdate_templates:
            try:
                item['publication_datetime'] = datetime.strptime(response.xpath(template1).extract_first(), template2)
                break
            except (TypeError, ValueError):
                continue
            
        item['scraping_datetime'] = datetime.now()

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        return item
