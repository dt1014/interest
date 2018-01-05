#!/bin/bash

working_dir=chainer/ABS
src_dir=${working_dir}/src
result_dir=${working_dir}/result
config_dir=${working_dir}/config
data_dir=data/
dataset_dir=${working_dir}/dataset

datalabel=""
command="${1}"
shift 1

for option in "$@"
do
    case "${option}" in
	"-s"|"--small" )
	    datalabel="_small"
	    shift 1
		;;
	"-c"|"--check" )
	    datalabel="_check"
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
	echo "------------------------------------------------"
	echo "dataset :   ${dataset_config_name}${datalabel}"
	echo "nn_opt  :   ${nn_opt}"
	echo "------------------------------------------------"
	
	indir=${dataset_dir}/result/${dataset_config_name}${datalabel}
	trainpath=${indir}/train.pkl
	valpath=${indir}/val.pkl
	dicpath=${indir}/dictionary.pkl
	outdir=${result_dir}/${dataset_config_name}${datalabel}/${nn_opt}
	mkdir -p ${outdir}

	tempdir=${indir}/temp
	mkdir -p ${tempdir}
	
	lastepoch=`echo ${opt_config} | jq -r .epoch`
	
	if [ ! -e ${outdir}/model${lastepoch} ];then
	
		python ${src_dir}/train.py \
			   --trainpath ${trainpath} \
			   --valpath ${valpath} \
			   --tempdir ${tempdir} \
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
			done
		done
	done
}

function test_() {
	echo "------------------------------------------------"
	echo "dataset :   ${dataset_config_name}${datalabel}"
	echo "nn_opt  :   ${nn_opt}"
	echo "------------------------------------------------"
	
	indir=${dataset_dir}/result/${dataset_config_name}${datalabel}
	trainpath=${indir}/train.pkl
	valpath=${indir}/val.pkl
	testpath=${indir}/test.pkl
	dicpath=${indir}/dictionary.pkl
	outdir=${result_dir}/${dataset_config_name}${datalabel}/${nn_opt}
	modelpath=${result_dir}/${dataset_config_name}${datalabel}/${nn_opt}/model{epoch}
	mkdir -p ${outdir}

	tempdir=${indir}/temp
	mkdir -p ${tempdir}
	
	lastepoch=`echo ${opt_config} | jq -r .epoch`
	
	if [ ! -e ${outdir}/model${lastepoch} ];then
	
		python -W ignore ${src_dir}/test.py \
			   --trainpath ${trainpath} \
			   --valpath ${valpath} \
			   --testpath ${testpath} \
			   --tempdir ${tempdir} \
			   --dicpath ${dicpath} \
			   --modelpath ${modelpath} \
			   --outdir ${outdir} \
			   --dataset_config "${dataset_config}" \
			   --nn_config "${nn_config}" \
			   --opt_config "${opt_config}"
	fi
}

function schedule_test() {

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
				
				test_
			done
		done
	done
}

function decode() {

	indir=${dataset_dir}/result/${dataset_config_name}${datalabel}
	trainpath=${indir}/df_id_train.pkl
	valpath=${indir}/df_id_val.pkl
	testpath=${indir}/df_id_test.pkl
	dicpath=${indir}/dictionary.pkl
	modelpath=${result_dir}/${dataset_config_name}${datalabel}/${nn_opt}/model${epoch}

	outpath=${result_dir}/${dataset_config_name}${datalabel}/${nn_opt}/decode.csv
	
	dataset_config=`echo ${dataset_config_json} | jq -r .${dataset_config_name}`
	nn_config=`echo ${nn_config_json} | jq -r .nn${nn_num}`
	opt_config=`echo ${opt_config_json} | jq -r .opt${opt_num}`
	
	#if [ -e ${modelpath} ];then
	if true; then
		python -W ignore ${src_dir}/decode.py \
			   --trainpath ${trainpath} \
			   --valpath ${valpath} \
			   --testpath ${testpath} \
			   --dicpath ${dicpath} \
			   --modelpath ${modelpath} \
			   --outpath ${outpath} \
			   --dataset_config "${dataset_config}" \
			   --nn_config "${nn_config}" \
			   --opt_config "${opt_config}"
	fi
		
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

if [ "${command}" = "train" ]; then
	schedule_train
	
elif [ "${command}" = "test" ]; then
	schedule_test
	
elif [ "${command}" = "decode" ]; then
	read -p "dataset number: " dataset_num
	read -p "nn number: " nn_num
	read -p "opt number: " opt_num
	read -p "epoch: " epoch
	dataset_config_name=dataset${dataset_num}
	nn_opt=nn${nn_num}opt${opt_num}
	decode
fi
