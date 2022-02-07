import cv2
import numpy as np
import sklearn.metrics

from aerial.tile import MetaTile
from .base_visualizer import BaseVisualizer

from utils.metric_utils import rank
from aerial.grid_utils import *

class AerialRetrieverVisualizer(BaseVisualizer):

    @staticmethod
    def modify_commandline_options(parser):
        parser.add_argument('--k', type=int, default=4, help='Number of nearest neighbours to show')
        parser.add_argument('--direction', type=str, default='image2map', help='Direction map2image|image2map|map2map|image2image')
        parser.add_argument('--location', nargs=3, type=float, default=[51.7534726,-1.2566519,18], help='query location')
        parser.add_argument('--show_index', action='store_true', help='if set will show index in query images')
        parser.add_argument('--samples', type=int, default=None, help='Number of samples to show')
        parser.add_argument('--aerial_dir', type=str, default=None, help='aerial_dir')
        return parser
        
    def __init__(self, opt):
        BaseVisualizer.__init__(self, opt)
        self.source_features, self.target_features, self.coords = super().get_data_v2(self.opt.model, self.opt.area)
        self.source_domain = 'aerial' if self.source_domain is 'Y' else 'map'
        self.target_domain = 'map' if self.target_domain is 'X' else 'aerial'


    def retrieve_neighbours(self):
        # Get coordinates
        H,W,T,_ = self.coords.shape
        y_min = self.coords[0,0,0,2]
        x_min = self.coords[0,0,0,3]

        # Query descriptor
        lat, lon, z = self.opt.location
        
        x, y = deg2num(lat, lon, z)
        x = int(x - x_min)
        y = int(y - y_min)
        gt_lat = self.coords[y,x,0,0]
        gt_lon = self.coords[y,x,0,1]
        location = (float(gt_lat),float(gt_lon),int(z))

        query_descriptor = self.source_features[int(y),int(x),0,:]
        query_image = MetaTile(location,self.opt.dataroot, self.opt.aerial_dir).get_metatile(domains=[self.source_domain])[0]
        
        
        thick = 5
        query_image = cv2.copyMakeBorder(query_image, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, (255,255,255))
        gt_image = MetaTile(location, self.opt.dataroot, self.opt.aerial_dir).get_metatile(domains=[self.target_domain])[0]
        
        # Get query descriptor and distances
        target_descriptors = self.target_features[:,:,0,:]          # Consider north aligned map tiles only
        target_shape =target_descriptors.shape[0:-1]    
        target_descriptors = target_descriptors.reshape(-1,16)
        distances = sklearn.metrics.pairwise_distances(query_descriptor.reshape(1,-1), 
                    target_descriptors, 'euclidean')
        sorted_distances_indices = np.argsort(distances, axis=1)

        ry, rx = np.unravel_index(sorted_distances_indices, target_shape)
        
        ry = ry[0:self.opt.k][0]
        rx = rx[0:self.opt.k][0]

        # get coordinates in lat, lon, theta
        lat = self.coords[ry,rx,0,0]
        lon = self.coords[ry,rx,0,1] 
        theta = self.coords[ry,rx,0,4] 
        print("Rank", rank)

        # Prepare image to show
        images = []

        for i in range(self.opt.k):
            location = (float(lat[i]),float(lon[i]),int(z))
            tile = MetaTile(location, self.opt.dataroot, self.opt.aerial_dir).get_metatile(domains=[self.target_domain],rotation=theta[i])[0]
            tile = cv2.copyMakeBorder(tile, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, (255,255,255))
            images.append(tile)

        image = np.concatenate(images, 1)
        img = np.concatenate([query_image,image],1)
        cv2.imshow("Result", img)
        cv2.waitKey(0)
        if self.opt.save:
            cv2.imwrite('temp/retrieved_aerial' + self.opt.area + '.jpg', img)
        
    def show(self):
        self.retrieve_neighbours()

    def print_info(self):
        print('Source domain ', self.source_domain)
        print('Target domain ', self.target_domain)

