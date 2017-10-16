#!/bin/bash

working_dir=dataset
src_dir=${working_dir}/src
result_dir=${working_dir}/result
log_dir=${working_dir}/log
target_list=${src_dir}/target_list.txt

mkdir -p ${log_dir}

function processCommonFromDB() {
    
    mkdir -p ${result_dir}/${target}
   
    logpath=${log_dir}/${target}.log
    if [ -f ${logpath} ]
    then
		rm ${logpath}
    fi

    python ${src_dir}/processCommonFromDB.py \
		   --outpath ${result_dir}/${target}/common_procesed.pkl \
		   --logpath ${logpath} \
		   --target ${target}
}

function pipe() {
    processCommonFromDB ${target}  
}

for option in "$@"
do
    case "${option}" in
	"-t"|"--target" )
	    target="${2}"
	    shift 2
    esac
done

if [ -z "${target}" ]
then
    for target in `cat ${target_list}`
    do
	pipe ${target}
    done
else
    pipe ${target}
fi

