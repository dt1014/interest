#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="afp_${run_datetime}.log"

scrapy crawl afp \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
 
