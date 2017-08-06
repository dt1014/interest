#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="gigazine_${run_datetime}.log"

scrapy crawl gigazine \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
 
