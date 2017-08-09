#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="sankei_${run_datetime}.log"

scrapy crawl sankei \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
 
