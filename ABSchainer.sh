#!/bin/bash

working_dir=chainer/ABS
training_dir=${working_dir}/training
data_dir=data/
dataset_dir=${working_dir}/dataset

for option in "$@"
do
    case "${option}" in
	"-s"|"--small" )
	    datalabel="_small"
	    shift 1
    esac
done

function getDataset() {

	inpath=${data_dir}/result/all/makeDictionary${datalabel}/
	outdir=${dataset_dir}/result/${config_name}${datalabel}
	mkdir -p ${outdir}
	if [ ! -e ${outdir}/train.pkl ];then

		echo "***dataset.py***"
		python -W ignore ${dataset_dir}/src/dataset.py \
			   --inpath ${inpath} \
			   --outdir ${outdir} \
			   --config "${config}"
	fi
}


dataset_config_path="${dataset_dir}/config.json"
dataset_config=`cat ${dataset_config_path}`
length=`echo ${dataset_config} | jq length`

for i in $( seq 1 ${length} )
do
	config_name=dataset${i}
	config=`echo ${dataset_config} | jq -r .${config_name}`
	getDataset
done
