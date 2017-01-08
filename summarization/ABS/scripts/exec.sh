#!/bin/bash

set -eu

REUTERS_PATHS_TEMPLATE='../../../scraper/output/reuters/\*/\*/\*.csv'
REUTERS_DATASET_PATH='../data/dataset/reuters.pkl'
mkdir -p '../data/dataset'

if [ -f ${REUTERS_DATASET_PATH} ]
then
	:
else
	python pyscripts/reuters_dataset.py \
		   --data_paths_template ${REUTERS_PATHS_TEMPLATE} \
		   --save_path ${REUTERS_DATASET_PATH}  
fi

python pyscripts/train.py \
	   --dataset_path ${REUTERS_DATASET_PATH} 
