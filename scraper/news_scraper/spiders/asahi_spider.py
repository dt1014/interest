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

from news_scraper.items import AsahiItem

class AsahiSpider(CrawlSpider):
    name = 'asahi'
    allowed_domains = ['www.asahi.com']

    start_urls = ['http://www.asahi.com',
                  'http://www.asahi.com/koshien',
                  'http://www.asahi.com/apital/',
                  'http://www.asahi.com/tech_science/']

    rules = [Rule(LinkExtractor(allow=['http://www.asahi.com/articles/.*',
                                       'http://www.asahi.com/(koshien|apital|tech_science)/articles']),
                  callback='parse_first',
                  follow=True),
             Rule(LinkExtractor(deny=['http://www.asahi.com/(shimen|area|corporate|shimbun|special|ad|msta)/.+',
                                      'http://www.asahi.com/and_.+']),
                  callback='parse_second',
                  follow=True)]

    def parse_first(self, response):

        url = response.url
        item = AsahiItem()
        item['URL'] = url
        item['title'] = ''
        if '/articles/photo/' in url:
            pass
        else:
            try:
                if 'tech_science/cnet/' in url:
                    item['ID'] = re.search('cnet/(.+)?\.html\??', url).group(1)
                else:
                    item['ID'] = re.search('articles/(.+)?\.html\??', url).group(1)
                
                    title_check = response.xpath('//*/div[@class="Title"]/h1/text()').extract_first()
                    if title_check:
                        item['title'] = title_check.replace('\u3000', ' ')
                        item['tag'] = ' '.join([x for x in response.xpath('/*//ul[@class="Tag"]//text()').extract() if x != '\n' and x != '\n\t'])
                        item['content'] = re.sub('[\n\r\u3000]', '<br>', '<br>'.join(response.xpath('//*/div[@class="ArticleText"]/p//text()').extract()))
                        item['member'] = False if len(response.xpath('//*/div[@class="MoveLink"]/ul//text()').extract()) == 0 else True
                        item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="Title"]/p[@class="LastUpdated"]/text()').extract_first(),
                                                                         '%Y年%m月%d日%H時%M分')
                        item['scraping_datetime'] = datetime.now()
                    else:
                        item['title'] = response.xpath('//*/div[@class="mod-headingB01 border-none"]/h1/text()').extract_first()
                        item['tag'] = ' '.join([x for x in response.xpath('/*//ul[@class="Tag"]//text()').extract() if x != '\n' and x != '\n\t'])
                        item['content'] = re.sub('[\n\r\u3000]', '<br>', '<br>'.join(response.xpath('//*/div[@class="text-block"]/p//text()').extract()))
                        item['member'] = False if len(response.xpath('//*/div[@class="MoveLink"]/ul//text()').extract()) == 0 else True
                        item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="row"]/p[@class="date"]/text()').extract_first(),
                                                                         '%Y年%m月%d日%H時%M分')
                        item['scraping_datetime'] = datetime.now()
                    
            except:
                item['title'] = ''
                    
        return item
