#!/bin/bash
# Note: Use --tile_zoom 18 for S1 and --tile_zoom 19 for S2
set -ex

NAME='street_model_pretrained'
AREA='hudsonriver5k unionsquare5k wallstreet5k' 
EPOCH='10'

python ./visualizer.py \
    --vname 'streetrecall' \
    --results_dir ${RESULTS} \
    --model ${NAME} \
    --area ${AREA} \
    --epoch ${EPOCH} \
    --direction image2map \
    --tile_zoom 18 \
    --legend 'HR' 'US' 'WS' \
    --title 'Recall'


