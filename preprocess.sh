#!/bin/bash

working_dir=makeDataSet/preprocessing
result_dir=${working_dir}/result

mkdir -p ${result_dir}

python ${working_dir}/process.py \
    --outpath ${result_dir} \
    --logpath ${result_dir}
