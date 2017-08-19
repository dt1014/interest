# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta
from itertools import takewhile
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import BloombergItem

class BloombergSpider(CrawlSpider):
    name = 'bloomberg'

    custom_settings = {
        'DOWNLOAD_DELAY': 10,
    }
    
    allowed_domains = ['www.bloomberg.co.jp']

    start_urls = ['https://www.bloomberg.co.jp']

    rules = [Rule(LinkExtractor(allow=['https://www.bloomberg.co.jp/news/articles/']),
                  callback='parse_articles',
                  follow=True),
             Rule(LinkExtractor(allow=['https://www.bloomberg.co.jp/news/videos/']),
                  callback='parse_videos',
                  follow=True),
             Rule(LinkExtractor(deny=['https://www.bloomberg.co.jp/(markets|quote|press-releases)/']))]
    
    def parse_articles(self, response):
        url = response.url
        item = BloombergItem()
        item['URL'] = url
        item['ID'] = re.sub('/', '-', re.search('https://www.bloomberg.co.jp/news/articles/(.+)', url).group(1))
        item['category'] = 'article'
        item['title'] = response.xpath('//*/title/text()').extract_first()
        item['content'] = re.sub('[\n\r\u3000]', '<br>','<br>'.join(response.xpath('//*/div[@class="article-body__content"]/p//text()').extract()))
        item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="published-info"]/time[@itemprop="datePublished"]/text()').extract_first().strip(),
                                                       '%Y年%m月%d日 %H:%M JST')
        item['scraping_datetime'] = datetime.now()

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        
        return item
        
    def parse_videos(self, response):
        url = response.url
        item = BloombergItem()
        item['URL'] = url
        item['ID'] = re.sub('/', '-', re.search('https://www.bloomberg.co.jp/news/videos/(.+)', url).group(1))
        item['category'] = 'video'
        item['title'] = response.xpath('//*/title/text()').extract_first()
        item['content'] = re.sub('[\n\r\u3000]', '<br>','<br>'.join(response.xpath('//*/div[@class="video-metadata__summary"]//text()').extract()))
        item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="video-metadata__footer"]/time/text()').extract_first().strip(),
                                                         '%Y年%m月%d日 %H:%M JST')
        item['scraping_datetime'] = datetime.now()

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))

        return item
