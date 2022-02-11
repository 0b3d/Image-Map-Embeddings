import os
import numpy as np
import torch
import random

import cv2
from PIL import Image
import torchvision.transforms as transforms
from slutils.locationM import LocationM
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

class MapDataset(BaseDataset):
    """A dataset class for num_augmentations of the StreetLearn dataset.

    It uses the slutils submodule
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
            X  (tensor) - - a tensor of <num_augmentations> tiles 
                            shape will be [batch_size, num_augmentations, num_channels, width, heigth]
            labels (tensor) -- A tensor with the location labels 
            index (int) - - index of location 
            paths (str) - - The path to images (Used only for saving images in training/testing time) 
        """

        pano_id = self.frame.loc[index,'pano_id']
        city = self.frame.loc[index,'city']
        yaw = self.frame.loc[index,'yaw']
        loc = LocationM(self.opt.area, pano_id, city, yaw, base_index='local', tile_style=self.opt.tile_style)  # An instance of location with 'index' -> index+1 
    
        X = []

        flip = (random.random() > 0.5) if self.opt.flips else False                   # gloabl flip, it will be applied to both domains
        rotation = 0.0 if self.opt.no_rotations else random.choice([0,-270,-180,-90]) # global rotation it will be applied to both domains

        for _ in range(self.opt.num_augmentations):
            
            # Rotation parameters at sample level (it can be used to train a rotational invariant model)
            if not self.opt.no_local_rotation and not self.opt.no_rotations:
                tile_rotation = random.choice([0,-270,-180,-90])
            else:
                tile_rotation=rotation

            zoom = np.random.randint(18,20) if self.opt.isTrain else self.opt.tile_zoom

            # Get tile
            tile = loc.getTile(zoom=zoom, crop_size=self.opt.tile_size)
            tile = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
            tile = Image.fromarray(tile)
            tile = get_transforms(self.opt.preprocess)(tile)
            X.append(tile)
       
        X = torch.stack(X, dim=0)
            
        sample = {'X':X}
        sample['labels'] = torch.full((1, self.opt.num_augmentations), index)
        sample['paths'] = str(index) + '.jpg'
        sample['index'] = index
        
        return sample
    
    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(getDataFrame(self.opt.area))
