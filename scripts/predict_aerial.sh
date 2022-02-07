#!/bin/bash
set -ex

NAME='aerial_model_pretrained'    
MODEL='street2vec'  
AREA='London_test'

python ./predict_aerial.py \
    --checkpoints_dir ${CHECKPOINTS} \
    --results_dir ${RESULTS} \
    --dataroot ${DATASETS}'digimap_data' \
    --name ${NAME} \
    --model ${MODEL} \
    --embedding_dim 16 \
    --dataset 'metatilespredict' \
    --area ${AREA} \
    --batch_size 100 \
    --epoch 'latest' \
    --num_augmentations 1 \
    --tile_zoom 18 \
    --scale 32 \
    --T 8 \
    --tile_size 128 \
    --pano_size 128 \
    --domain 'map' 'aerial' 







