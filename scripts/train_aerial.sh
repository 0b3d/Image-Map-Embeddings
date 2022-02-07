#!/bin/bash
set -ex

python ./train_aerial.py \
    --checkpoints_dir $CHECKPOINTS \
    --dataroot $DATASETS'digimap_data' \
    --name 'aerial_model' \
    --model 'street2vec' \
    --area 'multiarea' \
    --alpha 0.2 \
    --scale 32 \
    --dataset 'metatilestrain' \
    --N 10000 \
    --domain 'map' 'aerial' \
    --batch_size 20 \
    --rotation_noise_type 'gauss' \
    --rotation_std 0.08727 \
    --map_noise \
    --tile_size 128 \
    --pano_size 128 \
    --num_augmentations 10 \
    --drop_last \
    --flips \
    --tile_zoom 18 \
    --embedding_dim 16 \
    --n_epochs 50 \
    --n_epochs_decay 50 \
    --save_epoch_freq 25 \
    --seed 442 \
    --gpu_ids 0 

echo end time is "$(date)"



