#!/bin/bash
set -ex

NAME='aerial_model_pretrained'
AREA='London_test SP50NW ST57SE2014 ST57SE2016 ST57SE2017' 
EPOCH='latest'

python ./visualizer.py \
    --vname 'aerialrecall' \
    --results_dir ${RESULTS} \
    --model ${NAME} \
    --area ${AREA} \
    --epoch ${EPOCH} \
    --legend 'London' 'Oxford' 'Bristol 14' 'Bristol 16' 'Bristol 17' \
    --title 'Recall'

