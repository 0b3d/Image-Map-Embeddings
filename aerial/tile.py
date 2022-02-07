import os
import cv2 
import math
import random
import numpy as np
import pandas as pd 

# TMS functions taken from https://alastaira.wordpress.com/2011/07/06/converting-tms-tile-coordinates-to-googlebingosm-tile-coordinates/ #spellok
def tms(ytile, zoom):
    n = 2.0 ** zoom
    ytile = n - ytile - 1
    return int(ytile)


# Math functions taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames #spellok
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


# Math functions taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames #spellok
def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

class Tile():
    """A class for Slippy map tiles"""

    def __init__(self, coords, dataroot, aerial_dir=None):
        """
        Initialize the class Tile

        Parameters:
            coords -> A tuple with the coordinates and zoom level (x,y,z).
                      It accept both "lat, lon"  based coordinates or "x, y" grid coordinates of tile.
        
        """

        if type(coords[0]) == int and type(coords[1]) == int:
            self.x, self.y, self.z = coords
            self.vertex = num2deg(self.x, self.y, self.z)    # These are coordinates of top left vertex
            next_lat, next_lon = num2deg(self.x+1, self.y+1, self.z)
            self.centre = ( (self.vertex[0] + next_lat)/2 ,  (self.vertex[1] + next_lon)/2 )
            self.point_lat, self.point_lon = self.centre
        else:
            self.point_lat, self.point_lon, self.z = coords
            self.x, self.y = deg2num(self.point_lat, self.point_lon, self.z)
            self.vertex = num2deg(self.x, self.y, self.z)
            next_lat, next_lon = num2deg(self.x+1, self.y+1, self.z)
            self.centre = ( (self.vertex[0] + next_lat)/2 ,  (self.vertex[1] + next_lon)/2 )
    
        self.extent = [next_lat, self.vertex[1], self.vertex[0], next_lon] # Top, left, bottom, rigth
        self.aerial_dir = 'aerial_tiles' if aerial_dir is None else aerial_dir
        self.dataroot = dataroot

    def set_zoom(self, zoom):
        """ Set tile zoom and update tile metacoordinates """
        self.z = zoom
        self.x, self.y = deg2num(self.point_lat, self.point_lon, self.z)
        self.vertex = num2deg(self.x, self.y, self.z)
        next_lat, next_lon = num2deg(self.x+1, self.y+1, self.z)
        self.centre = ( (self.vertex[0] + next_lat)/2 ,  (self.vertex[1] + next_lon)/2 )

    def get_path(self, domain='aerial'):
        if domain == 'aerial':
            path = os.path.join(self.dataroot, self.aerial_dir, str(self.z), str(self.x), str(self.y) + '.jpg')
        else:
            path = os.path.join(self.dataroot, 'map_tiles', str(self.z), str(self.x), str(self.y) + '.png')
        return path

    def get_tile(self, domain='aerial'):
        if domain == 'aerial':
            path = os.path.join(self.dataroot, self.aerial_dir, str(self.z), str(self.x), str(self.y) + '.jpg')
        else:
            path = os.path.join(self.dataroot, 'map_tiles', str(self.z), str(self.x), str(self.y) + '.png')
        return cv2.imread(path)

    def get_tile_with_info(self, domain='aerial', size=256, colour=(255,255,255), text=True):
        """ Get tiles with index and zoom labels"""
        thick = int(0.05 * size) # Thickness is 5 % of size
        tile = self.get_tile(domain=domain) 
        tile = cv2.resize(tile, (size, size))
        tile = cv2.copyMakeBorder(tile, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, colour)
        if text == True:
            text = 'Tile: {},{},{}'.format(self.x, self.y, self.z) 
            cv2.putText(tile, text, (10,size), cv2. FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1, cv2.LINE_AA)
        return tile

    def show(self, domain='both'):
        if domain == 'both':
            map = self.get_tile_with_info(domain='map')
            image = self.get_tile_with_info(domain='aerial')
            img = np.concatenate([map, image], axis=1)
        else:
            img = self.get_tile_with_info(domain=domain)
        cv2.imshow('Tile', img)
        cv2.waitKey(0)


class MetaTile():
    """ This class abstracts a tile centered at any given coordinate. It is produced by concatenating, croping and rotating the required tiles from the grid"""
    
    def __init__(self, coords, dataroot, aerial_dir = None):
        """ Initialize class MetaTile 
        
            Parameters: 
                coords -> A tuple with centre coordinates and desired zoom level (lat, lon, zoom)
        """
        self.coords = coords
        self.lat, self.lon, self.z = coords 
        self.centre_tile = Tile(self.coords, dataroot, aerial_dir) 
        self.aerial_dir = aerial_dir
        self.dataroot = dataroot
        
    
    def get_metatile(self, domains=['aerial','map'], rotation=0.0, scale=1.0, flip=None, blur=False, text=None, outSize=256):
        point = self.coords[0:2]     
        centre_tile = Tile(self.coords, self.dataroot, self.aerial_dir)              
        
        for domain in domains: 
            path = centre_tile.get_path(domain)
            assert os.path.isfile(path), "Tile {} does not exist".format(path) 
        
        delta =  (centre_tile.extent[2] - centre_tile.extent[0], centre_tile.extent[3] - centre_tile.extent[1]) # in wgs84
        shift_lat = -1 * (point[0] - centre_tile.vertex[0])
        shift_lon = point[1] - centre_tile.vertex[1]
        point_coords = (int(round(shift_lon / delta[1] * 256)), int(round(shift_lat / delta[0] * 256))) #x,y
        new_centre = (point_coords[0]+256,point_coords[1]+256)

        images = []

        for domain in domains:
            tile_list = []
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    coords = (centre_tile.x+i, centre_tile.y+j, centre_tile.z)
                    tile = Tile(coords, self.dataroot, self.aerial_dir).get_tile(domain)
                    if tile is None:
                        tile = np.zeros((256,256,3), dtype=np.uint8)
                    tile_list.append(tile)
            column = np.concatenate(tile_list, axis=0)
            parent = np.hstack(np.split(column,3,0))

            if rotation != 0.0:
                rot_mat = cv2.getRotationMatrix2D((new_centre[0],new_centre[1]), np.rad2deg(rotation), scale)
                parent = cv2.warpAffine(parent, rot_mat, parent.shape[1::-1], flags=cv2.INTER_LINEAR)
            tile = parent[(new_centre[1]-outSize//2):(new_centre[1]+outSize//2),(new_centre[0]-outSize//2):(new_centre[0]+outSize//2),:]

            if flip is not None:
                tile = cv2.flip(tile, flip)

            if blur:
                ksize = random.choice([None,3])
                if ksize is not None:
                    tile = cv2.GaussianBlur(tile,(ksize,ksize),cv2.BORDER_DEFAULT)

            if text is not None:
                cv2.putText(tile, text, (10,20), cv2. FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1, cv2.LINE_AA)

            images.append(tile)

        return images

    def show(self,outSize=256):
        images = self.get_metatile(domains=['aerial', 'map'],outSize=outSize)
        tile = np.concatenate(images, axis=1)
        cv2.imshow('Tile', tile)
        cv2.waitKey(0)

if __name__ == "__main__":
    lat, lon, zoom =   51.7852587, -1.27647400, 18
    rotation, scale, flip = 200, 1.0, None
    dataroot = os.path.join(os.environ['DATASETS'],'digimap_data')
    print(dataroot)
    metatile = MetaTile((lat,lon,zoom), dataroot=dataroot)
    images = metatile.get_metatile(domains=['aerial','map'], rotation=rotation)
    tile = np.concatenate(images, axis=1)
    cv2.imshow('Tile', tile)
    cv2.waitKey(0)  
