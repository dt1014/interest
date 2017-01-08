#!/bin/bash

mkdir -p output
scrapy crawl reuters \
	   --logfile=output/reuters_spider.log \
	   --loglevel=INFO
