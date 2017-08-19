# -*- coding: utf-8 -*-

import scrapy

class ReutersItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()
   
class BBCItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    title = scrapy.Field()
    introduction = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()
   
class ITMediaItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    page_count = scrapy.Field()
    title = scrapy.Field()
    introduction = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class GigazineItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    tag = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class JijiItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    introduction = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class SankeiItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    page_count = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()
    
class AsahiItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    tag = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    member = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()
    
class YomiuriItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class YomidrItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class MainichiItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    tag = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class BloombergItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()
    
class NikkeiItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

class AFPItem(scrapy.Item):
    URL = scrapy.Field()
    ID = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publication_datetime = scrapy.Field()
    scraping_datetime = scrapy.Field()

