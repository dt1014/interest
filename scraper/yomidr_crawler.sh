#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="yomidr_${run_datetime}.log"

scrapy crawl yomidr \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
