#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="reuters_${run_datetime}.log"

scrapy crawl reuters \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
