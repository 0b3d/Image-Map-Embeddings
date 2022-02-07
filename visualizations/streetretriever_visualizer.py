import numpy as np
import os

import cv2
import sklearn.metrics

from slutils.area import Area
from .base_visualizer import BaseVisualizer

from utils.metric_utils import rank

class StreetRetrieverVisualizer(BaseVisualizer):

    @staticmethod
    def modify_commandline_options(parser):
        parser.add_argument('--k', type=int, default=4, help='Number of nearest neighbours to show')
        parser.add_argument('--samples', type=int, default=10, help='Number of examples to show')
        parser.add_argument('--city', type=str, default='manhattan', help='city')
        parser.add_argument('--direction', type=str, default='image2map', help='Direction map2image|image2map|map2map|image2image')
        parser.add_argument('--locations', nargs='+', type=int, help='A list with the indixes of locations to show (based in python indexing 0:4999)')
        parser.add_argument('--version', type=str, default='v1', help='v1 shows both domains for retrieved examples (one example per page), v2 shows the quey and target domain images only (one example per row)')
        parser.add_argument('--topk', type=int, default=None, help='Retrieve examples where rank is equal to topk')
        parser.add_argument('--show_index', action='store_true', help='If set, it shows index of locations')
        
        return parser
        
    def __init__(self, opt):
        BaseVisualizer.__init__(self, opt)
        self.source_features, self.target_features, _ = super().get_data(opt.model, opt.area)
        self.loc_ids = np.arange(0,self.source_features.shape[0]) 
        self.rank_ = rank(self.source_features,self.target_features,self.loc_ids,self.loc_ids)
        self.distances = sklearn.metrics.pairwise_distances(self.source_features, self.target_features,'euclidean')
        self.sorted_distances_indices = np.argsort(self.distances, axis=1)
        self.area = Area(opt.area, opt.dataroot)

    
    def retrieve_from_street2vec_v1(self):
        """It shows an example per page including both domains. Gt at the top and retrieved examples in rows underneath"""

        if self.opt.locations is None:
            if self.opt.topk is None:
                indices = np.random.randint(0,self.source_features.shape[0],self.opt.samples) 
            else:
                indices = np.where( self.rank_ == self.opt.topk )[0]
                indices = np.random.choice(indices,self.opt.samples,False)
        else:
            indices = self.opt.locations
            indices = np.asarray(self.opt.locations)

        for lindex in indices:   
            locations = []

            queryLocation = self.area.get_location(int(lindex), zooms=[18])
            text = str(lindex) if self.opt.show_index else None
            query_img = queryLocation.get_location_with_info(size=self.opt.tile_size,text=text)
            locations.append(query_img)

            # Get k nearest neighbours
            nearest_nodes = np.take(self.loc_ids, self.sorted_distances_indices[lindex,0:self.opt.k]) # Take the k nearest indices to visualize

            for retrieved_lindex in nearest_nodes:
                retrievedLocation = self.area.get_location(int(retrieved_lindex), zooms=[18])

                colour = (0, 255, 0) if lindex == retrieved_lindex else (255, 255, 255)
                text = str(retrieved_lindex) if self.opt.show_index else None
                retrieved_img = retrievedLocation.get_location_with_info(size=self.opt.tile_size, colour=colour,text=text)
                locations.append(retrieved_img)

            image = np.concatenate(locations, 0)

            cv2.imshow('query/retrieved',image) 
            cv2.waitKey(0)
        cv2.destroyWindow('query/retrieved')

    def retrieve_from_street2vec_v2(self):
        """It shows an example per row. Gt on the left and retrieved examples on the right. Only retrieved images in the target domain are shown"""

        if self.opt.locations is None:
            if self.opt.topk is None:
                indices = np.random.randint(0,self.source_features.shape[0],self.opt.samples) 
            else:
                indices = np.where( self.rank_ == self.opt.topk )[0]
                indices = np.random.choice(indices,self.opt.samples,False)
        else:
            indices = self.opt.locations
            indices = np.asarray(self.opt.locations)

        nchuncks = max(len(indices) // 4,1)
        chuncks =  np.array_split(indices, nchuncks, axis=0)
        
        for indices in chuncks:
            examples = []
            for lindex in indices:   
                locations = []
                # Read original location
                queryLocation = self.area.get_location(int(lindex), zooms=[18])
                
                text = str(lindex) if self.opt.show_index else None
                query_snaps = queryLocation.get_snaps_with_info(size=self.opt.tile_size,text=text)
                query_img = np.concatenate(query_snaps,axis=1) 
                locations.append(query_img)

                nearest_nodes = np.take(self.loc_ids, self.sorted_distances_indices[lindex,0:self.opt.k]) # Take the k nearest indices to visualize

                for retrieved_lindex in nearest_nodes:
                    retrievedLocation = self.area.get_location(int(retrieved_lindex), zooms=[18])

                    colour = (0, 255, 0) if lindex == retrieved_lindex else (255, 255, 255)
                    text = str(retrieved_lindex) if self.opt.show_index else None
                    retrieved_img = retrievedLocation.get_tile_with_info(zoom=self.opt.tile_zoom, size=self.opt.tile_size, colour=colour, text=text)
                    locations.append(retrieved_img)

                image = np.concatenate(locations, 1)
                examples.append(image)

            image = np.concatenate(examples,axis=0)
            if self.opt.save:
                filename = '{}_{}_{}_{}_{}.{}'.format(self.opt.name, self.opt.model, self.opt.area, self.opt.tile_zoom, self.opt.seed, self.opt.fig_format)
                path = os.path.join(self.opt.results_dir, filename)
                cv2.imwrite(path, image)
            
            cv2.imshow('query/retrieved',image) 
            cv2.waitKey(0)


    def show(self):
        if self.opt.version == 'v1':
            self.retrieve_from_street2vec_v1()
        else:
            self.retrieve_from_street2vec_v2()


    def print_info(self):
        print('Source domain ', self.source_domain)
        print('Target domain ', self.target_domain)

