from .base_options import BaseOptions
from utils.util import modify_parser

class PredictOptions(BaseOptions):
    """This class includes test options.

    It also includes shared options defined in BaseOptions.
    """

    def initialize(self, parser):
        parser = BaseOptions.initialize(self, parser)  
        parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        parser.set_defaults(serial_batches=True, phase='predict') 
        modify_parser(parser,'area','nargs','+')
        self.isTrain = False
        return parser