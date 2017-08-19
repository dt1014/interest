#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="bloomberg_${run_datetime}.log"

scrapy crawl bloomberg \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
 
