# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta
from itertools import takewhile
import logging
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import mojimoji

from news_scraper.items import JijiItem

class JijiSpider(CrawlSpider):
    name = 'jiji'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5, ################################################
        'ROBOTSTXT_OBEY': False
    }
    
    allowed_domains = ['www.jiji.com']
    
    start_urls = ['https://www.jiji.com/',
                  'https://www.jiji.com/jc/c?g=spo',
                  'https://www.jiji.com/jc/v',
                  'https://www.jiji.com/jc/c?g=ent',
                  'https://www.jiji.com/jc/list?g=jfn',
                  'https://www.jiji.com/jc/f2',
                  'https://www.jiji.com/jc/list?g=afp',
                  'https://www.jiji.com/jc/c?g=int',
                  'https://www.jiji.com/jc/list?g=bnw',
                  'https://www.jiji.com/jc/movie',
                  'https://www.jiji.com/jc/c?g=soc',
                  'https://www.jiji.com/jc/market',
                  'https://www.jiji.com/jc/daily',
                  'https://www.jiji.com/jc/p']

    # # start_urls = ['https://www.jiji.com/jc/p',
    # #               'https://www.jiji.com/jc/p?id=20170808112310-0024679905']
    # # start_urls = ['https://www.jiji.com/jc/movie',
    # #               'https://www.jiji.com/jc/movie?p=mov891-movie03']
    # start_urls = ['https://www.jiji.com/jc/tsn?&p=20170807-photo1']
    # # start_urls = ['https://www.jiji.com/jc/pga',
    # #               'https://www.jiji.com/jc/pga?g=spo&k=0000000008068']
    # start_urls = ['https://www.jiji.com/jc/market',
    #              'https://www.jiji.com/jc/market?g=stock']
    # start_urls = ['https://www.jiji.com/jc/daily',
    #               'https://www.jiji.com/jc/daily?d=0801']
    # allowed_domains = ['www.jiji.com'] #####################

    
    rules = [Rule(LinkExtractor(deny=[r'https://www\.jiji\.com/(service|c_profile|jinji|topseminar|hall).*$',
                                      r'https://www\.jiji\.com/jc/(v|v[0-9]|d[0-9]|f[0-9]|e|ak|v4|ad|graphics|books|f_mode|calendar|forecast|m_stock|giin|travel|car|score|rio2016).*$']),
                  callback='parse_articles',
                  follow=True)]
    
    def parse_articles(self, response):
        
        url = response.url
        item = JijiItem()
        item['URL'] = url
        item['scraping_datetime'] = datetime.now()
        if re.search('.*=pv$', url):
            pass
        
        elif '/article?' in url or '/pga?' in url:
            if not '/pga?' in url:
                item['ID'] = ''
            else:
                item['ID'] = 'pga-'
            try:
                item['category'] = re.search('g=(.+)&', url).group(1)
                item['ID'] += item['category'] + re.search('k=(.+)$', url).group(1)
            except AttributeError:
                item['category'] = re.search('g=(.+)$', url).group(1)
                item['ID'] += item['category'] + re.search('k=(.+)&', url).group(1)
            
            # wall street journal or 
            if item['category'] == 'ws' or item['category'] == 'tha':
                item['title'] = ''
                item['content'] = ''

            elif '/article?' in url:
                item['title'] = response.xpath('//*/div[@class="ArticleTitle"]/h1/text()').extract()[0]
                item['content'] = re.sub('[\n\t\r\u3000]', '<br>', ''.join([x for x in \
                                                                            response.xpath('//*/div[@class="ArticleText clearfix"]/p/text()').extract()]))
                
            elif '/pga?' in url:
                item['title'] = response.xpath('//*/div[@class="ArticleTitle"]/h1/text()').extract()[0]
                item['content'] = re.sub('[\n\t\r\u3000]', '<br>', ''.join([x for x in \
                                                                            response.xpath('//*/div[@id="pga_article"]/p/text()').extract()]))

            try:
                pd = json.loads(response.xpath('//*/script[@type="application/ld+json"]/text()').extract()[0])['datePublished']
                item['publication_datetime'] = datetime.strptime(re.search('^\d{4}-\d{2}-\d{2}', pd).group(0) \
                                                                 + ' ' \
                                                                 + re.search('T(.+)\+', pd).group(1),
                                                                 '%Y-%m-%d %H:%M:%S')
            except IndexError:
                item['publication_datetime'] = datetime(1, 1, 1) # I dont know
             
            print()
            print('*********************************************************************')
            print('url     : ', url)
            print('id      : ', item['ID'])
            print('category: ', item['category'])
            print('title   : ', item['title'])
            print(item['content'])
            print(item['publication_datetime'])
            print('*********************************************************************')
            
        elif '/p?' in url or '/pm?' in url:
            if re.search('(list|about)$', url):
                pass
            else:
                item['ID'] = 'p-pm' + re.search('(p|pm)\?id=(.+)$', url).group(2)
                item['category'] = 'p-pm'
                item['title'] = response.xpath('//*/div[@class="ArticleTitle"]/h1/text()').extract()[0]
                item['content'] = response.xpath('//*/div[@class="MainPhotoText"]/h2/text()').extract()
                if len(item['content']) == 0:
                    item['content'] = response.xpath('//*/div[@class="MainPhotoText"]/p/text()').extract()
                item['content'] = item['content'][0]
                try:
                    pd = json.loads(response.xpath('//*/script[@type="application/ld+json"]/text()').extract()[0])['datePublished']
                    item['publication_datetime'] = datetime.strptime(re.search('^\d{4}-\d{2}-\d{2}', pd).group(0) \
                                                                     + ' ' \
                                                                     + re.search('T(.+)\+', pd).group(1),
                                                                     '%Y-%m-%d %H:%M:%S')
                except IndexError:
                    item['publication_datetime'] = datetime(1, 1, 1) # I dont know
                    
                print()
                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                print(url)
                print(item['ID'])
                print(item['category'])
                print(item['title'])
                print(item['content'])
                print(item['publication_datetime'])
                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

        elif '/movie?' in url:
            if re.search('(list|about)$', url):
                pass
            else:
                item['ID'] = re.search('movie\?p=(.+)$', url).group(1)
                item['category'] = 'movie'
                item['title'] = response.xpath('//*/div[@class="ArticleTitle"]/h1/text()').extract()[0]
                item['content'] = re.sub('[\n\t\r\u3000]', '<br>', ''.join([x for x in \
                                                                            response.xpath('//*/div[@class="ArticleText MovieDateArticleText clearfix"]/p/text()').extract()]))
                pd = json.loads(response.xpath('//*/script[@type="application/ld+json"]/text()').extract()[0])['datePublished']
                item['publication_datetime'] = datetime.strptime(re.search('^\d{4}-\d{2}-\d{2}', pd).group(0) \
                                                                 + ' ' \
                                                                 + re.search('T(.+)\+', pd).group(1),
                                                                 '%Y-%m-%d %H:%M:%S')
                
                print()
                print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                print(url)
                print(item['ID'])
                print(item['category'])
                print(item['title'])
                print(item['content'])
                print(item['publication_datetime'])
                print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')

            
        elif '/tsn?' in url:
            if re.search('(list|about)$', url):
                pass
            else:
                item['ID'] = 'tsn' + re.search('tsn\?&?p=(.+)$', url).group(1)
                item['category'] = 'tsn'
                item['title'] = response.xpath('//*/strong[@class="spo_prm-cap-title"]//text()').extract()[0]
                item['content'] = re.sub('[\n\t\r\u3000]', '<br>', ''.join([x for x in \
                                                                            response.xpath('//*/div[@id="spo_picture-area"]/p/text()').extract()]))
                item['publication_datetime'] = re.search('(\d{4}年\d{1,2}月\d{1,2}日)', 
                                                         response.xpath('//*/div[@id="wrapper_premium-photo"]/h1/text()').extract()[0]).group(0)
                item['publication_datetime'] = datetime.strptime(item['publication_datetime'],
                                                                 '%Y年%m月%d日')
                
                print()
                print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                print(url)
                print(item['ID'])
                print(item['category'])
                print(item['title'])
                print(item['content'])
                print(item['publication_datetime'])
                print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            
        elif '/market?' in url:
            
            match = re.search('p=(tyo|nyc|ldn)', url)
            if match:
                try:
                    item['category'] = re.search('g=(.+)&', url).group(1)
                except AttributeError:
                    item['category'] = re.search('g=(.+)$', url).group(1)

                item['ID'] = item['category'] + '-' + match.group(1)
                item['title'] = response.xpath('//*/div[@class="MarketArticleText"]/h2/text()').extract()[0]
                item['content'] = '<br>'.join([x.replace('\u3000', ' ') for x in \
                                               response.xpath('//*/div[@class="MarketArticleText"]/p/text()').extract()])
                pd = re.sub('(年|月|日\s|:)', '-', re.search('\((.+)\)$', item['content']).group(1))
                item['ID'] += '-' + pd
                item['publication_datetime'] = datetime.strptime(pd,
                                                                 '%Y-%m-%d-%H-%M')

                print()
                print('#####################################################################')
                print('url     : ', url)
                print('id      : ', item['ID'])
                print('category: ', item['category'])
                print('title   : ', item['title'])
                print(item['content'])
                print(item['publication_datetime'])
                print('#####################################################################')
                
            else:
                pass

        elif '/daily?' in url:
            if '?d' in url:
                today = re.search('\?d=(\d{4})', url).group(1)
                if item['scraping_datetime'] < datetime(datetime.now().year, int(today[:2]), int(today[2:])):
                    year = item['scraping_datetime'].year - 1
                else:
                    year = item['scraping_datetime'].year
                item['publication_datetime'] = datetime(year, int(today[:2]), int(today[2:]))
                item['category'] = 'whattoday'
                item['ID'] = item['category'] + '-' + str(year) + today[:2] + today[2:]
                item['title'] = response.xpath('//*/div[@class="ArticleText TodayDateArticleText clearfix"]/h2/text()').extract()[0]
                item['content'] = re.sub('[\n\t\r\u3000]', '<br>', ''.join([x for x in \
                                                                            response.xpath('//*/div[@class="ArticleText TodayDateArticleText clearfix"]/p/text()').extract()]))
                
                print()
                print('?????????????????????????????????????????????????????????????????????')
                print('url     : ', url)
                print('id      : ', item['ID'])
                print('category: ', item['category'])
                print('title   : ', item['title'])
                print(item['content'])
                print(item['publication_datetime'])
                print('?????????????????????????????????????????????????????????????????????')
                
            else:
                pass
            
        else:
            pass

        self.logger.info('scraped from <%s> published in %s' % (item['URL'], item['publication_datetime']))
        
        return item
    
    def parse_second(self, response):
        print(response.url)
        return JijiItem()
