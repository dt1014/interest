#!/bin/bash

working_dir=data
src_dir=${working_dir}/src
result_dir=${working_dir}/result
log_dir=${working_dir}/log
target_list=${src_dir}/target_list.txt

mkdir -p ${log_dir}

function processCommonFromDB() {
    
    mkdir -p ${result_dir}/${target}
   
    logpath=${log_dir}/${target}.log

	outpath=${result_dir}/${target}/common_procesed.pkl
	
	if [ ! -e ${outpath} ];then
		
		if [ -f ${logpath} ]
		then
			rm ${logpath}
		fi
		echo "***processCommonFromDB.py***"
		python ${src_dir}/processCommonFromDB.py \
			   --outpath ${outpath} \
			   --logpath ${logpath} \
			   --target ${target}
	fi
}

function getTarget() {

	outdir=${result_dir}/all/getTarget${datalabel}
	mkdir -p ${outdir}
	outpath=${outdir}/title_target.pkl
	
	if [ ! -e ${outpath} ];then

		echo "***getTarget.py***"
		
		if [ -z "${datalabel}" ];then
			python ${src_dir}/getTarget.py \
				   --outpath ${outpath} 
		else
			python ${src_dir}/getTarget.py \
				   --outpath ${outpath} \
				   --small
		fi

	fi
}

function makeDictionary() {

	inpath=${result_dir}/all/getTarget${datalabel}/title_target.pkl
	outdir=${result_dir}/all/makeDictionary${datalabel}
	mkdir -p ${outdir}
	if [ ! -e ${outdir}/df_id.pkl ];then

		echo "***makeDictionary.py***"
		python -W ignore ${src_dir}/makeDictionary.py \
			   --inpath ${inpath} \
			   --outdir ${outdir}
	fi
}

datalabel=""

for option in "$@"
do
    case "${option}" in
	"-t"|"--target" )
	    target="${2}"
	    shift 2
		;;
	"-s"|"--small" )
	    datalabel="_small"
	    shift 1
    esac
done

if [ -z "${target}" ]
then
    for target in `cat ${target_list}`
    do
		processCommonFromDB ${target}
    done
else
    processCommonFromDB ${target}
fi

getTarget

makeDictionary


