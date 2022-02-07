#!/bin/bash
set -ex

python ./localize.py \
    --localizer 'aerialpf' \
    --expname 'mytest' \
    --name 'aerial_model_pretrained' \
    --area "SP50NW" \
    --dataroot $DATASETS'digimap_data' \
    --results_dir $RESULTS \
    --checkpoints_dir $CHECKPOINTS \
    --model street2vec \
    --epoch 'latest' \
    --dataset_mode None \
    --seed 440 \
    --visualize \
    --trials 1 \
    --steps 500
    
    

