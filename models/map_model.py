"This model is the map sub-network used only for testing, not training "
import torch
import sys
import itertools

import torch.nn.functional as F

from .base_model import BaseModel
from .nets.street2vec_nets import define_netX, define_netVLAD, define_netEMBX

class MapModel(BaseModel):
    """ This class implements the street2vec model (V1), for embedding images and map tiles 
        It expect as sample a dictionary with images from two domains X and Y.
    """

    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        """Add new dataset-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.

        """
        # New arguments
        parser.set_defaults(panorama_mode='grid')
        parser.add_argument('--embedding_dim', type=int, default=8, help='Dimensions in the embedding space')
        parser.add_argument('--scale', type=int, default=32, help='Dimensions in the embedding space')
        parser.add_argument('--no_l2_norm', action='store_true', help='Disable l2-norm') # default is false
        parser.add_argument('--clusters', type=int, default=64, help='Number of VLAD clusters')
        parser.add_argument('--alpha', type=float, default=2.0, help='For soft triplet loss')
        parser.add_argument('--no_vlad', action='store_true', help='If set do not include VLAD') # By default VLAD is included
        parser.set_defaults(batch_size=15, eval=True)

        return parser

    def __init__(self, opt):
        """Initialize the class.

        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseModel.__init__(self, opt)
        
        # specify the images you want to save/display. The training/test scripts will call <BaseModel.get_current_visuals>
        self.visual_names = ['X'] if opt.panorama_mode == 'list' else ['X_thumb']
        
        # Define networks
        self.model_names = ['X','EMBX']     # specify the models you want to save to the disk
        self.netX = define_netX(opt)
        self.netEMBX = define_netEMBX(opt)

        if not self.opt.no_vlad:                        # if no_vlad flag is not set load vlad
            self.model_names.extend(['VLADX'])
            self.netVLADX = define_netVLAD(opt)

        if self.opt.isTrain:
            parameters = []
            for net_name in self.model_names:
                net = getattr(self, 'net'+net_name)
                parameters.append(net.parameters())
            
        print('initialized')


    def set_input(self, sample):
        """Unpack sample data from the dataloader and perform necessary pre-processing steps.

        Parameters:
            sample (dict): include the data itself and its metadata information.
        """
        
        X = sample[self.opt.domain[0]].to(self.device) # [batch_size, num_augmentations, num_channels, width, heigth]
        
        self.X  = X.view(-1, 3, X.size(3), X.size(4))
        self.index =        sample['index']
        self.image_paths =  sample['paths']
        self.labels =       sample['labels'].to(self.device).view(-1)
        self.N = self.opt.batch_size*self.opt.num_augmentations

    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>."""
        
        self.X_f = self.netX(self.X)                 # extract features from domain X
        self.X_d = self.X_f.view(self.X_f.size(0),-1) if self.opt.no_vlad else self.netVLADX(self.X_f)  # get a vector descriptor for domain X       
        self.X_o = self.netEMBX(self.X_d)            # project X descriptor to a lower dimension




