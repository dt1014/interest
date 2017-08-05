#!/bin/bash

mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="itmedia_${run_datetime}.log"

scrapy crawl itmedia \
	   --logfile=log/${logfile_name} \
	   --loglevel=INFO
