import os
import numpy as np 
import pandas as pd
import cv2 
from slutils.equirec2perspec import Equirec2Perspec as E2P

 
class Location():
    def __init__(self, index, pano_id, yaw, lat, lon, global_index, area_name, city, dataroot, zooms=[18,19]):
        
        self.index = index
        self.pano_id = pano_id
        self.global_index = global_index
        self.area_name = area_name 
        self.city = city 
        self.dataroot = dataroot 
        self.zooms = zooms 
        self.yaw = yaw 
        self.lon = lon 
        self.lat = lat
        
        panorama_path = os.path.join( dataroot, 'jpegs_' + city + '_2019', pano_id + '.jpg') 
        tile_z18_path = os.path.join( dataroot, 'tiles_' + city + '_2019','z18', str(global_index).zfill(5) + '.png')
        tile_z19_path = os.path.join( dataroot, 'tiles_' + city + '_2019','z19', str(global_index).zfill(5) + '.png') 

        if 18 in zooms:
            assert os.path.isfile(tile_z18_path), "Tile {} not found".format(tile_z18_path)
            self.tile_z18 = cv2.imread(tile_z18_path) 
            self.tile_z18_path = tile_z18_path
        
        if 19 in zooms:
            assert os.path.isfile(tile_z19_path), "Tile {} not found".format(tile_z19_path)
            self.tile_z19 = cv2.imread(tile_z19_path) 
            self.tile_z19_path = tile_z19_path

        assert os.path.isfile(panorama_path), "Panorama {} not found".format(panorama_path)
        self.pano = cv2.imread(panorama_path) 
        self.pano_path = panorama_path

    # ---- Tile methods ----

    def get_tile(self, size=None, zoom=18, rotation=0, flip=False):
        """Returns tile image with specified zoom"""

        if zoom == 18:
            img = self.tile_z18
        elif zoom == 19:
            img = self.tile_z19
        else:
            raise Exception("Invalid tile zoom value")

        if size is not None:
            if type(size) == int:
                W, H = size, size
            else:
                W, H = size
        else:
            H, W, _ = img.shape

        try:
            oH, oW, C = img.shape # original tile size
        except:
            raise Exception("Problem getting the shape of tile {}".format(self.tileName))

        if rotation is not None and rotation!=0:
            (h, w) = img.shape[:2]
            center = (w / 2, h / 2) 
            M = cv2.getRotationMatrix2D(center, rotation, 1.0)
            img = cv2.warpAffine(img, M, (w, h)) 
        
        if flip:
            img = cv2.flip(img, 1)
        
        if H != oH or W != oW:
            img = cv2.resize(img, (W,H))

        return img

    def show_tile(self):
        """Shows the tile and wait for a key to be pressed"""
        cv2.imshow('Tile', self.get_tile_with_info())
        cv2.waitKey(0)
        cv2.destroyWindow('Tile')

    def get_tile_with_info(self, zoom=18, size=256, colour=(255,255,255), text=None):
        """ Get tiles with an index and zoom label. Also it shows an arrow to indicate heading direction"""
        thick = int(0.05 * size) # Thickness is 5 % of size
        tile = self.get_tile(zoom=zoom)
        tile = cv2.resize(tile, (size, size))
        tile = cv2.copyMakeBorder(tile, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, colour)
        
        if text is not None:
            txt = 'ID: {}'.format(text) #Show ID
            cv2.putText(tile, txt, (10,size), cv2. FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1, cv2.LINE_AA)
        
        cv2.arrowedLine(tile, (size//2, size//2), ((size//2, size//2 - 15)), (255,0,0), 1, cv2.LINE_4, 0, 0.4)
        
        return tile

    # ---- Panorama methods ----

    def show_pano(self):
        cv2.imshow('Panorama', self.pano)
        cv2.waitKey(0)

    def get_zoom(self):
        """Returns pano's zoom level"""
        return int(np.ceil(self.pano.shape[0] / 512))

    def get_snaps(self, size=224, mode='list', rotation=0.0, flip=False, noise=False):
        """ Returns panorama snapshots
            Parameters:
                size (int) -> Snaps tile size
                mode (str) -> Indicates snaps returned format grid|list
                rotation (float) -> Yaw rotation angle
                flip (bool) -> Indicates whether a vertical flip to the panorama will be made before crop
                noise -> Add random noise to the cropping parameters (fov, pitch and tetha)  
                
                
            Returns ->
                if mode is 'list', it will return a list of snaps in the directions [0,-90,90,180] (F,L,R,B) w.r.t yaw angle.
                if mode is 'grid', it will return an image with snaps concatenated in a grid [F,B
                                                                                              L,R]
        """
        snaps = []
        equ = E2P.Equirectangular(self.pano)
        
        views = [0,-90,90,180] 
        
        if noise:
            fov_shift = np.random.normal(loc=0, scale=10)
            pitch_shift = np.random.normal(loc=0,scale=10)
            tetha_shift = np.random.normal(loc=0,scale=10)

        else:
            fov_shift = 0
            pitch_shift = 0
            tetha_shift = 0        

        H, W = size if hasattr(size,'__iter__') else (size,size)
        tetha_shift = tetha_shift + rotation    
        snaps = [equ.GetPerspective(100+fov_shift, t+tetha_shift, pitch_shift, H, W) for t in views]
        
        if mode == 'list' and not flip:
            return snaps
        
        elif mode == 'list' and flip:
            new_list = [cv2.flip(snaps[i], 1) for i in [0,2,1,3]] # flip snaps 
            return new_list 

        elif mode == 'grid' and not flip:    
            row1 = np.concatenate([snaps[0], snaps[3]], axis=1) # Concatenate F and B
            row2 = np.concatenate([snaps[1], snaps[2]], axis=1) # Concatenate L and R
            img = np.concatenate([row1, row2], axis=0) # [F,R;L,R]
            return img 
        
        elif mode == 'grid' and flip:
            snaps = [cv2.flip(snap, 1) for snap in snaps]
            row1 = np.concatenate([snaps[0], snaps[3]], axis=1) # Concatenate F and B
            row2 = np.concatenate([snaps[2], snaps[1]], axis=1) # Concatenate L and R
            img = np.concatenate([row1, row2], axis=0) # [F,R;L,R]
            return img
            

    def get_snaps_with_info(self, size=224, colour = (255,255,255), text=None):
        """ Returns a list with snaps in directions 0, 90, -90, 180"""
        H, W = size if hasattr(size,'__iter__') else (size,size)
        thick = int(0.05 * H) # Thickness is 5 % 
        snaps = self.get_snaps(size)
        snaps = [cv2.copyMakeBorder(snap, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, colour) for snap in snaps] 
        directions = ['F', 'L', 'R', 'B']
        if text is not None:
            for i, direction in enumerate(directions):
                txt = 'ID: ' + text + ' ' + direction
                cv2.putText(snaps[i], txt, (10,size), cv2. FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1, cv2.LINE_AA)
        return snaps 

    def crop_pano(self, fov, theta, pitch, h, w):
        """ Returns a pano the the specified parameters"""
        equ = E2P.Equirectangular(self.pano)
        snap = equ.GetPerspective(fov, theta, pitch, h, w)
        return snap

    # ---- Location methods ----
            
    def get_location(self, pano_mode='list', zoom=18, size=224, rotation=0, flip=False, noise=False):
        images = [] 
        snaps = self.get_snaps(mode=pano_mode, rotation=rotation, size=size, flip=flip, noise=noise)
        tile = self.get_tile(size=size, zoom=zoom, rotation=rotation, flip=flip)
        if pano_mode == 'list':
            images = snaps
        else: 
            images.append(snaps)
        images.append(tile)
        return images 

    def get_location_with_info(self, zoom=18, size=224, colour=(255,255,255), text=None):
        snaps = self.get_snaps_with_info(size=size, colour=colour, text=text)
        tile = self.get_tile_with_info(zoom=zoom, size=size, colour=colour, text=text)
        snaps.append(tile)
        img = np.concatenate(snaps, axis=1)
        return img
    
    def show_location(self, block=True):
        img = self.get_location_with_info()
        cv2.imshow("Location", img)
        if block:
            cv2.waitKey(0)
            cv2.destroyWindow('Location')

    def get_neighbours(self):
        linkFile = os.path.join( self.dataroot, 'jpegs_' + self.city + '_2019', 'links.txt')
        names = ['pano_id', 'bearing', 'neighbor']
        frame = pd.read_csv(linkFile, names=names)
        subframe = frame[ frame['pano_id'] == self.pano_id ]
        neighbors = subframe['neighbor'].to_list()
        bearings = subframe['bearing'].to_list()
        return neighbors, bearings

    def __str__(self) -> str:
        return "Location in {}, index: {}".format(self.area_name, self.index)

