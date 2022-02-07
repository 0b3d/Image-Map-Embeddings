import argparse
import visualizations

class BaseOptions():
    """This class defines options used for visualization
    """

    def __init__(self):
        """Reset the class; indicates the class hasn't been initailized"""
        self.initialized = False

    def initialize(self, parser):
        """Define the common options that are used in both training and test."""
        # basic parameters
        parser.add_argument('--format', type=str, default='npz', help='Format of features file npz|mat')
        parser.add_argument('--vname', required=True, help='name of the visualizer')
        parser.add_argument('--model', type=str, default='ground', help='name of the model to visualize')
        parser.add_argument('--epoch', type=str, default='latest', help='epoch_to_load')
        parser.add_argument('--area', required=True, default='hudsonriver5k', help='area to process')
        parser.add_argument('--dataroot', required=False, help='path to dataset')
        parser.add_argument('--tile_zoom', default=18, help='Tile zoom')
        parser.add_argument('--tile_size', type=int, default=128, help='Tile size')
        parser.add_argument('--results_dir', required=False, default='./results', help='Results directory')
        parser.add_argument('--save', action='store_true', help="Save figure to results_dir")
        parser.add_argument('--fig_format', type=str, default='png', help="Save image format")
        parser.add_argument('--fig_dpi', type=int, default=300, help="Image's dpi")
        parser.add_argument('--fig_size', type=int, default=[8,6], help="Image's size in cm")
        parser.add_argument('--seed', type=int, default=442, help='Set the seed, -1 means random')


        self.initialized = True
        return parser

    def gather_options(self):
        
        if not self.initialized:  
            parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)

        opt, _ = parser.parse_known_args()

        # modify specific visualizer-related parser options
        visualizer_name = opt.vname
        model_option_setter = visualizations.get_option_setter(visualizer_name)
        parser = model_option_setter(parser)

        self.parser = parser
        return parser.parse_args()

    def print_options(self, opt):
        """Print options
        """
        message = ''
        message += '----------------- Options ---------------\n'
        for k, v in sorted(vars(opt).items()):
            comment = ''
            default = self.parser.get_default(k)
            if v != default:
                comment = '\t[default: %s]' % str(default)
            message += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
        message += '----------------- End -------------------'
        print(message)

    def parse(self):
        opt = self.gather_options()
        self.print_options(opt)
        self.opt = opt
        return self.opt
