#!/bin/bash

working_dir=chainer/ABS
src_dir=${working_dir}/src
result_dir=${working_dir}/result
config_dir=${working_dir}/config
data_dir=data/
dataset_dir=${working_dir}/dataset

datalabel=""

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
	outdir=${dataset_dir}/result/${dataset_config_name}${datalabel}
	mkdir -p ${outdir}
	if [ ! -e ${outdir}/train.pkl -o ! -e ${outdir}/val.pkl -o ! -e ${outdir}/test.pkl ];then

		echo "***dataset.py***"
		python -W ignore ${dataset_dir}/src/dataset.py \
			   --inpath ${inpath} \
			   --outdir ${outdir} \
			   --config "${dataset_config}"
	fi
}

function schedule_getDataset() {

	for i in $( seq 1 ${dataset_length} )
	do
		dataset_config_name=dataset${i}
		dataset_config=`echo ${dataset_config_json} | jq -r .${dataset_config_name}`
		getDataset
	done

}

function train() {

	indir=${dataset_dir}/result/${dataset_config_name}${datalabel}
	trainpath=${indir}/train.pkl
	valpath=${indir}/val.pkl
	dicpath=${indir}/dictionary.pkl
	outdir=${result_dir}/${dataset_config_name}${datalabel}/${nn_opt}
	mkdir -p ${outdir}

	lastepoch=`echo ${opt_config} | jq -r .epoch`
	
	if [ ! -e ${outdir}/model${lastepoch} ];then
	
		python ${src_dir}/train.py \
			   --trainpath ${trainpath} \
			   --valpath ${valpath} \
			   --dicpath ${dicpath} \
			   --outdir ${outdir} \
			   --dataset_config "${dataset_config}" \
			   --nn_config "${nn_config}" \
			   --opt_config "${opt_config}"
	fi
}

function schedule_train() {

	for i in $( seq 1 ${dataset_length} )
	do
		dataset_config_name=dataset${i}
		dataset_config=`echo ${dataset_config_json} | jq -r .${dataset_config_name}`
		
		for i in $( seq 1 ${nn_length} )
		do
			for j in $( seq 1 ${opt_length} )
			do
				nn_opt=nn${i}opt${j}
				nn_config=`echo ${nn_config_json} | jq -r .nn${i}`
				opt_config=`echo ${opt_config_json} | jq -r .opt${j}`
				
				train
				exit

			done
		done
	done
}


dataset_config_path="${dataset_dir}/config.json"
dataset_config_json=`cat ${dataset_config_path}`
dataset_length=`echo ${dataset_config_json} | jq length`
nn_config_path="${config_dir}/nn.json"
nn_config_json=`cat ${nn_config_path}`
nn_length=`echo ${nn_config_json} | jq length`
opt_config_path="${config_dir}/opt.json"
opt_config_json=`cat ${opt_config_path}`
opt_length=`echo ${opt_config_json} | jq length`
	
schedule_getDataset
schedule_train
