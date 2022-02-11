import os, sys
import numpy as np
import pandas as pd
import cv2 


class Tile():
    "A tile is a png image with matlab index ID stored in tileDir with the same name as the panorama asociated"

    def __init__(self, tileDir, ID, yaw):
        """Initialize the Tile class.

        Parameters:
            tileDir (str)   -- Path to the directory where the 'tiles' folder is stored. Example os.path.join( os.environ['DATASETS'],'streetlearn', 'jpegs_manhattan_2019')
            ID (str or int) -- If ID is a string it should be the name of the panorama file (Example PreXwwylmG23hnheZ__zGw.jpg)
                            -- If ID is an integer it will be interpreted as the global index of the location. According to the nodes.txt file 

        """
        self.tileDir = tileDir
        
        if type(ID) is str:
            self.tileName = ID
            self.yaw = yaw
        
        elif type(ID) is int:
            filename = os.path.join( self.tileDir, 'nodes.txt' )
            names = ["pano_id", "yaw", "lat", "lon"]
            frame = pd.read_csv(filename, names=names)
            pano_id = frame.loc[ID, 'pano_id']
            self.tileName = pano_id + '.png'
        
        else:
            sys.exit("Pano ID not found")
    
    def __str__(self):
        index, lat, lon, yaw = self.getCoordinates()
        return "Tile with index {} centered at ({},{}) and {} degrees of heading".format(index+1, lat, lon, yaw)

    def getCoordinates(self):
        """Get the coordinates of the tile"""
        filename = os.path.join( self.tileDir, 'nodes.txt' )
        names = ["pano_id", "yaw", "lat", "lon"]
        frame = pd.read_csv(filename, names=names)
        row = frame.loc[frame['pano_id'] == self.tileName.split('.')[0]]
        index = row.index[0]
        yaw, lat, lon = row['yaw'].values[0], row['lat'].values[0], row['lon'].values[0]
        return (index, lat, lon, yaw)
    
    def getTile(self, zoom=19, crop_size=128):
        """Returns tile image with specified zoom"""
        path = os.path.join( self.tileDir, 'z'+str(zoom), self.tileName)
        img = cv2.imread(path)
        # rotate image
        (h, w) = img.shape[:2]
        center = (w/2, h/2)
        M = cv2.getRotationMatrix2D(center, self.yaw, 1.0)
        rotate_img = cv2.warpAffine(img, M, (w, h), borderValue=(255,255,255)) 

        # center crop
        hn = crop_size
        wn = crop_size
        x = center[0] - hn/2
        y = center[1] - wn/2
        crop_img = rotate_img[int(x):int(x+hn), int(y):int(y+wn)]

        return crop_img

    def showTile(self):
        """Shows the tile and wait for a key to be pressed"""
        window_name = "({},{})".format(self.lat, self.lon)
        cv2.imshow(window_name, self.getTilewithInfo())
        cv2.waitKey(0)

    def getTilewithInfo(self, zoom=19, size=256, colour=(255,255,255), text=None):
        """ Get tiles with an index and zoom label. Also it shows an arrow to indicate heading direction"""
        thick = int(0.05 * size) # Thickness is 5 % of size
        tile = self.getTile(zoom=zoom)
        tile = cv2.resize(tile, (size, size))
        tile = cv2.copyMakeBorder(tile, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, colour)
        #text = '({},{})'.format(self.lat, self.lon)          
        if text is not None:
            txt = 'ID: {}'.format(text) #Show ID
            cv2.putText(tile, txt, (10,size), cv2. FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.arrowedLine(tile, (size//2, size//2), ((size//2, size//2 - 15)), (255,0,0), 1, cv2.LINE_4, 0, 0.4)
        return tile

if __name__ == "__main__":
    tileDir = os.path.join(os.environ['DATASETS'], 'streetlearn', 'tiles_manhattan_2019')
    tile = Tile(tileDir, 53160, 10) 
    tile.showTile()
