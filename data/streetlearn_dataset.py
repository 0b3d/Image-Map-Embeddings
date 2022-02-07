import cv2
import random
import numpy as np
import torch

from PIL import Image
import torchvision.transforms as transforms

from slutils.area import Area
from slutils.utils import rotate_panorama
from data.base_dataset import BaseDataset
from data.transforms import AddGaussianNoise, RandomErasing
from utils.util import tensor2im
       
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
    if 'normalize' in preprocess:
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    if 'erasing' in preprocess:
        transform_list += [RandomErasing(p=0.75, scale=(0.01, 0.10), ratio=(0.2, 0.8), value='random', inplace=True)]
    if 'noise' in preprocess:
        transform_list += [AddGaussianNoise(mean=0.0, std=0.01)]
    return transforms.Compose(transform_list)

class StreetLearnDataset(BaseDataset):
    """A customized dataset Class for StreetLearn data """

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser.set_defaults(dataroot='streetlearn', tile_size=128, area='train', domain=['X','Y'])
        
        parser.add_argument('--pano_size', type=int, default=128, help='Panorama size')
        parser.add_argument('--panorama_mode', type=str, default='list', help='Input mode for the panorama pano|grid|list')
        parser.add_argument('--no_local_rotation', action='store_true', help='Disable rotations and fliping at location level')
        parser.add_argument('--no_map_random_crop', action='store_true', help='Disable random cropping for the map tile')
        parser.add_argument('--no_aligned', action='store_true', help='Disabled tile and panorama aligment')
        parser.add_argument('--flips', action='store_true', help='If specified use flippling for data augmentation')
        parser.add_argument('--no_rotations', action='store_true', help='Disable rotations for data augmentation')
        
        if is_train:
            parser.set_defaults(preprocess='erasing,normalize')
        else:
            parser.set_defaults(preprocess='normalize', batch_size=100, flips=False, num_augmentations=1, serial_batches=True)

        return parser

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        self.area = Area(opt.area, opt.dataroot)
        self.dataroot = opt.dataroot

    def __getitem__(self, index):
        """ Gets a sample location including augmentations.

        Parameters:
            index -- Index of the location.

        Returns a dictionary that contains
            X  (tensor) - - Map tiles' tensor with shape [batch_size, num_augmentations, num_channels, width, heigth]
            Y  (tensor) - - Panoramas tensor with shape [batch_size, direction*, num_augmentations, num_channels, width, heigth] 
                            * Only exists when panorama_mode is 'list'
                            
            labels (tensor) -- A tensor with the location labels 
            index (int) - - index of location 
            paths (str) - - Path to panorama (used for some visualizations)
        """

        zooms = [18,19] if self.opt.isTrain else [self.opt.tile_zoom]
        
        loc = self.area.get_location(index, zooms=zooms)
        X, Y = [],[]

        flip = (random.random() > 0.5) if self.opt.flips else False                   # It will be applied to both domains
        rotation = 0.0 if self.opt.no_rotations else random.choice([0,-270,-180,-90]) # It will be applied to both domains

        for _ in range(self.opt.num_augmentations):
            
            # local rotation parameters
            if not self.opt.no_local_rotation and not self.opt.no_rotations:
                tile_rotation = random.choice([0,-270,-180,-90])
                pano_rotation = random.uniform(-180,180) if self.opt.no_aligned else tile_rotation 
            else:
                tile_rotation=rotation
                pano_rotation=rotation
            
            zoom = np.random.randint(18,20) if self.opt.isTrain else self.opt.tile_zoom

            tile = loc.get_tile(zoom=zoom, rotation=tile_rotation, flip=flip)
            if not self.opt.no_map_random_crop:
                tile = random_crop(tile,size_final=self.opt.tile_size)
            else:
                if not (tile.shape[0] == self.opt.tile_size):
                    tile = cv2.resize(tile,(self.opt.tile_size,self.opt.tile_size))
            
            tile = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
            tile = Image.fromarray(tile)
            tile = get_transforms(self.opt.preprocess)(tile)
            X.append(tile)

            # Get panorama
            if self.opt.panorama_mode == 'grid':
                pano = [loc.get_snaps(size=self.opt.pano_size, mode='grid', flip=flip, rotation=pano_rotation, noise=self.opt.isTrain)]
            
            elif self.opt.panorama_mode == 'list':
                pano = loc.get_snaps(size=self.opt.pano_size, mode='list', flip=flip, rotation=pano_rotation, noise=self.opt.isTrain) #[F,L,R,B]
            
            elif self.opt.panorama_mode == 'pano':
                yaw  = rotation + np.random.normal(0,5) # A small random rotation
                pitch = np.random.normal(0,5)
                roll = np.random.normal(0,5)
                pano = loc.get_pano(flip=flip, size=(self.opt.pano_size*2,self.opt.pano_size))
                pano = [rotate_panorama(pano, roll, pitch, yaw)]

            else:
                raise Exception('Panorama mode {} not found'.format(self.opt.panorama_mode))

            for img in pano:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                img = Image.fromarray(img)
                img = get_transforms(self.opt.preprocess)(img)
                Y.append(img) 
        
        X = torch.stack(X, dim=0)
        Y = torch.stack(Y, dim=0)
        if self.opt.panorama_mode == 'list':
            lista = torch.chunk(Y, self.opt.num_augmentations, dim=0)
            Y = torch.stack(lista, dim=0)
            
        sample = {'X':X, 'Y':Y}
        sample['labels'] = torch.full((1, self.opt.num_augmentations), index)
        sample['paths'] = str(index) + '.jpg'
        sample['index'] = index
        return sample
    
    def show_dataset(self,examples=2):
        for _ in range(examples):
            index = np.random.randint(0,self.__len__())
            sample = self.__getitem__(index)
            print(sample['Y'].size())
            if self.opt.panorama_mode == 'list':
                snaps = torch.chunk(sample['Y'],4,dim=1)
                pano = torch.cat(snaps, dim=4).squeeze()
            else:
                pano = sample['Y']    

            for i in range(self.opt.num_augmentations):
                X = sample['X'][i]
                Y = pano[i]
                imA = tensor2im(X.view(1,X.size(0),X.size(1),X.size(2)))
                imB = tensor2im(Y.view(1,Y.size(0),Y.size(1),Y.size(2)))
                imA = cv2.cvtColor(imA, cv2.COLOR_RGB2BGR)
                imB = cv2.cvtColor(imB, cv2.COLOR_RGB2BGR)

                if imA.shape[0] != imB.shape[0]:
                    cv2.imshow("Tile", imA)
                    cv2.imshow("Panorama", imB)
                else:
                    img = np.concatenate((imA, imB),axis=1)
                    cv2.imshow("Location", img)
                
                cv2.waitKey(0)

    def __len__(self):
        """Return the total number of images in the dataset."""
        return self.area.N
