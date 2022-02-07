"The general structure of this code is inpired on https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix"

import argparse
import os
from utils import util
import torch
import models
import data
import localizer
import time


class BaseOptions():
    """This class defines options used during both training and test time.

    It also implements several helper functions such as parsing, printing, and saving the options.
    It also gathers additional options defined in <modify_commandline_options> functions in dataset, model and localizer classes.
    """

    def __init__(self):
        """Reset the class; indicates the class hasn't been initailized"""
        self.initialized = False

    def initialize(self, parser):
        """Define the common options that are used in both training and test."""
        # basic parameters
        parser.add_argument('--dataroot', required=False, default='./datasets', help='path to images')
        parser.add_argument('-n','--name', type=str, default='experiment_name', help='name of the experiment. It decides where to store samples and models')
        num_devices = torch.cuda.device_count()
        parser.add_argument('--gpu_ids', type=str, default=str(num_devices-1), help='gpu ids: e.g. 0  0,1,2, 0,2. use -1 for CPU')
        parser.add_argument('--checkpoints_dir', type=str, default='./checkpoints', help='models are saved here')
        parser.add_argument('--show_dataset', action='store_true', help='If given the script will show some dataset examples and then exit')
        # model parameters
        parser.add_argument('-m','--model', type=str, default='street2vec', help='chooses which model to use. [cycle_gan | pix2pix | test | colorization | hash]')
        parser.add_argument('--init_type', type=str, default='normal', help='network initialization [normal | xavier | kaiming | orthogonal]')
        parser.add_argument('--init_gain', type=float, default=0.02, help='scaling factor for normal, xavier and orthogonal.')
        
        # dataset parameters
        parser.add_argument('--num_augmentations', type=int, default=5, help='Number of data augmentations by location')
        parser.add_argument('-d','--dataset_mode', required=False, type=str, default='street2vec', help='chooses how datasets are loaded')
        parser.add_argument('--area', type=str, default='hudsonriver5k', help='name of the area to experiment')
        parser.add_argument('--tile_zoom', type=int, default=18, help='Zoom of map tiles')
        parser.add_argument('--tile_size', type=int, default=256, help='Tile size')
        parser.add_argument('--batch_size', type=int, default=1, help='input batch size')
        parser.add_argument('--serial_batches', action='store_true', help='if true, takes images in order to make batches, otherwise takes them randomly')
        parser.add_argument('--drop_last', action='store_true',help='if true, dataloader will drop the last batch if it is smaller than batch size')
        parser.add_argument('--num_threads', default=4, type=int, help='# threads for loading data')
        parser.add_argument('--max_dataset_size', type=int, default=float("inf"), help='Maximum number of samples allowed per dataset. If the dataset directory contains more than max_dataset_size, only a subset is loaded.')
        parser.add_argument('--preprocess', type=str, default='normalize', help='scaling and cropping of images at load time [resize_and_crop | crop | scale_width | scale_width_and_crop | none]')
        
        # additional parameters
        parser.add_argument('--seed', type=int, default=442, help='Set the seed')
        parser.add_argument('--epoch', type=str, default='latest', help='which epoch to load? set to latest to use latest cached model')
        parser.add_argument('--load_iter', type=int, default='0', help='which iteration to load? if load_iter > 0, the code will load models by iter_[load_iter]; otherwise, the code will load models by [epoch]')
        parser.add_argument('--verbose', action='store_true', help='if specified, print more debugging information')
        parser.add_argument('--suffix', default='', type=str, help='customized suffix: opt.name = opt.name + suffix: e.g., {model}_{netG}_size{load_size}')
        # localizer parameters
        parser.add_argument('--localizer', type=str, default=None, help='Name of the algorithm for localization')
        self.initialized = True
        return parser

    def gather_options(self):
        """Initialize our parser with basic options(only once).
        Add additional model-specific and dataset-specific options.
        These options are defined in the <modify_commandline_options> function
        in model and dataset classes.
        """
        if not self.initialized:  # check if it has been initialized
            parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)

        # get the basic options
        opt, _ = parser.parse_known_args()

        # modify dataset-related parser options
        if opt.dataset_mode != "None":
           dataset_name = opt.dataset_mode
           dataset_option_setter = data.get_option_setter(dataset_name)
           parser = dataset_option_setter(parser, self.isTrain)

        # modify model-related parser options
        model_name = opt.model
        model_option_setter = models.get_option_setter(model_name)
        parser = model_option_setter(parser, self.isTrain)
        opt, _ = parser.parse_known_args()  # parse again with new defaults

        # Modify localizer-related parser options
        if opt.localizer is not None:
           localizer_option_setter = localizer.get_option_setter(opt.localizer)
           parser = localizer_option_setter(parser)

        # save and return the parser
        self.parser = parser
        return parser.parse_args()

    def print_options(self, opt):
        """Print and save options

        It will print both current options and default values(if different).
        It will save options into a text file / [checkpoints_dir] / opt.txt
        """
        message = ''
        now = time.strftime("%c")
        message += '----------------- Options (%s) ---------------\n' % now
        for k, v in sorted(vars(opt).items()):
            comment = ''
            default = self.parser.get_default(k)
            if v != default:
                comment = '\t[default: %s]' % str(default)
            message += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
        message += '----------------- End -------------------'
        print(message)

        # save to the disk
        expr_dir = os.path.join(opt.checkpoints_dir, opt.name)
        util.mkdirs(expr_dir)
        file_name = os.path.join(expr_dir, '{}_opt.txt'.format(opt.phase))
        with open(file_name, 'a') as opt_file:   #with open(file_name, 'wt') as opt_file:
            opt_file.write(message)
            opt_file.write('\n')

    def parse(self):
        """Parse our options, create checkpoints directory suffix, and set up gpu device."""
        opt = self.gather_options()
        opt.isTrain = self.isTrain   # train or test

        # process opt.suffix
        if opt.suffix:
            suffix = ('_' + opt.suffix.format(**vars(opt))) if opt.suffix != '' else ''
            opt.name = opt.name + suffix

        self.print_options(opt)

        # set gpu ids
        n_gpus_available = torch.cuda.device_count()
        print('There are {} available gpus'.format(n_gpus_available))
        for i in range(n_gpus_available):
            print('Device {} is a {}'.format(i,torch.cuda.get_device_name(i)))

        str_ids = opt.gpu_ids.split(',')
        opt.gpu_ids = []
        for str_id in str_ids:
            id = int(str_id)
            if id >= 0:
                opt.gpu_ids.append(id)
        if len(opt.gpu_ids) > 0:
            torch.cuda.set_device(opt.gpu_ids[0])

        self.opt = opt
        return self.opt
