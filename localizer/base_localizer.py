
import torch
import random
import numpy as np

from abc import ABC, abstractmethod


class BaseLocalizer(ABC):
    def __init__(self, opt):
        self.opt = opt
        if self.opt.seed >= 0:
            np.random.seed(opt.seed) 
            random.seed(opt.seed)
            torch.manual_seed(opt.seed)
            torch.backends.cudnn.deterministic = True
            torch.cuda.manual_seed(opt.seed)
                
    @staticmethod
    def modify_commandline_options(parser, is_train):
        """Add new dataset-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.
        """
        return parser

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def localize(self):
        pass
    
    @abstractmethod
    def set_model(self,model):
        pass
    