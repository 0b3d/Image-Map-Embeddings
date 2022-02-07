import os
import torch
import numpy as np
from collections import OrderedDict
from abc import ABC, abstractmethod
from .utils import get_scheduler 

class BaseModel(ABC):
    """This class is an abstract base class (ABC) for models.
    To create a subclass, you need to implement the following five functions:
        -- <__init__>:                      initialize the class; first call BaseModel.__init__(self, opt).
        -- <set_input>:                     unpack data from dataset and apply preprocessing.
        -- <forward>:                       produce intermediate results.
        -- <optimize_parameters>:           calculate losses, gradients, and update network weights.
        -- <modify_commandline_options>:    (optionally) add model-specific options and set default options.
    """

    def __init__(self, opt):
        """Initialize the BaseModel class.

        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions

        When creating your custom class, you need to implement your own initialization.
        In this function, you should first call <BaseModel.__init__(self, opt)>
        Then, you need to define five lists:
            -- self.loss_names (str list):          specify the training losses that you want to plot and save.
            -- self.model_names (str list):         define networks used in our training.
            -- self.visual_names (str list):        specify the images that you want to display and save.
            -- self.optimizer_names (str list):     list names of optimizers to be saved in disk
            -- self.optimizers (optimizer list):    define and initialize optimizers. You can define one optimizer for each network. If two networks are updated at the same time, you can use itertools.chain to group them. See cycle_gan_model.py for an example.
        """
        self.opt = opt
        self.gpu_ids = opt.gpu_ids
        self.isTrain = opt.isTrain
        self.device = torch.device('cuda:{}'.format(self.gpu_ids[0])) if self.gpu_ids else torch.device('cpu')  # get device name: CPU or GPU
        
        self.save_dir = os.path.join(opt.checkpoints_dir, opt.name)  # save all the checkpoints to save_dir
        if opt.preprocess != 'scale_width':  # with [scale_width], input images might have different sizes, which hurts the performance of cudnn.benchmark.
            torch.backends.cudnn.benchmark = True
        self.loss_names = []
        self.model_names = []
        self.visual_names = []
        self.optimizer_names = []
        self.optimizers = []
        self.image_paths = []
        self.metric = 0  # used for learning rate policy 'plateau'
        self.metric_value = None  # Best metric
        self.total_iters = 0     
        self.epoch_iters = 0

        # Set the seed
        if opt.seed != -1:
            np.random.seed(opt.seed)
            #torch.set_deterministic(True)
            torch.manual_seed(opt.seed)
            torch.cuda.manual_seed(opt.seed)
            torch.cuda.manual_seed_all(opt.seed) # if multi-GPU.
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False


    @staticmethod
    def modify_commandline_options(parser, is_train):
        """Add new model-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.
        """
        return parser

    @abstractmethod
    def set_input(self, input):
        """Unpack input data from the dataloader and perform necessary pre-processing steps.

        Parameters:
            input (dict): includes the data itself and its metadata information.
        """
        pass

    @abstractmethod
    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>."""
        pass

    @abstractmethod
    def optimize_parameters(self):
        """Calculate losses, gradients, and update network weights; called in every training iteration"""
        pass

    def setup(self, opt):
        """Load and print networks; create schedulers

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        if self.isTrain:
            self.schedulers = [get_scheduler(optimizer, opt) for optimizer in self.optimizers]
        if not self.isTrain or opt.continue_train:
            load_suffix = 'iter_%d' % opt.load_iter if opt.load_iter > 0 else opt.epoch
            self.load_networks(load_suffix)
        self.print_networks(opt.verbose)

    def eval(self):
        """Make models eval mode during test time"""
        for name in self.model_names:
            if isinstance(name, str):
                net = getattr(self, 'net' + name)
                net.eval()

    def train(self):
        """Make model trainable"""
        for name in self.model_names:
            if isinstance(name, str):
                net = getattr(self, 'net' + name)
                net.train()


    def test(self):
        """Forward function used in test time.

        This function wraps <forward> function in no_grad() so we don't save intermediate steps for backprop
        It also calls <compute_visuals> to produce additional visualization results
        """

        with torch.no_grad():
            self.forward()
            self.compute_visuals()

    def compute_visuals(self):
        """Calculate additional output images for visdom and HTML visualization"""
        pass

    def get_image_paths(self):
        """ Return image paths that are used to load current data"""
        return self.image_paths

    def update_learning_rate(self):
        """Update learning rates for all the networks; called at the end of every epoch"""
        for scheduler in self.schedulers:
            if self.opt.lr_policy == 'plateau':
                scheduler.step(self.metric)
            else:
                scheduler.step()

        lr = self.optimizers[0].param_groups[0]['lr']
        print('learning rate = %.7f' % lr)

    def get_current_visuals(self):
        """Return visualization images. train.py will display these images with visdom, and save the images to a HTML"""
        visual_ret = OrderedDict()
        for name in self.visual_names:
            if isinstance(name, str):
                visual_ret[name] = getattr(self, name)
        return visual_ret

    def get_current_losses(self):
        """Return traning losses / errors. train.py will print out these errors on console, and save them to a file"""
        errors_ret = OrderedDict()
        for name in self.loss_names:
            if isinstance(name, str):
                errors_ret[name] = float(getattr(self, 'loss_' + name))  
        return errors_ret

    def save_networks(self, prefix, epoch_count, epoch_iters=None, total_iters=None, metric_value=None):
        """Save all the networks and optimizers to the disk. It also saves the current iteration and optionally a performance metric.

        Parameters:
            prefix -- current epoch or any text prefix; used in the file name '%s_net_%s.pth' % (prefix, name)
            epoch_count -- current epoch
            epoch_iters -- count of current iterations in current epoch
            total_iters -- total count of iterations 
            metric_value    -- Metric value for current epoch (optional)
        """
        # save networks
        for name in self.model_names:
            if isinstance(name, str):
                save_filename = '%s_net_%s.pth' % (prefix, name)
                save_path = os.path.join(self.save_dir, save_filename)
                net = getattr(self, 'net' + name)
                if isinstance(net, torch.nn.DataParallel):
                    state_dict = net.module.state_dict()
                else:
                    state_dict = net.state_dict()
                
                ckpt = {'epoch_iters': epoch_iters,
                        'total_iters': total_iters,
                        'last_epoch': epoch_count,
                        'metric_value': metric_value,
                        'model_state_dict': state_dict,
                        }

                if len(self.gpu_ids) > 0 and torch.cuda.is_available():
                    torch.save(ckpt, save_path)
                else:
                    torch.save(ckpt, save_path)


        # Save optimizers
        for name in self.optimizer_names:
            if isinstance(name, str):
                save_filename = '%s_optimizer_%s.pth' % (prefix, name)
                save_path = os.path.join(self.save_dir, save_filename)
                optimizer = getattr(self, 'optimizer_' + name)
                
                ckpt = {'epoch_iters': epoch_iters,
                        'total_iters': total_iters,
                        'last_epoch': epoch_count,
                        'metric_value': metric_value,
                        'optimizer_state_dict': optimizer.state_dict(),
                        }

                if len(self.gpu_ids) > 0 and torch.cuda.is_available():
                    torch.save(ckpt, save_path)
                else:
                    torch.save(ckpt, save_path)

    def load_networks(self, prefix):
        """Load all the networks and optimizers (if training) from the disk. It also loads the current iteration and a performance metric.

        Parameters:
            prefix -- current epoch or any text prefix; used in the filename '%s_net_%s.pth' % (prefix, name)
        """
        for name in self.model_names:
            if isinstance(name, str):
                load_filename = '%s_net_%s.pth' % (prefix, name)
                load_path = os.path.join(self.save_dir, load_filename)

                if os.path.isfile(load_path):
                    net = getattr(self, 'net' + name)
                    if isinstance(net, torch.nn.DataParallel):
                        net = net.module

                    # Load checkpoint
                    ckpt = torch.load(load_path, map_location=str(self.device))
                    epoch_count = ckpt['last_epoch']
                    self.opt.epoch_count = epoch_count if prefix == 'latest' else epoch_count + 1
                    self.epoch_iters = 0 #ckpt['epoch_iters']
                    self.total_iters = ckpt['total_iters']
                    if self.isTrain:
                        self.metric_value = ckpt['metric_value'] if self.opt.initial_metric_value is None else self.opt.initial_metric_value
                    else:
                        self.metric_value = ckpt['metric_value']
                    net.load_state_dict(ckpt['model_state_dict'])
                    print('loaded the model from %s, n_epoch: %s num_iters: %s' % (load_path,epoch_count,self.total_iters))
                
                else:
                    print("Warning file {} not found".format(load_path))

        # Load optimizers
        if self.isTrain:
            for name in self.optimizer_names:
                if isinstance(name, str):
                    load_filename = '%s_optimizer_%s.pth' % (prefix, name)
                    load_path = os.path.join(self.save_dir, load_filename)

                    if os.path.isfile(load_path):
                        optimizer = getattr(self, 'optimizer_' + name)

                        # Load checkpoint
                        ckpt = torch.load(load_path, map_location=str(self.device))
                        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
                        print('loaded the optimizer from %s' % load_path)


                    else:
                        print("Warning file {} not found".format(load_path))

       
    def print_networks(self, verbose):
        """Print the total number of parameters in the network and (if verbose) network architecture

        Parameters:
            verbose (bool) -- if verbose: print the network architecture
        """
        print('---------- Networks initialized -------------')
        for name in self.model_names:
            if isinstance(name, str):
                net = getattr(self, 'net' + name)
                num_params = 0
                for param in net.parameters():
                    num_params += param.numel()
                if verbose:
                    print(net)
                print('[Network %s] Total number of parameters : %.3f M' % (name, num_params / 1e6))
        print('-----------------------------------------------')

    def set_requires_grad(self, nets, requires_grad=False):
        """Set requies_grad=Fasle for all the networks to avoid unnecessary computations
        Parameters:
            nets (network list)   -- a list of networks
            requires_grad (bool)  -- whether the networks require gradients or not
        """
        if not isinstance(nets, list):
            nets = [nets]
        for net in nets:
            if net is not None:
                for param in net.parameters():
                    param.requires_grad = requires_grad