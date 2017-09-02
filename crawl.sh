#!/bin/bash

target=${1}
shift 1
loglevel="INFO"

for option in "$@"
do
	case "${option}" in
		"-l"|"--loglevel" )
			loglevel="${2}"
			shift 2
	esac
done

if [ -z "${target}" ]
then
	echo "define target"
	exit 1
fi

cd scraper
mkdir -p log

run_datetime=`date '+%y%m%d-%H%M'`
logfile_name="${target}_${run_datetime}.log"

scrapy crawl ${target} \
	   --logfile="log/"${logfile_name} \
	   --loglevel=${loglevel}

ret=$?

if [ $ret -eq 0 ]
then
	:
else
	rm "log/"${logfile_name}
fi

cd ..
