#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="asahi_${run_datetime}.log"

scrapy crawl asahi \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
