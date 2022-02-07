import torch
import numpy as np

dtype = torch.cuda.FloatTensor
dtype_long = torch.cuda.LongTensor

def trilinear_interpolation_numpy(descriptor_grid, y, x, t):
    H,W,_,_ = descriptor_grid.shape

    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    t0 = np.floor(t).astype(int) % 8

    x1 = x0 + 1
    y1 = y0 + 1
    t1 = (t0 + 1) % 8

    # Clip values
    y0 = np.clip(y0,0,H-1)
    x0 = np.clip(x0,0,W-1)
    y1 = np.clip(y1,0,H-1)
    x1 = np.clip(x1,0,W-1)

    yd = np.expand_dims((y - y0),1)   
    xd = np.expand_dims((x - x0),1)   
    td = np.expand_dims((t - t0),1)   

    xdc = 1 - xd    
    ydc = 1 - yd    
    tdc = 1 - td    

    # Interpolate in y direction
    c00 = descriptor_grid[y0,x0,t0]*ydc + descriptor_grid[y1,x0,t0]*yd 
    c01 = descriptor_grid[y0,x0,t1]*ydc + descriptor_grid[y1,x0,t1]*yd 
    c10 = descriptor_grid[y0,x1,t0]*ydc + descriptor_grid[y1,x1,t0]*yd 
    c11 = descriptor_grid[y0,x1,t1]*ydc + descriptor_grid[y1,x1,t1]*yd 

    # Interpolate in x direction
    c0 = c00*xdc + c10*xd 
    c1 = c01*xdc + c11*xd 

    #Interpolate in t direction
    c = c0*tdc + c1*td  

    # Normalize descriptors 
    norm = np.linalg.norm(c,axis=1,keepdims=True)
    descriptors = c / norm
    return descriptors

def trilinear_interpolation_torch(descriptor_grid, y, x, t):
    H,W,_,_ = descriptor_grid.shape
    
    x0 = torch.floor(x).long()
    y0 = torch.floor(y).long()
    t0 = torch.floor(t).long() % 8

    x1 = x0 + 1
    y1 = y0 + 1
    t1 = (t0 + 1) % 8

    # Clip values
    y0 = torch.clamp(y0,0,H-1)
    x0 = torch.clamp(x0,0,W-1)
    y1 = torch.clamp(y1,0,H-1)
    x1 = torch.clamp(x1,0,W-1)

    yd = (y - y0.float()).view(-1,1)   
    xd = (x - x0.float()).view(-1,1)   
    td = (t - t0.float()).view(-1,1)

    xdc = 1 - xd    
    ydc = 1 - yd    
    tdc = 1 - td    

    # Interpolate in y direction
    c00 = descriptor_grid[y0,x0,t0]*ydc + descriptor_grid[y1,x0,t0]*yd 
    c01 = descriptor_grid[y0,x0,t1]*ydc + descriptor_grid[y1,x0,t1]*yd 
    c10 = descriptor_grid[y0,x1,t0]*ydc + descriptor_grid[y1,x1,t0]*yd
    c11 = descriptor_grid[y0,x1,t1]*ydc + descriptor_grid[y1,x1,t1]*yd 

    # Interpolate in x direction
    c0 = c00*xdc + c10*xd 
    c1 = c01*xdc + c11*xd 

    #Interpolate in t direction
    c = c0*tdc + c1*td  

    # Normalize descriptors 
    norm = torch.norm(c,dim=1, keepdim=True)
    descriptors = c / norm
    return descriptors
