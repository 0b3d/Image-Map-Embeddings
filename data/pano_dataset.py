import os
import numpy as np
import torch
import random

import cv2
from PIL import Image
import torchvision.transforms as transforms

from slutils.locationP import LocationP
from slutils.utils import getDataFrame, rotate_panorama
from data.base_dataset import BaseDataset
from data.transforms import AddGaussianNoise, RandomErasing
from utils.util import denormalize_image_and_show, get_concat_h_cut, tensor2im
       
def random_crop(tile, size_t=224, size_final=128):
    """ Crop and add noise to the tile"""
    w, h = tile.shape[0:2]
    delta = h - size_t
    ht = np.random.randint(0, delta)
    wt = ht
    temp_tile = tile[ht:h-ht, wt:w-wt]
    tile = cv2.resize(temp_tile, (size_final,size_final))
    return tile

def get_transforms(preprocess):
    transform_list = []
    transform_list += [transforms.ToTensor()]
    transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    if 'erasing' in preprocess:
        transform_list += [RandomErasing(p=0.75, scale=(0.01, 0.10), ratio=(0.2, 0.8), value='random', inplace=True)]
    if 'noise' in preprocess:
        transform_list += [AddGaussianNoise(mean=0.0, std=0.01)]
    return transforms.Compose(transform_list)

class  PanoDataset(BaseDataset):
    """A dataset class for num_augmentations of the StreetLearn dataset.

    It uses the SLutils submodule
    """

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser.set_defaults(dataroot='streetlearn', tile_size=128, area='train', domain=['X','Y'])
        parser.add_argument('--pano_size', type=int, default=128, help='Panorama size')
        parser.add_argument('--tile_style', type=str, default='s2v', help='Style of tiles')
        parser.add_argument('--panorama_mode', type=str, default='list', help='Input mode for the panorama pano|grid|snaps_list')
        parser.add_argument('--no_local_rotation', action='store_true', help='if specified, disable rotate and fliping at location level data augmentation')
        parser.add_argument('--no_aligned', action='store_true', help='map tile and panorama will have different heading angle')
        parser.add_argument('--no_map_random_crop', action='store_true', help='if specified, disable random cropping the map')        
        parser.add_argument('--embedding_model', type=str, default='s2v_ground_full_train_8d', help='specify model from which read features')
        
        if is_train:
            parser.set_defaults(preprocess='crop,erasing')
        else:
            parser.set_defaults(preprocess='none',batch_size=100,flips=False,num_augmentations=1,serial_batches=True)

        return parser

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        self.frame = getDataFrame(opt.area)

    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index - - a random location index. This correspond to the index of a location in the dataset.

        Returns a dictionary that contains
            Y  (tensor) - - a tensor of <num_augmentations> panoramas
                            shape will be [batch_size, direction*, num_augmentations, num_channels, width, heigth] 
                            * This dimention only exists when panorama_mode is 'list' and it correspond to snaps
                            
            labels (tensor) -- A tensor with the location labels 
            index (int) - - index of location 
            paths (str) - - The path to images (Used only for saving images in training/testing time) 
        """

        pano_id = self.frame.loc[index,'pano_id']
        city = self.frame.loc[index,'city']
        yaw = self.frame.loc[index,'yaw']
        loc = LocationP(self.opt.area, pano_id, city, yaw, theta_init=0, base_index='local', tile_style=self.opt.tile_style)  # An instance of location with 'index' -> index+1 
    
        Y = []

        flip = (random.random() > 0.5) if self.opt.flips else False                   # gloabl flip, it will be applied to both domains
        rotation = 0.0 if self.opt.no_rotations else random.choice([0,-270,-180,-90]) # global rotation it will be applied to both domains

        for _ in range(self.opt.num_augmentations):
            
            # Rotation parameters at sample level (it can be used to train a rotational invariant model)
            if not self.opt.no_local_rotation and not self.opt.no_rotations:
                tile_rotation = random.choice([0,-270,-180,-90])
                pano_rotation = random.uniform(-180,180) if self.opt.no_aligned else tile_rotation 
            else:
                tile_rotation=rotation
                pano_rotation=rotation
            
            zoom = np.random.randint(18,20) if self.opt.isTrain else self.opt.tile_zoom

            # Get panorama
            if self.opt.panorama_mode == 'grid':
                pano = [loc.getSnaps(size=self.opt.pano_size, mode='grid', flip=flip, rotation=pano_rotation, noise=self.opt.isTrain)]
           
            elif self.opt.panorama_mode == 'list':
                pano = loc.getSnaps(size=self.opt.pano_size, mode='list', flip=flip, rotation=pano_rotation, noise=self.opt.isTrain) #[F,L,R,B]
           
            elif self.opt.panorama_mode == 'pano':
                yaw  = rotation + np.random.normal(0,5) # A slighly random rotation
                pitch = np.random.normal(0,5)
                roll = np.random.normal(0,5)
                pano = loc.getPano(flip=flip, size=(self.opt.pano_size*2,self.opt.pano_size))
                pano = [rotate_panorama(pano, roll, pitch, yaw)]

            else:
                raise Exception('Panorama mode not found')

            for img in pano:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Convert to RGB and change range to [0-1]
                img = Image.fromarray(img)
                img = get_transforms(self.opt.preprocess)(img)
                Y.append(img) # Append current image example to location list of snaps
                
        Y = torch.stack(Y, dim=0)
        if self.opt.panorama_mode == 'list':
            lista = torch.chunk(Y, self.opt.num_augmentations, dim=0)
            Y = torch.stack(lista, dim=0)
            
        sample = {'Y':Y}
        sample['labels'] = torch.full((1, self.opt.num_augmentations), index)
        sample['paths'] = str(index) + '.jpg'
        sample['index'] = index
        
        return sample
        
    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(getDataFrame(self.opt.area))
