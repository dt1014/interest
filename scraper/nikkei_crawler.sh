#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="nikkei_${run_datetime}.log"

scrapy crawl nikkei \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
 
