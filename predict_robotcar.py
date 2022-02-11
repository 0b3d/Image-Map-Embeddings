"""Predict features in the oxfordrobotcar dataset (4-view images only).

Example (You need to train models first or download pre-trained models from our website):
        Predict embedded descriptors for X domain:
        
        python predict_robotcar.py --name v2_12 -d robotcarframes --chunk 1 
        --frames_dir processed_chunk1 –traversal 2015-10-29-10-55-43 -m pano 
        --embedding_dim 16 --no_vlad --batch_size 10 --pano_size 128 --epoch 10  --area oxford

"""
import os
from options.predict_options import PredictOptions
from data import create_dataset
from models import create_model
import torch
import numpy as np
import scipy.io as sio


if __name__ == '__main__':
    opt = PredictOptions().parse()  # get test options

    # hard-code some parameters for test
    opt.num_threads = 0            # test code only supports num_threads = 1
    opt.num_augmentations = 1      # only one image per location
    opt.serial_batches = True      # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True             # no flip; comment this line if results on flipped images are needed.
    opt.no_rotation = True         # No rotation in the testing images
    opt.preprocess = 'none'
    opt.display_id = -1            # no visdom display; the test code saves the results to a HTML file.
    opt.panorama_mode = 'list'
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    model.eval()                   # evaluation mode
    
    n = len(dataset)
    print("Number of samples to predict: ", n)
    
    predictions = np.zeros((n,opt.embedding_dim), dtype=float)
    
    for i, data in enumerate(dataset):
        model.set_input(data)  # unpack data from data loader
        
        with torch.no_grad():
            model.forward()
            out = model.Y_o.cpu().data.numpy()
            k = out.shape[0]
            predictions[i*opt.batch_size:(i*opt.batch_size+k),:] = out
        
        if i % 10 == 0:  # save images to an HTML file
            print('{} images processed'.format(k*i) )

    domain = 'Y'
    save_filename = 'robotcar_%s_%s_z%d' % (opt.traversal, opt.area, opt.tile_zoom)
    save_dir = os.path.join(opt.results_dir, opt.name)
    print('Finish, {} images from domain {} processed, predictions saved in {}'.format(n,domain,save_dir))
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join( save_dir ,save_filename + '.npz')
    np.savez(save_path, predictions=predictions)
    save_path = os.path.join( save_dir,  save_filename + '.mat')
    sio.savemat(save_path, {'predictions':predictions})
