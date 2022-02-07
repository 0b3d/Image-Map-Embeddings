import cv2
import torch
import random
import numpy as np

import torchvision.transforms as transforms

from PIL import Image
from utils.util import tensor2im
from aerial.tile import MetaTile, deg2num, num2deg
from data.base_dataset import BaseDataset
from data.transforms import AddGaussianNoise, RandomErasing
from utils.util import modify_parser
from aerial.utils import draw_north
from aerial.area import get_area_extents

def get_transforms(preprocess):
    transform_list = []
    transform_list += [transforms.ToTensor()]
    if 'normalize' in preprocess:
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    if 'erasing' in preprocess:
        transform_list += [RandomErasing(p=0.75, scale=(0.01, 0.1), ratio=(0.2, 0.8), value='random', inplace=True)]
    if 'noise' in preprocess:
        transform_list += [AddGaussianNoise(mean=0.0, std=0.01)]

    return transforms.Compose(transform_list)

def add_noise(lat, lon, z, rotation, opt):
    delta_lat = 360/2**z
    delta_lon = (85.0511 * 2)/2**z
    lat_ = random.gauss(mu=lat, sigma=0.10*delta_lat) if not opt.no_shifts else lat
    lon_ = random.gauss(mu=lon, sigma=0.10*delta_lon) if not opt.no_shifts else lon
    
    scale_ = random.uniform(opt.z_scale[0], opt.z_scale[1])
    if opt.rotation_noise_type == 'gauss':
        rotation_ = rotation + random.gauss(mu=rotation, sigma=opt.rotation_std) if not opt.no_rotations else 0.0
    elif opt.rotation_noise_type == 'uniform':
        rotation_ = random.uniform(0.0, 2*np.pi) if not opt.no_rotations else 0.0
    else:
        raise NotImplementedError("Rotation noise type not implemented")
    
    rotation_ %= 2*np.pi
    return [lat_, lon_, rotation_, scale_]

class MetaTilesPredictDataset(BaseDataset):
    """A dataset that provides map and aerial tiles at a specific zoom level with orientations.
       It is used to predict all descriptors in an area.
    """

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser.set_defaults(tile_size=256, area='London_test')

        parser.add_argument('--T', type=int, default=8, help='Orientation resolution')
        parser.add_argument('--pano_size', type=int, default=256, help='The size of the aerial image') 
        parser.add_argument('--extent', type=float, nargs=4, help='Optional working extent [min_lat, min_lon, max_lat, max_lon]') 
        parser.add_argument('--aerial_dir', type=str, default='aerial_tiles', help='Name of directory with the aerial tiles')
        parser.add_argument('--domain', nargs='+', type=str, default="aerial", choices=["map","aerial"], help='A list of indices to show (based in python indexing 0:4999)')
        
        modify_parser(parser, 'tile_zoom', 'nargs', '+')

        if is_train:
            parser.set_defaults(preprocess='normalize,blur,erasing', panorama_mode='grid')
        else:
            parser.set_defaults(flips=False, preprocess='normalize', panorama_mode='grid')
            parser.add_argument('--scale_factor', type=int, default=1, help='map scale factor')

        return parser

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        self.target_domain = self.opt.domain

        areas = get_area_extents()
        extent = areas[opt.area] if opt.extent is None else opt.extent
        self.opt.extent = extent
        self.extent = extent 
        
        limits = { z:self.get_limits(z) for z in opt.tile_zoom} 

        z = opt.tile_zoom[0]
        W = limits[z][2] - limits[z][0] + 1 # Width 
        H = limits[z][3] - limits[z][1] + 1 # Height
        T = opt.T                           # Angle

        grid = np.zeros((H,W,T,5))
        x = np.arange(limits[z][0],limits[z][2]+1,1)
        y = np.arange(limits[z][1],limits[z][3]+1,1)
        t = np.linspace(0,2*np.pi,T,endpoint=False)
        c = np.zeros((y.shape[0],x.shape[0],4))

        for j in range(H):
            for i in range(W):
                lat, lon = num2deg(x[i]+0.5,y[j]+0.5,z)
                c[j,i,:] = np.asarray([lat, lon, y[j], x[i]])
        
        grid[:,:,:,:4] = np.expand_dims(c,2)
        grid[:,:,:, 4] = np.tile(t,H*W).reshape(H,W,T)

        self.set_coords(grid)
        self.aerial_dir = opt.aerial_dir 
        self.dataroot = opt.dataroot

    def set_coords(self, coords):
        self._coords = coords

    def get_limits(self,z):
        min_x, min_y = deg2num(self.extent[2],self.extent[1],z)
        max_x, max_y = deg2num(self.extent[0],self.extent[3],z)
        return [min_x,min_y,max_x,max_y]
    
    def __getitem__(self, index):
        """
        Parameters:
            index --> a random index. 

        Returns a dictionary that contains X, Y, coords, index and labels
            X  (tensor) - - a tensor of map tiles 
            Y  (tensor) - - a tensor of aerial tiles 
            labels (tensor) -- A tensor with the location label (same as index here)
            index (int) - - index of location 
        """
        images = {}
        for domain in self.opt.domain:
            images[domain] = []

        coords = self._coords.reshape(-1,5)
        lat, lon, theta = coords[index,0], coords[index,1], coords[index,4]                        
        loc = (lat, lon, self.opt.tile_zoom[0])

        for domain in self.opt.domain:
            img = MetaTile(loc, self.dataroot, aerial_dir=self.opt.aerial_dir).get_metatile(domains=[domain],rotation=theta)[0]
            
            if self.opt.tile_size != 256 and domain == 'map':
                img = cv2.resize(img, (self.opt.tile_size, self.opt.tile_size))
            if self.opt.pano_size != 256 and domain == 'aerial':
                img = cv2.resize(img, (self.opt.pano_size, self.opt.pano_size))
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = get_transforms(self.opt.preprocess)(img)
            images[domain].append(img)
      
        sample = {}
        for domain in self.opt.domain:
            sample[domain] = torch.stack(images[domain], dim=0)
        
        sample['labels'] = torch.full((1, self.opt.num_augmentations), index, dtype=torch.long)
        sample['coords'] = np.asarray([lat,lon,theta])
        sample['index'] = index
        return sample
    
    def show_dataset(self,examples=2, random=True):
        
        if random:
            examples = np.random.randint(0,self.__len__(),examples)
        else:
            examples = np.arange(0,examples)

        for index in examples:
            sample = self.__getitem__(index)
            
            if 'aerial' in sample.keys() and 'map' in sample.keys():
                for i in range(self.opt.num_augmentations):
                    A = sample['map'][i]
                    B = sample['aerial'][i]
                    coords = sample['coords']

                    imA = tensor2im(A.view(1, A.size(0), A.size(1), A.size(2)))
                    imB = tensor2im(B.view(1, B.size(0), B.size(1), B.size(2)))
                    imA = cv2.cvtColor(imA, cv2.COLOR_RGB2BGR)
                    imB = cv2.cvtColor(imB, cv2.COLOR_RGB2BGR)

                    imB = draw_north(imB,coords[2],origin=np.asarray([64,64]))

                    if imA.shape[0] != imB.shape[0]:
                        cv2.imshow("Tile", imA)
                        cv2.imshow("Aerial", imB)
                    else:
                        img = np.concatenate((imA, imB),axis=1)
                        cv2.imshow("Location", img)
                    
                    cv2.waitKey(0)
            
            else:
                domain = self.opt.domain[0]
                for i in range(self.opt.num_augmentations):
                    A = sample[domain][i]
                    imA = tensor2im(A.view(1,A.size(0),A.size(1),A.size(2)))
                    imA = cv2.cvtColor(imA, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Tile", imA)
                    cv2.waitKey(0)            

    def __len__(self):
        """Return the total number of images in the dataset."""
        return self._coords.reshape(-1,5).shape[0]
