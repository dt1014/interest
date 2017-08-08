#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="jiji_${run_datetime}.log"

#SCRAPY_SETTINGS_MODULE="news_scraper.settings_robotstxt_notobey"

scrapy crawl jiji \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
