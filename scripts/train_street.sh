#!/bin/bash
set -ex

python ./train_street.py \
    --name 'street_model' \
    --model 'street2vec' \
    --alpha 0.2 \
    --scale 32 \
    --dataset 'streetlearn' \
    --dataroot $DATASETS'streetlearn' \
    --checkpoints_dir $CHECKPOINTS \
    --num_augmentations 5 \
    --no_local_rotation \
    --batch_size 10 \
    --tile_size 128 \
    --pano_size 128 \
    --drop_last \
    --flips \
    --embedding_dim 16 \
    --n_epochs 5 \
    --n_epochs_decay 5 \
    --save_epoch_freq 2 \
    --seed 442 \
    --gpu_ids 0

echo end time is "$(date)"



