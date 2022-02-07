import numpy as np 
from aerial.tile import deg2num, num2deg
from math import sqrt

def deg2num_rect(extent, zoom=18):
    x_min, y_min = deg2num(extent[2],extent[1], zoom)
    x_max, y_max = deg2num(extent[0],extent[3], zoom)
    return [x_min, y_min,x_max, y_max]

def get_XY_size(extent, zoom=18):
    XYextent = deg2num_rect(extent, zoom)
    H = XYextent[3] - XYextent[1]
    W = XYextent[2] - XYextent[0]
    return H,W

def get_uniform_coords_in_extent(extent, scale_factor=2, zoom=18):
    H, W = get_XY_size(extent, zoom)
    new_H = H * scale_factor
    new_W = W * scale_factor
    lat = np.linspace(extent[2], extent[0], new_H)
    lon = np.linspace(extent[1], extent[3], new_W)
    lon = np.tile(lon,new_H)
    lat = np.repeat(lat,new_W)
    z = np.tile(zoom,new_H*new_W)
    coords = np.stack([lat,lon,z],1)
    return coords 

def get_extent(coords):
    test = coords[0][0].item()
    isXY = test.is_integer()
    if isXY: 
        min_x, min_y = coords[:,:2].min(0)
        max_x, max_y = coords[:,:2].max(0)
        z = coords[0,2].item()
        max_lat, min_lon = num2deg(min_x, min_y, z)
        min_lat, max_lon = num2deg(max_x+1, max_y+1, z)
        extent = [min_lat, min_lon, max_lat, max_lon]
    else:        
        min_lat, min_lon = coords[:,:2].min(0)
        max_lat, max_lon = coords[:,:2].max(0)
        extent = [min_lat, min_lon, max_lat, max_lon]
    return extent, isXY

def get_grid(descriptors, original_extent, working_extent, scale_factor, zoom=18): 
    area_extent_xy = deg2num_rect(original_extent, zoom)
    working_extent_xy = deg2num_rect(working_extent,zoom)
    H,W = get_XY_size(original_extent, zoom)
    new_H, new_W = H*scale_factor, W*scale_factor
    min_x = (working_extent_xy[0] - area_extent_xy[0])*scale_factor 
    min_y = (working_extent_xy[1] - area_extent_xy[1])*scale_factor
    max_x = (working_extent_xy[2] - area_extent_xy[0])*scale_factor 
    max_y = (working_extent_xy[3] - area_extent_xy[1])*scale_factor 
    descriptors = np.reshape(descriptors,(int(new_H),int(new_W),-1)) 
    descriptors = descriptors[min_y:max_y+1,min_x:max_x+1] 
    return descriptors

def get_scale_factor(original_num_elements, current_num_elements):
    return int(sqrt(current_num_elements / original_num_elements))

