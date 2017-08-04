#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="bbc_${run_datetime}.log"

scrapy crawl bbc \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
 
