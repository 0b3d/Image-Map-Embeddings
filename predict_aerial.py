import os, sys
from random import random
import torch
import numpy as np

from data import create_dataset
from models import create_model
from options.predict_options import PredictOptions

if __name__ == '__main__':
    opt = PredictOptions().parse() 
    areas = opt.area if type(opt.area) == list else [opt.area] 
    names = opt.name if type(opt.name) == list else [opt.name]

    for name in names:
        opt.name = name

        for area in areas:
            opt.area = area
            print("predicting ... ", name, area)

            dataset = create_dataset(opt) 

            if opt.show_dataset:
                dataset.dataset.show_dataset(50, random=True) 
                sys.exit()


            model = create_model(opt)     
            model.setup(opt)             
            model.eval()                   

            coords = dataset.dataset._coords
            H,W,T,_ = coords.shape
            n = len(dataset) * opt.num_augmentations
            print("Number of samples to predict: ", n)
            
            pred = {
                'X' : np.zeros((n,opt.embedding_dim), dtype=float),
                'Y' : np.zeros((n,opt.embedding_dim), dtype=float),
                'coords': dataset.dataset._coords
            }
            
            for i, data in enumerate(dataset):
                
                model.set_input(data) 
                k1 = opt.batch_size*opt.num_augmentations
                with torch.no_grad():
                    model.forward()
                    x = model.X_o.cpu().data.numpy()
                    y = model.Y_o.cpu().data.numpy()
                    k2 = x.shape[0]
                    pred['X'][i*k1:(i*k1+k2),:] = x
                    pred['Y'][i*k1:(i*k1+k2),:] = y
                    
                if i % 10 == 0:  
                    print('{} images processed'.format(k2*i) )

            pred['X'] = pred['X'].reshape(H,W,T,-1)
            pred['Y'] = pred['Y'].reshape(H,W,T,-1)

            z = opt.tile_zoom[0] if len(opt.tile_zoom) == 1 else -1 
            
            save_filename = '%s_%s_z_%d' % (opt.epoch, opt.area, z)
            save_dir = os.path.join(opt.results_dir, opt.name)
            print('Finish, {} images processed, predictions saved in {}'.format(n,save_dir))
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            save_path = os.path.join( save_dir ,save_filename + '.npz')
            np.savez(save_path, X=pred['X'], Y=pred['Y'], coords=pred['coords'])