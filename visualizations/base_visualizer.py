import os
import matplotlib
from abc import ABC, abstractmethod
from matplotlib import pyplot as plt
import numpy as np
import scipy.io as sio

class BaseVisualizer(ABC):
    def __init__(self, opt):
        self.opt = opt
        if self.opt.seed >= 0:
            np.random.seed(self.opt.seed)     
        
        # define source, target domains
        if opt.direction == 'map2map':
            self.source_domain, self.target_domain = 'X', 'X'
        elif opt.direction == 'image2image':
            self.source_domain, self.target_domain = 'Y', 'Y'
        elif opt.direction == 'map2image':
            self.source_domain, self.target_domain = 'X', 'Y'
        elif opt.direction == 'image2map':
            self.source_domain, self.target_domain = 'Y', 'X'
        else:
            raise NotImplementedError

    
    @abstractmethod
    def show(self):
        pass 

    @abstractmethod  
    def print_info(self):
        pass

    def get_data(self, model, area):
        data = {}
        if self.opt.format == 'npz':
            for domain in ['X', 'Y']:
                dataFilename = os.path.join( self.opt.results_dir, model, self.opt.epoch + '_predictions_' + domain +'_'+area + '_test_zoom_' + str(self.opt.tile_zoom) + '.npz')
                data[domain] = np.load(dataFilename)['predictions'].astype(np.float64) 
                try:
                    coords = np.load(dataFilename)['coords']
                except:
                    coords = None
                    #print("Warning no coords inside file")
        else:
            dataFilename = os.path.join( self.opt.results_dir, model, 'z' + str(self.opt.tile_zoom), area + '.mat')
            data = sio.loadmat(dataFilename)

        if self.opt.direction == 'map2map':
            source_features, target_features = data['X'], data['X']
        elif self.opt.direction == 'image2image':
            source_features, target_features = data['Y'], data['Y']
        elif self.opt.direction == 'map2image':
            source_features, target_features = data['X'], data['Y']
        elif self.opt.direction == 'image2map':
            source_features, target_features = data['Y'], data['X']
        else:
            raise NotImplementedError

        return source_features, target_features, coords


    def get_data_v2(self, model, area):
        data = {}

        for domain in ['X', 'Y']:
            dataFilename = os.path.join( self.opt.results_dir, model, self.opt.epoch + '_' +area + '_z_' + str(self.opt.tile_zoom) + '.npz')
            data[domain] = np.load(dataFilename)[domain]
        coords = np.load(dataFilename)['coords'] 

        if   self.opt.direction == 'map2map':
            source_features, target_features = data['X'], data['X']
        elif self.opt.direction == 'image2image':
            source_features, target_features = data['Y'], data['Y']
        elif self.opt.direction == 'map2image':
            source_features, target_features = data['X'], data['Y']
        elif self.opt.direction == 'image2map':
            source_features, target_features = data['Y'], data['X']
        else:
            raise NotImplementedError

        return source_features, target_features, coords

    def savefig(self, path):
        print("Figure saved in", path)
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(self.opt.fig_size[0]/2.54, self.opt.fig_size[1]/2.54)
        plt.savefig(path, dpi=self.opt.fig_dpi, bbox_inches = "tight")
