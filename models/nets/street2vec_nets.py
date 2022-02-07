import os 
import torch
import torch.nn as nn
import torch.nn.functional as F
from models.nets.resnet_nets import resnet50
from models.nets.resnet_nets import resnet18
from models.nets.utils import init_net

class EmbNetY(nn.Module):
    def __init__(self, opt, l2_normalize = True, scale=3):
        super(EmbNetY, self).__init__()       

        if opt.panorama_mode == 'list':
            inSize = (opt.pano_size//32)**2*512*4
        elif opt.panorama_mode == 'pano':
            inSize = (opt.pano_size//32)**2*512*2
        else:
            inSize = (opt.pano_size//32)**2*512

        self.opt = opt
        self.relu = nn.ReLU(inplace=False)
        self.sm = nn.Softsign()
        self.yfc1 = nn.Linear(inSize, 1024)
        self.yfc2 = nn.Linear(1024,opt.embedding_dim)
        self.ybn1 = nn.BatchNorm1d(num_features=inSize)
        self.ybn2 = nn.BatchNorm1d(num_features=1024)
        self.ybn3 = nn.BatchNorm1d(num_features=opt.embedding_dim)

    def forward(self,y):
        y = self.ybn1(y)
        y = self.relu(y)
        y = self.yfc1(y)
        y = self.ybn2(y)        
        y = self.relu(y)
        y = self.yfc2(y)

        if not self.opt.no_l2_norm:
            y_norm = y.norm(p=2, dim=1, keepdim=True)
            y_l2_normalized = y.div(y_norm)
            return self.opt.scale * y_l2_normalized
        
        else:
            return y

class EmbNetX(nn.Module):
    def __init__(self, opt, l2_normalize = True, scale=3):
        super(EmbNetX, self).__init__()       
        inSize = 512*(opt.tile_size//32)**2

        self.opt = opt
        self.relu = nn.ReLU(inplace=False)
        self.sm = nn.Softsign()
        self.xfc1 = nn.Linear(inSize, 512)
        self.xfc2 = nn.Linear(512,opt.embedding_dim)
        self.xbn1 = nn.BatchNorm1d(num_features=inSize)
        self.xbn2 = nn.BatchNorm1d(num_features=512)
        self.xbn3 = nn.BatchNorm1d(num_features=opt.embedding_dim)

    def forward(self,x):
        x = self.xbn1(x)
        x = self.relu(x)        
        x = self.xfc1(x)
        x = self.xbn2(x)
        x = self.relu(x)
        x = self.xfc2(x)

        if not self.opt.no_l2_norm:
            x_norm = x.norm(p=2, dim=1, keepdim=True)
            x_l2_normalized = x.div(x_norm)

            return self.opt.scale * x_l2_normalized
        else:
            return x

def define_netX(opt):
    """ Define the feature extractor for panoramas, based on Resnet50
        
        Returns:
            Resnet18 with imagenet weights
    """

    net = resnet18(pretrained=True)
    if len(opt.gpu_ids) > 0:
        assert(torch.cuda.is_available())
        net.to(opt.gpu_ids[0])
        net = torch.nn.DataParallel(net, opt.gpu_ids)  # multi-GPUs
    return net


def define_netY(opt):
    """ Define the feature extractor for panoramas, based on Resnet50
        
        Returns:
            Resnet50 with places weights
    """

    net = resnet50()
    
    # Load weights
    model_file = 'resnet50_places365.pth.tar'
    if not os.access(model_file, os.W_OK):
        weight_url = 'http://places2.csail.mit.edu/models_places365/' + model_file
        os.system('wget ' + weight_url)
    checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}

    net.load_state_dict(state_dict, strict=False)

    if len(opt.gpu_ids) > 0:
        assert(torch.cuda.is_available())
        net.to(opt.gpu_ids[0])
        net = torch.nn.DataParallel(net, opt.gpu_ids)  # multi-GPUs

    return net

def define_netEMBX(opt):
    """ Define embedding network """
    net = EmbNetX(opt)
    net = init_net(net, opt.init_type, opt.init_gain, opt.gpu_ids)
    return net

def define_netEMBY(opt):
    """ Define embedding network """
    net = EmbNetY(opt)
    net = init_net(net, opt.init_type, opt.init_gain, opt.gpu_ids)
    return net

