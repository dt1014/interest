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

from news_scraper.items import YomidrItem

class YomidrSpider(CrawlSpider):
    name = 'yomidr'

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': False
    }
    
    allowed_domains = ['yomidr.yomiuri.co.jp']

    start_urls = ['https://yomidr.yomiuri.co.jp/']

    rules = [Rule(LinkExtractor(allow=['https://yomidr.yomiuri.co.jp/article/[0-9]{8}-'],
                                deny=['https://yomidr.yomiuri.co.jp/(byoin-no-jitsuryoku|iryo-sodan|seminar-event)/.+', '\?catname=']),
                  callback='parse_medical',
                  follow=True),
             Rule(LinkExtractor(deny=['.html?url=']))]

    def parse_medical(self, response):
        url = response.url
        item = YomidrItem()
        item['URL'] = url
        item['title'] = ''

        check = response.xpath('//*[@name="xyomidr:category"]/@content').extract_first()
        
        if check == 'ニュース' or check == '深層プラス for yomiDr.':
            try:
                item['ID'] = re.search('/article/(.+?)(/|$)', url).group(1)
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
