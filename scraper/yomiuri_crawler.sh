#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="yomiuri_${run_datetime}.log"

scrapy crawl yomiuri \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
