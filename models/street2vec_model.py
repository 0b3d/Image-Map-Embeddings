import torch
import itertools
import torch.nn.functional as F
from .base_model import BaseModel
from .nets.street2vec_nets import define_netX, define_netY, define_netEMBX, define_netEMBY
from .nets.softtriplet import SoftTripletLoss

class Street2VecModel(BaseModel):
    """ This class implements the network for embedding images and map tiles 
        It expect as input a dictionary with images from two domains X and Y.
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
        parser.add_argument('--embedding_dim', type=int, default=16, help='Dimension size in the embedding space')
        parser.add_argument('--scale', type=int, default=32, help='Radius of the hypersphere')
        parser.add_argument('--no_l2_norm', action='store_true', help='Disable l2-norm')
        parser.add_argument('--alpha', type=float, default=0.2, help='For soft triplet loss')
        
        if is_train:
            parser.set_defaults(batch_size=15,n_epochs=30, n_epochs_decay=20, lr=0.00004)
            parser.add_argument('--l1', type=float, default=1.0, help='Lambda 1 factor for loss function')
            parser.add_argument('--l2', type=float, default=1.0, help='Lambda 2 factor for loss function')
            parser.add_argument('--l3', type=float, default=1.0, help='Lambda 3 factor for loss function')
            parser.add_argument('--l4', type=float, default=1.0, help='Lambda 4 factor for loss function')
        else:
            parser.set_defaults(batch_size=15, eval=True)

        return parser

    def __init__(self, opt):
        """Initialize the class.

        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseModel.__init__(self, opt)
        
        if self.opt.isTrain and len(opt.domain) == 1:
            raise AssertionError('Street2vec model requeres two domains, only {} was given'.format(opt.domain))

        self.loss_names = ['l1', 'l2', 'l3', 'l4', 'soft']
        self.visual_names = ['X','Yf','Yl','Yr','Yb'] if opt.panorama_mode == 'list' else ['X_thumbnail', 'Y_thumbnail']
        
        # Define networks
        self.model_names = ['X','Y', 'EMBX','EMBY']
        self.netX = define_netX(opt)
        self.netY = define_netY(opt)
        self.netEMBX = define_netEMBX(opt)
        self.netEMBY = define_netEMBY(opt)

        if self.opt.isTrain:
            parameters = []
            for net_name in self.model_names:
                net = getattr(self, 'net'+net_name)
                parameters.append(net.parameters())

            self.optimizer_names = ['O']
            self.optimizer_O = torch.optim.Adam(itertools.chain(*parameters), lr=opt.lr, betas=(opt.beta1, 0.999))
            self.optimizers = [self.optimizer_O]
            self.criterion = SoftTripletLoss(self.opt, self.device)

    def set_input(self, sample):
        """Unpack sample data from the dataloader and perform necessary pre-processing steps.

        The data can be in either of the following formats
            - when opt.panorama_mode is list    ->  

        Parameters:
            sample (dict): include the data itself and its metadata information.
        """
        X = sample[self.opt.domain[0]].to(self.device) 
        Y = sample[self.opt.domain[1]].to(self.device) 
        
        self.X  = X.view(-1, 3, X.size(3), X.size(4))       #   X - > [batch_size, num_augmentations, num_channels, width, heigth]
        
        if self.opt.panorama_mode == 'list':
            # Y -> [batch_size, num_augmentations, snaps*, num_channels, width, heigth]
            self.Yf = Y[:,:,0,:,:,:].view(-1,3,Y.size(4), Y.size(5))
            self.Yl = Y[:,:,1,:,:,:].view(-1,3,Y.size(4), Y.size(5))
            self.Yr = Y[:,:,2,:,:,:].view(-1,3,Y.size(4), Y.size(5))
            self.Yb = Y[:,:,3,:,:,:].view(-1,3,Y.size(4), Y.size(5))
        else:
            # Y - > [batch_size, num_augmentations, num_channels, width, heigth]
            self.Y  = Y.view(-1, 3, Y.size(3), Y.size(4))
            self.Y_thumbnail = F.interpolate(self.Y, size=128).detach() # For visualization
            self.X_thumbnail = F.interpolate(self.X, size=128).detach() # For visualization

        self.index =        sample['index']
        self.labels =       sample['labels'].to(self.device).view(-1)
        self.N = self.opt.batch_size*self.opt.num_augmentations

    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>."""
        
        self.X_f = self.netX(self.X)                
        self.X_d = self.X_f.view(self.X_f.size(0),-1)  

        if self.opt.panorama_mode == 'list':        
            self.Y_flist = [self.netY(getattr(self, name)) for name in ['Yf','Yl','Yr','Yb']] 
            self.Y_dlist = [Y.view(Y.size(0),-1) for Y in self.Y_flist]
            self.Y_d = torch.cat(self.Y_dlist,dim=1) 
        
        else:                                       
            self.Y_f = self.netY(self.Y)             
            self.Y_d = self.Y_f.view(self.Y_f.size(0),-1)
            
        self.X_o = self.netEMBX(self.X_d) 
        self.Y_o = self.netEMBY(self.Y_d)        
        
    def backward(self):
        """Calculate loss"""
        self.loss_l1, self.loss_l2, self.loss_l3, self.loss_l4 = self.criterion.batch_all(self.X_o, self.Y_o, self.labels, 'mean')
        self.loss_soft = self.opt.l1 * self.loss_l1 + self.opt.l2 * self.loss_l2 + self.opt.l3 * self.loss_l3 + self.opt.l4 * self.loss_l4 
        self.loss_soft.backward()

    def optimize_parameters(self):
        self.forward()
        self.optimizer_O.zero_grad()
        self.backward()
        self.optimizer_O.step()

    def compute_visuals(self, writer, total_iters):
        visuals = self.get_current_visuals()
        images = []
        vnames = ''                
        for key in visuals:
            mean = torch.Tensor([0.5, 0.5, 0.5]).view(1,3,1,1).to(self.device)
            std = torch.Tensor([0.5, 0.5, 0.5]).view(1,3,1,1).to(self.device)
            
            v = visuals[key]*std + mean
            images.append(v[0])
            vnames += '-' + key

        images = torch.stack(images,0)
        writer.add_images(vnames, images, global_step=total_iters)



