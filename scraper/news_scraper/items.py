# -*- coding: utf-8 -*-

import scrapy

class NewsItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()
   
