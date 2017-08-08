# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime
import logging

from scrapy import signals
from scrapy.exporters import CsvItemExporter, XmlItemExporter
from scrapy.exceptions import DropItem

my_dir = os.path.dirname(os.path.abspath(__file__))
db_dir_name = os.path.normpath(os.path.join(my_dir, '../../'))
sys.path.append(db_dir_name)
from postgre_db import operation, tables

class ForDebugPipeline(object):

    def __init__(self):
        self.counter = 0
    
    def process_item(self, item, spider):
        pass
        # if len(item['title']) == 0:
        #     self.logger.info('save this item to postgres: <%s>'%item['URL'])
        #     raise DropItem('drop item')
        # print('*'*100)
        # for key, val in item.items():
        #     if 'datetime' in key:
        #         val = val.strftime('%Y-%m-%d %H:%M:%S')
            
        #     if key is not 'content' and key is not 'introduction':                
        #         print('%-20s: '%key, val)
                
        # if 'introduction' in item.keys():
        #     print(item['introduction'])
        #     print()
        # print(re.sub('(<br>){2,}', '<br>', re.sub('\n', '<br>', item['content'])))

class ToPostgreSQLPipeline(object):
    def __init__(self, postgres_host, postgres_db):
        self.postgres_host = postgres_host
        self.postgres_db = postgres_db

        self.name_table_dic = {'reuters': tables.ReutersArticle,
                               'bbc': tables.BBCArticle,
                               'itmedia': tables.ITMediaArticle,
                               'gigazine': tables.GigazineArticle,
                               'jiji': tables.JijiArticle}
        
        self.logger = logging.getLogger(name='pipeline')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            postgres_host=crawler.settings.get('POSTGRES_HOSTNAME'),
            postgres_db=crawler.settings.get('POSTGRES_DATABASE')
        )
    
    def open_spider(self, spider):
        postgres_url = 'postgres://%s/%s'%(self.postgres_host, self.postgres_db)
        self.session_maker = operation.get_session_maker(postgres_url)
        
    def close_spider(self, spider):
        self.session.close()
        
    def process_item(self, item, spider):
        if len(item['title']) == 0:
            raise DropItem()
        
        self.add_item(item, spider , self.name_table_dic[spider.name])


    def add_item(self, item, spider, articleClass):
        
        item['content'] = re.sub('(<br>){2,}', '<br>', re.sub('\n', '<br>', item['content']))

        with operation.session_scope(self.session_maker) as session:
            table = articleClass
            exist = session.query(table).filter_by(ID=item['ID']).first()

            if not exist:
                print('*'*100)
                for key, val in item.items():
                    if key is not 'content' and key is not 'introduction':
                        print('%-20s: '%key, val)
        
                article = articleClass(**item)
                session.add(article)
                self.logger.info('save this item to postgres: <%s>'%item['URL'])
            else:
                self.logger.info('skip saving this item: <%s>'%item['URL'])

                
class ToFileBasePipeline(object):
    '''
    not 汎用
    '''
    def __init__(self):
        self.filepath = ''
        self.exporters = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider, filepath=None):
        colnames = ['URL', 'ID', 'category', 'publication_datetime', 'scraping_datetime', 'title', 'content']
        if not filepath:
            return 
        self.filepath = filepath
        if not os.path.exists(self.filepath.rsplit('/', 1)[0]):
            os.makedirs(self.filepath.rsplit('/', 1)[0])
        f_out = open(self.filepath, 'w+b')
        exporter = CsvItemExporter(f_out, fields_to_export=colnames)
        exporter.start_exporting()
        self.exporters[self.filepath] = exporter

    def spider_closed(self, spider):
        for exporter in self.exporters.values(): 
            exporter.finish_exporting()

    def process_item(self, item, spider):

        category = item['category'].replace(' ', '_')
        
        date = datetime.strptime(item['publication_datetime'], '%Y年 %m月 %d日 %H:%M JST').date()
        self.current_filepath = 'output/%s/%s/year=%d/reuters_%d%d.csv' % (spider.__class__.name,
                                                                           category,
                                                                           date.year,
                                                                           date.year,
                                                                           date.month)

        if self.filepath != self.current_filepath and not self.exporters.get(self.current_filepath):
            self.spider_opened(spider, self.current_filepath)
            
        self.exporters[self.current_filepath].export_item(item)
            
        return item

