import os
import numpy as np

from matplotlib import pyplot as plt
#import matplotlib.font_manager

from .base_visualizer import BaseVisualizer
from utils.metric_utils import rank

def _modify_model(parser, dest, value):
    for action in parser._actions:
        if action.dest == dest:
            action.nargs = value
            return
    else:
        raise AssertionError('argument {} not found'.format(dest))

class StreetRecallVisualizer(BaseVisualizer):

    @staticmethod
    def modify_commandline_options(parser):
        parser.add_argument('--city', type=str, default='manhattan', help='city')
        parser.add_argument('--direction', type=str, default='image2map', choices=("map2image","image2map","map2map","image2image"), help='Domain direction')
        parser.add_argument('--legend', type=str, nargs='+', help='legends to show in plot')
        parser.add_argument('--title', type=str, help='title to show in plot')  
        parser.add_argument('--xlim', type=float, default=2.0, help='upper x limit')  
        parser.add_argument('--samples', type=int, default=None, help='samples')  
        
        _modify_model(parser, 'model', '+') # Modify model action in parser to support a list of models
        _modify_model(parser, 'area', '+') # Modify model action in parser to support a list of models
        return parser
        

    def __init__(self, opt):
        BaseVisualizer.__init__(self, opt)
        self.opt = opt
    
    def show(self):
        #plt.style.use('./utils/an_optional_style.mplstyle')

        linestyle = 'solid'
        top1p_list = []
        for model in self.opt.model:
            for area in self.opt.area:
                source_features, target_features, _ = super().get_data(model, area)
                if self.opt.samples is None:
                    n = source_features.shape[0]  
                    indices = np.arange(0,n)
                    self.loc_ids = indices
                else:
                    n = self.opt.samples
                    indices = np.random.randint(0,source_features.shape[0],n)
                    self.loc_ids = np.arange(0,n)
                
                source_features = source_features[indices]
                target_features = target_features[indices]

                rank_ = rank(source_features,target_features,self.loc_ids,self.loc_ids)
                accuracy = np.zeros_like(rank_)

                nodes = rank_.shape[0]
                for k in range(nodes):
                    accuracy[k] = np.sum(rank_ <= k).astype(np.float)
                accuracy = accuracy / nodes
                x = (self.loc_ids / nodes)*100
                plt.plot(x,accuracy,linestyle=linestyle)

                top1 = 100*accuracy[1]
                top5 = 100*accuracy[5]
                top10 = 100*accuracy[10]

                top1p = 100*accuracy[round(0.01*nodes)]
                top1p_list.append(top1p) 
                print("Model {} Area {} Top 1 {:.3f} Top 5 {:.3f} Top 10 {:.3f} Top 1% {:.3f}".format(model, area, top1, top5, top10, top1p))
            
            linestyle = 'dashed'
            plt.gca().set_prop_cycle(None)

        if self.opt.legend is not None:
            legend = self.opt.legend
        else:
            legend = self.opt.model
        
        legend = ['{} ({:.1f} %)'.format(legend[i], top1p_list[i]) for i in range(len(legend))]

        if self.opt.title is not None:
            plt.title(self.opt.title)

        plt.margins(x=0,y=0)
        plt.xlim([0, self.opt.xlim]) 
        plt.xlabel("k (% of the dataset)")
        plt.ylabel("Top-k% recall")
        plt.legend(legend)
        plt.grid()
        
        if self.opt.save:
            filename = '{}_{}_{}_{}.{}'.format(self.opt.vname, self.opt.model, self.opt.area, self.opt.tile_zoom, self.opt.fig_format)
            path = os.path.join('temp', filename)
            super().savefig(path)
            
        plt.show()


    def print_info(self):
        print('Source domain ', self.source_domain)
        print('Target domain ', self.target_domain)



