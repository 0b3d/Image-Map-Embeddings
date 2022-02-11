import os
import sys
import torch
import random
import numpy as np
import pandas as pd

import cv2
from PIL import Image
import torchvision.transforms as transforms

from data.base_dataset import BaseDataset
from utils.util import denormalize_image_and_show, get_concat_h_cut, tensor2im
from datetime import datetime as dt

def get_transforms(preprocess):
    transform_list = []
    transform_list += [transforms.ToTensor()]
    transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    return transforms.Compose(transform_list)

class RobotCarFramesDataset(BaseDataset):
    """A dataset class for num_augmentations of the StreetLearn dataset.

    It uses the SLutils submodule
    """

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser.set_defaults(dataroot='robotcar')
        parser.add_argument('--traversal', type=str, default='2015-10-29-10-55-43', help='Name of the robotcar traversal')
        parser.add_argument('--chunk', type=str, default='1', help='Number of chunk')
        parser.add_argument('--frames_dir', type=str, default='processed_v2', help='The directory where images are saved')
        parser.add_argument('--pano_size', type=int, default=128, help='Panorama size')
        parser.add_argument('--panorama_mode', type=str, default='list', help='Input mode for the panorama pano|grid|snaps_list')
        
        if is_train:
            print("Warning robotcar dataset not supported")
        else:
            parser.set_defaults(preprocess='none',
                                batch_size=100,
                                flips=False,
                                num_augmentations=1,
                                panorama_mode = "list",
                                serial_batches=True)
        return parser

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        
        self.save_dir = os.path.join('datasets/robotcar/', self.opt.traversal, self.opt.frames_dir)
        metafile = os.path.join(self.save_dir, self.opt.traversal + '_chunk' + self.opt.chunk + '.csv')        
        self.frame = pd.read_csv(metafile)

    def __getitem__(self, index):

        ts = self.frame.loc[index,"ts"]
        
        Y = []
        for view in ["front","left","right","rear"]:
            filename = str(ts) + '_' + view + '.png'
            path = os.path.join(self.save_dir, filename)
            tile = cv2.imread(path)
            tile = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
            tile = Image.fromarray(tile)
            tile = get_transforms(self.opt.preprocess)(tile)
            Y.append(tile)
                    
        Y = torch.stack(Y, dim=0)
       
        if self.opt.panorama_mode == 'list':
            lista = torch.chunk(Y, self.opt.num_augmentations, dim=0)
            Y = torch.stack(lista, dim=0)

        sample = {'Y':Y}
        sample['labels'] = torch.full((1, self.opt.num_augmentations), index)
        sample['index'] = index
        sample['paths'] = str(index) + '.jpg'
        return sample
    
    def show_dataset(self,examples=2):
        for _ in range(examples):
            index = np.random.randint(0,self.__len__())
            sample = self.__getitem__(index)
            snaps = torch.chunk(sample['Y'],4,dim=1)
            pano = torch.cat(snaps, dim=4).squeeze()
            Y = pano
            imB = tensor2im(Y.view(1,Y.size(0),Y.size(1),Y.size(2)))
            imB = cv2.cvtColor(imB, cv2.COLOR_RGB2BGR)
            cv2.imshow("Panorama", imB)
            cv2.waitKey(0)

    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(self.frame)
