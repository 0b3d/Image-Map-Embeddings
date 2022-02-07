import argparse
import localizer
from .base_options import BaseOptions


class LocalizeOptions(BaseOptions):
    """This class includes test options.

    It also includes shared options defined in BaseOptions.
    """

    def initialize(self, parser):
        parser = BaseOptions.initialize(self, parser)  
        parser.set_defaults(phase='localize')

        parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        parser.add_argument('--steps', type=int, default = None, help='Number of steps')
        parser.add_argument('--visualize', action='store_true', help='If set a figure displaying current state will be produced at each step')
        parser.add_argument('--nosave', action='store_true', help='If set save experiment information')
        
        
        self.isTrain = False
        return parser