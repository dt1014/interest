# -*- coding: utf-8 -*-


import os
from datetime import datetime
from scrapy import signals
from scrapy.exporters import CsvItemExporter, XmlItemExporter

colnames = ['URL', 'ID', 'category', 'publication_datetime', 'scraping_datetime', 'title', 'content']

class ReutersScraperPipeline(object):
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
        
        
