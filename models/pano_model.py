"This model is the panorama sub-network used only for testing, not training "
import torch
import sys
import itertools

import torch.nn.functional as F

from .base_model import BaseModel
from .nets.street2vec_nets import define_netY, define_netVLAD, define_netEMBY

class PanoModel(BaseModel):
    """ This class implements the image subnetwork of street2vec model 
        It expect as sample a dictionary with panoramas "Y"
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
        self.visual_names = ['Y'] if opt.panorama_mode == 'list' else ['Y_thumb']
        
        # Define networks
        self.model_names = ['Y','EMBY']     # specify the models you want to save to the disk
        self.netY = define_netY(opt)
        self.netEMBY = define_netEMBY(opt)

        if not self.opt.no_vlad:                        # if no_vlad flag is not set load vlad
            self.model_names.extend(['VLADY'])
            self.netVLADY = define_netVLAD(opt)

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
        Y = sample['Y'].to(self.device) # [batch_size, num_augmentations, snaps*, num_channels, width, heigth]
        if self.opt.panorama_mode == 'list':
            self.Yf = Y[:,:,0,:,:,:].view(-1,3,Y.size(4), Y.size(5))
            self.Yl = Y[:,:,1,:,:,:].view(-1,3,Y.size(4), Y.size(5))
            self.Yr = Y[:,:,2,:,:,:].view(-1,3,Y.size(4), Y.size(5))
            self.Yb = Y[:,:,3,:,:,:].view(-1,3,Y.size(4), Y.size(5))
        else:
            self.Y  = Y.view(-1, 3, Y.size(3), Y.size(4))
            self.Y_thumb = F.interpolate(self.Y, size=128).detach() # A thumbnail for visualization

        self.index =        sample['index']
        self.image_paths =  sample['paths']
        self.labels =       sample['labels'].to(self.device).view(-1)
        self.N = self.opt.batch_size*self.opt.num_augmentations

    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>."""
        
        if self.opt.panorama_mode == 'list':         # If domain Y is a list of snaps
            self.Y_flist = [self.netY(getattr(self, name)) for name in ['Yf','Yl','Yr','Yb']] # extract features for each snap in domain Y
            self.Y_dlist = [Y.view(Y.size(0),-1) if self.opt.no_vlad else self.netVLADY(Y) for Y in self.Y_flist]
            self.Y_d = torch.cat(self.Y_dlist,dim=1) # Concatenate domain Y snap's descriptors
        else:                                        # if domain Y is a single image
            self.Y_f = self.netY(self.Y)             # extract features for domain Y
            self.Y_d = self.Y_f.view(self.Y_f.size(0),-1) if self.opt.no_vlad else self.netVLADY(self.Y_f) # form a descriptor for Y
            
        self.Y_o = self.netEMBY(self.Y_d)            # project Y descriptor to a lower dimension       




