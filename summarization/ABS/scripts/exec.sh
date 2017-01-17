#!/bin/bash

set -eu

REUTERS_PATHS_TEMPLATE='../../../scraper/output/reuters/\*/\*/\*.csv'
DATASET_DIR='../data/dataset'
FROM_DB_DIR='../data/raw_data/from_db'
DICTIONARY_DIR='../data/dictionary'

mkdir -p ${DATASET_DIR}
mkdir -p ${DICTIONARY_DIR}

if [ -f ${DICTIONARY_DIR}/tokens.csv -a -f ${DICTIONARY_DIR}/alldata.dict -a -f ${DICTIONARY_DIR}/bow.pkl ]
then
	echo 'skip make dictionary' 
else
	python pyscripts/make_dictionary.py \
		   --reuters_paths_template ${REUTERS_PATHS_TEMPLATE} \
		   --from_db_path ${FROM_DB_DIR}/sources.pkl \
		   --save_dir ${DICTIONARY_DIR}
fi

if [ -f ${DATASET_DIR}/train.csv -a -f ${DATASET_DIR}/test.csv -a -f ${DATASET_DIR}/dictionary.pkl -a -f ${DATASET_DIR}/batch.pkl ]
then
	echo 'skip making dataset'
else
	python pyscripts/dataset.py \
		   --reuters_paths_template ${REUTERS_PATHS_TEMPLATE} \
		   --from_db_path ${FROM_DB_DIR}/sources.pkl \
		   --dictionary_dir ${DICTIONARY_DIR} \
		   --save_dir ${DATASET_DIR}  
fi


MODEL_DIR='../result/models'
mkdir -p ${MODEL_DIR}

export CUDA_VISIBLE_DEVICES='1'
python pyscripts/train_ABS.py \
	   --batch_path ${DATASET_DIR}/batch.pkl \
	   --dictionary_path ${DATASET_DIR}/dictionary.pkl \
	   --save_dir ${MODEL_DIR}

# python pyscripts/decoder_ABS.py \
# 	   --dataset_path ${REUTERS_DATASET_DIR}/test.pkl \
# 	   --model_dir ${MODEL_DIR} 
