"""Predict features in streeatlearn dataset and openstreetmap (pano-map pair).

It will load a saved model from --checkpoints_dir and save the results to --results_dir.

"""
import os
import torch
import numpy as np
import scipy.io as sio
from options.predict_options import PredictOptions
from data import create_dataset
from models import create_model

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
            model = create_model(opt)      
            model.setup(opt)               
            model.eval()                   
            
            n = len(dataset) * opt.num_augmentations
            print("Number of samples to predict: ", n)
            
            
            pred = {
                'X' : np.zeros((n,opt.embedding_dim), dtype=np.float32),
                'Y' : np.zeros((n,opt.embedding_dim), dtype=np.float32),
            }
            
            count = 0
            for i, data in enumerate(dataset):
                model.set_input(data) 
                k1 = opt.batch_size*opt.num_augmentations
                with torch.no_grad():
                    model.forward()
                    x = model.X_o.cpu().data.numpy()
                    y = model.Y_o.cpu().data.numpy()
                    assert (x.dtype == np.float32) and (x.dtype == np.float32), "Data is not np.float32"
                    k2 = x.shape[0]
                    pred['X'][i*k1:(i*k1+k2),:] = x
                    pred['Y'][i*k1:(i*k1+k2),:] = y
                    count += k2
                    
                #if count % 1 == 0:
                print('{} images processed'.format(count), end='\r')

            for domain in ['X','Y']:
                save_filename = '%s_predictions_%s_%s_test_zoom_%d' % (opt.epoch, domain, opt.area, opt.tile_zoom)
                save_dir = os.path.join(opt.results_dir, opt.name)
                print('Finish, {} images from domain {} processed, predictions saved in {}'.format(n,domain,save_dir))
                if not os.path.isdir(save_dir):
                    os.makedirs(save_dir)
                predictions = pred[domain]
                save_path = os.path.join( save_dir ,save_filename + '.npz')
                np.savez(save_path, predictions=predictions)
            
            save_path = os.path.join( save_dir,  opt.area + '.mat')
            sio.savemat(save_path, pred)