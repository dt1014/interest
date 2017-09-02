# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta
from itertools import takewhile
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scraper.items import ZaikeiItem

def process(url):
    m = re.search('(http://www\.zaikei\.co\.jp/article/(.+?))(\?|$)', url)
    if m:
        return m.group(1)
    
class ZaikeiSpider(CrawlSpider):
    name = 'zaikei'

    custom_settings = {
        'DOWNLOAD_DELAY': 6,
    }
    
    allowed_domains = ['www.zaikei.co.jp']
    
    start_urls = ['http://www.zaikei.co.jp/',
                  'http://www.zaikei.co.jp/search/index.php?cx=partner-pub-2349110898842832%3Acn457n-qwfs&cof=FORID%3A9&ie=UTF-8&q=2010&sa.x=0&sa.y=0&sa=%E6%A4%9C%E7%B4%A2' # 2010で検索
                  'http://www.zaikei.co.jp/search/index.php?cx=partner-pub-2349110898842832%3Acn457n-qwfs&cof=FORID%3A9&ie=UTF-8&q=2005&sa.x=0&sa.y=0&sa=%E6%A4%9C%E7%B4%A2'] # 2005で検索
    
    rules = [Rule(LinkExtractor(allow=['http://www\.zaikei\.co\.jp/article/.+'],
                                process_value=process),
                  callback='parse_articles',
                  follow=True),
             Rule(LinkExtractor(deny=['http://www.zaikei.co.jp/(print|rss|photo|contactus|aboutus)/.+']))]

    def parse_articles(self, response):
        url = response.url
        item = ZaikeiItem()
        item['URL'] = url
        m = re.search('http://www.zaikei.co.jp/article/(.+?)/(.+?)\.html', url)
        item['ID'] = m.group(1) + '-' + m.group(2)
        item['category'] = response.xpath('//*/div[@class="title"]/p[@class="rss"]/a//text()').extract_first()
        item['title'] = re.sub('\u3000', ' ', response.xpath('//*/title/text()').extract_first())

        item['content'] = re.sub('[\n\r\u3000]', '<br>', '<br>'.join(response.xpath('//*/div[@id="article_body_weblio"]//text()').extract()))
        item['publication_datetime'] = datetime.strptime(response.xpath('//*/div[@class="option"]//p[@class="update"]//text()').extract_first(),
                                                         '%Y年%m月%d日 %H:%M')
        item['scraping_datetime'] = datetime.now()

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        return item
