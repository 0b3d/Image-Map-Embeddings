#!/bin/bash
# Note: Use --tile_zoom 18 for S1 and --tile_zoom 19 for S2
set -ex

NAME='street_model_pretrained'   
MODEL='street2vec'  
EMBEDDING_DIM=16
DATASET='streetlearn' 
AREA='hudsonriver5k unionsquare5k wallstreet5k'
EPOCH=10
PROPROCESS='normalize'
TILE_ZOOM=18 

python ./predict_street.py \
    --checkpoints_dir ${CHECKPOINTS} \
    --results_dir ${RESULTS} \
    --name ${NAME} \
    --model ${MODEL} \
    --embedding_dim ${EMBEDDING_DIM} \
    --dataset ${DATASET} \
    --dataroot ${DATASETS}'streetlearn' \
    --area ${AREA} \
    --batch_size 100 \
    --preprocess ${PROPROCESS} \
    --no_rotations \
    --no_local_rotation \
    --num_augmentations 1 \
    --tile_zoom ${TILE_ZOOM} \
    --no_map_random_crop \
    --epoch ${EPOCH} \




