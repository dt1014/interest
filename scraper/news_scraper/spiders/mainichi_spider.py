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

from news_scraper.items import MainichiItem

class MainichiSpider(CrawlSpider):
    name = 'mainichi'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    
    allowed_domains = ['mainichi.jp']

    start_urls = ['https://mainichi.jp/']

    rules = [Rule(LinkExtractor(allow=['https?://mainichi.jp/articles/']),
                  callback='parse_articles',
                  follow=True),
             Rule(LinkExtractor(allow=['https?://mainichi.jp/(koshien|sportsspecial|ama-baseball|senkyo)/articles/']),
                  callback='parse_others',
                  follow=True),
             Rule(LinkExtractor(allow=['https?://mainichi.jp/premier']),
                  callback='parse_premier',
                  follow=True),
             Rule(LinkExtractor(allow=['https?://mainichi.jp/movie/video/?id=']),
                  callback='parse_movie',
                  follow=True),
             Rule(LinkExtractor(deny=['https?://mainichi.jp/(auth|help|graphs|english|info)',]),
                  callback='first',
                  follow=True)]

    def parse_articles(self, response):
        url = response.url
        item = MainichiItem()
        item['URL'] = url
        item['ID'] = re.sub('/', '-', re.search('articles/(.+c)$', url).group(1))

        title_check_xpath = ['//*/article/header/h1/text()']
        for tc_xpath in title_check_xpath:
            title_check = response.xpath(tc_xpath).extract_first()
            if title_check:
                item['title'] = title_check.replace('\u3000', ' ')
                break
            
        item['tag'] = ' '.join(response.xpath('//*/div[@class="article-info"]/ul[@class="channel-list inline-list"]/li//text()').extract())
        item['content'] = re.sub('[\n\r\u3000]', '<br>', '<br>'.join(response.xpath('//*/div[@class="main-text"]/p[@class="txt"]//text()').extract()))
        
        for date in response.xpath('//*/div[@class="article-info"]/p[@class="post"]//text()').extract():
            if re.search('[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日 [0-9]{1,2}時[0-9]{1,2}分', date):
                item['publication_datetime'] = datetime.strptime(date,
                                                                 '%Y年%m月%d日 %H時%M分')
                break
            
        item['scraping_datetime'] = datetime.now()

        try:
            item['publication_datetime']
            print()
            print('ok')
            print(url)
        except:
            print()
            print('ng')
            print(url)
            
        # try:
        #     print()
        #     print('*'*100)
        #     print(item['URL'])
        #     print(item['ID'])
        #     print(item['title'])
        #     print(item['tag'])
        #     print(item['content'])
        #     print('*'*100)
        #     #self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        # except:
        #     print()
        #     print('ERROR')
        #     print(url)
            
    def parse_premier(self, response):
        url = response.url
        item = MainichiItem()
        # print()
        # print('&'*100)
        # print(url)
        # print('&'*100)
        
    def parse_premier(self, response):
        url = response.url
        item = MainichiItem()
        # print()
        # print('='*100)
        # print(url)
        # print('='*100)

    def parse_movie(self, response):
        url = response.url
        item = MainichiItem()
        # print()
        # print('%'*100)
        # print(url)
        # print('%'*100) 
        
    def first(self, response):
        url = response.url
        item = MainichiItem()
        # print()
        # print('-'*100)
        # print(url)
        # print('-'*100)    
