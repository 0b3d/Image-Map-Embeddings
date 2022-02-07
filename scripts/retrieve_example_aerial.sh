#!/bin/bash
set -ex

NAME='aerial_model_pretrained'
AREA='London_test' 
EPOCH='latest'

python ./visualizer.py \
    --vname 'aerialretriever' \
    --results_dir ${RESULTS} \
    --dataroot $DATASETS'digimap_data' \
    --model ${NAME} \
    --area ${AREA} \
    --epoch ${EPOCH} \
    --location '51.5067780' '-0.1034980' '18'

