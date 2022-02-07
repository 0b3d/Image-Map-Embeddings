import cv2
import torch
import math
import random
import numpy as np

from PIL import Image
import torchvision.transforms as transforms

from aerial.tile import MetaTile
from utils.util import tensor2im
from data.base_dataset import BaseDataset
from data.transforms import AddGaussianNoise, RandomErasing
from utils.util import modify_parser


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
        raise NotImplementedError('Rotation type not implemented yet')
    
    rotation_ %= 2*np.pi
    return [lat_, lon_, rotation_, scale_]

class MetaTilesTrainDataset(BaseDataset):

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser.set_defaults(tile_size=256, area='London_test')

        parser.add_argument('--aerial_dir', type=str, default='aerial_tiles', help='Name of directory with the aerial tiles')
        parser.add_argument('--N', type=int, default=10000, help='Number of metatiles to generate in every epoch')
        parser.add_argument('--pano_size', type=int, default=256, help='The size of the aerial image')
        parser.add_argument('--map_noise', action='store_true', help='Enable noise in the maps domain')
        parser.add_argument('--domain', nargs='+', type=str, default="aerial", choices=["map","aerial"], help='Domain(s) to process')
        parser.add_argument('--rotation_noise_type', type=str, default='uniform', help='Noise type for rotations')
        parser.add_argument('--rotation_std', type=float, default=3.1416/12, help='Rotation params, only if rotation_noise_type is Gaussian')
        parser.add_argument('--no_shifts', action='store_true', help='Disable shifting for data augmentation')
        parser.add_argument('--no_rotations', action='store_true', help='if specified, disables rotation for data augmentation')
        parser.add_argument('--z_scale', type=float, nargs=2, default=[0.7072,1.4142], help='Scale range for images')
        parser.add_argument('--flips', action='store_true', help='if specified use flippling for data augmentation')
        modify_parser(parser, 'tile_zoom', 'nargs', '+')

        if is_train:
            parser.set_defaults(preprocess='normalize,blur,erasing', panorama_mode='grid')
        else:
            parser.set_defaults(preprocess='normalize', flips=False, num_augmentations=1, panorama_mode='grid')
            parser.add_argument('--scale_factor', type=int, default=1, help='map scale factor')

        return parser

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)

        #assert opt.isTrain, "Dataset MetatilesTrain is only for training"
        if self.opt.isTrain:
            areas = [[51.4601825, -0.202123,  51.5477509, -0.1282832], # TQ27NE + TQ28SE (London)
                    [51.8782034 , -2.2913592, 51.9683822, -2.1469677],  # SO82 (Countryside)
                    [51.4246955, -0.9946054, 51.4690068, -0.9216473]   # SU77SW (Reading)
                    ]
                    
        else:
            areas = [[51.4601825, -0.1282832, 51.5477509, -0.0544434]] # Use TQ37NW as validation 
        
        new_areas = []
        # Remove a 5% strip in all sides to avoid boundary effects
        for extent in areas:
            strip_lat = 0.05*(extent[2] - extent[0])
            strip_lon = 0.05*(extent[3] - extent[1])        
            area = [extent[0]+strip_lat, extent[1]+strip_lon, extent[2]-strip_lat, extent[3]-strip_lon]
            new_areas.append(area)

        self.areas = new_areas    
        self.aerial_dir = opt.aerial_dir 
        self.dataroot = opt.dataroot

    def __getitem__(self, index):

        images = {}
        for domain in self.opt.domain:
            images[domain] = []

        coords_list = []
        
        extent = random.choice(self.areas)
        lat = random.uniform(extent[0], extent[2])
        lon = random.uniform(extent[1], extent[3])
        z = random.choice(self.opt.tile_zoom)   

        coords = (lat, lon, z) 
        rotation = random.uniform(0, 2*np.pi) if not self.opt.no_rotations else 0.0
        flip = random.choice([None,-1,0,1]) if self.opt.flips else None 
        image_yaw = np.zeros((self.opt.num_augmentations,))
        map_yaw = np.zeros((self.opt.num_augmentations,))

        
        for a in range(self.opt.num_augmentations):
            
            lat_, lon_, rotation_, scale_ = add_noise(lat, lon, z, rotation, self.opt)
            coords = (lat_, lon_, z)

            for domain in self.opt.domain:

                if domain == 'aerial':  
                    lat_, lon_, rotation_, scale_ = add_noise(lat, lon, z, rotation, self.opt)

                    scale_ = 1.0 if a == 0 else scale_      # Force the first pair to have same scale
                    z_ = math.log2( scale_ ) + z
                    coords = (lat_, lon_, z)
                
                    text = "{:.3f},{:.3f},{:.2f},{:.0f}".format(lat_,lon_, z_, rotation_*180/3.1416) if self.opt.show_dataset else None
                    blur = True if 'blur' in self.opt.preprocess else False
                    img = MetaTile(coords, self.dataroot, self.aerial_dir).get_metatile(domains=[domain], rotation=rotation_, scale=scale_, flip=flip, blur=blur, text=text)[0]
                    image_yaw[a] = rotation_
                
                else:
                    if self.opt.map_noise:
                        lat_, lon_, rotation_, scale_ = add_noise(lat, lon, z, rotation, self.opt)
                        scale_ = 1.0 
                        z_ = math.log2( scale_ ) + z
                        coords = (lat_, lon_, z)
                        text = "{:.3f},{:.3f},{:.2f},{:.0f}".format(lat_,lon_, z_, rotation_*180/3.1416) if self.opt.show_dataset else None
                        img = MetaTile(coords, self.dataroot).get_metatile(domains=[domain], rotation=rotation_, scale=scale_, flip=flip, text=text)[0] 
                        map_yaw[a] = rotation_
                    else:
                        text = "{:.3f},{:.3f},{:.2f},{:.0f}".format(lat_,lon_, z, rotation_*180/3.1416) if self.opt.show_dataset else None
                        img = MetaTile(coords, self.dataroot).get_metatile(domains=[domain], rotation=0.0, scale=1.0, flip=flip, text=text)[0] 
                        map_yaw[a] = 0.0

                if self.opt.tile_size != 256 and domain == 'map':
                    img = cv2.resize(img, (self.opt.tile_size, self.opt.tile_size))
                if self.opt.pano_size != 256 and domain == 'aerial':
                    img = cv2.resize(img, (self.opt.pano_size, self.opt.pano_size))
            
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = get_transforms(self.opt.preprocess)(img)
                images[domain].append(img)

            coords_list.append([lat_,lon_,z_])    
        
        sample = {}
        for domain in self.opt.domain:
            sample[domain] = torch.stack(images[domain], dim=0)
        
        sample['labels'] = torch.full((1, self.opt.num_augmentations), index, dtype=torch.long)
        sample['zoom'] = torch.full((1, self.opt.num_augmentations), z-18, dtype=torch.long)
        sample['index'] = index
        sample['paths'] = str(lat) + '_' + str(lon) + '.jpg' # used for some visualizations
        sample['coords'] = np.asarray(coords_list)

        return sample
    
    def show_dataset(self,examples=2):
        for _ in range(examples):
            index = np.random.randint(0,self.__len__())
            sample = self.__getitem__(index)
            if 'aerial' in sample.keys() and 'map' in sample.keys():
                for i in range(self.opt.num_augmentations):
                    A = sample['map'][i]
                    B = sample['aerial'][i]
                    imA = tensor2im(A.view(1,A.size(0),A.size(1),A.size(2)))
                    imB = tensor2im(B.view(1,B.size(0),B.size(1),B.size(2)))
                    imA = cv2.cvtColor(imA, cv2.COLOR_RGB2BGR)
                    imB = cv2.cvtColor(imB, cv2.COLOR_RGB2BGR)

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
        return self.opt.N
