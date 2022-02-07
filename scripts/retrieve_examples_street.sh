#!/bin/bash
set -ex

NAME='street_model_pretrained'
AREA='hudsonriver5k' 
EPOCH='10'

python ./visualizer.py \
    --vname 'streetretriever' \
    --results_dir ${RESULTS} \
    --dataroot $DATASETS'streetlearn' \
    --model ${NAME} \
    --area ${AREA} \
    --epoch ${EPOCH} \
    --version v1 \
    --seed -1

