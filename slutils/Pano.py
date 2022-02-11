import os, sys 
import numpy as np 
import cv2
import pandas as pd
from slutils.equirec2perspec import Equirec2Perspec as E2P

class Pano():
    """ Create object panorama"""
    
    def __init__(self, panoDir, ID):
        """Initialize the Pano class.

        Parameters:
            panoDir (str)   -- Path to the directory where panoramas are stored. Example os.path.join( os.environ['DATASETS'],'streetlearn', 'jpegs_manhattan_2019')
            ID (str or int) -- If ID is a string it should be the name of the panorama file (Example PreXwwylmG23hnheZ__zGw.jpg)
                            -- If ID is an integer it will be intewrpreted as the global index of the location. According to the nodes.txt file 

        """

        self.panoDir = panoDir
        
        if type(ID) is str:
            self.panoName = ID
        
        elif type(ID) is int:
            filename = os.path.join( self.panoDir, 'nodes.txt' )
            names = ["pano_id", "yaw", "lat", "lon"]
            frame = pd.read_csv(filename, names=names)
            pano_id = frame.loc[ID, 'pano_id']
            self.panoName = pano_id + '.jpg'
        else:
            raise Exception("Pano ID not found")

        self.path = self.getPath()
        self.pano = self.getPano()
        self.shape = self.pano.shape

    def getPath(self):
        path = os.path.join( self.panoDir, self.panoName)
        return path

    def getPano(self, size=None, flip=False):
        assert os.path.isfile(self.path), "Pano {} was not found".format(self.path) 
        pano = cv2.imread(self.path)
        if size is not None:
            pano = cv2.resize(pano, size)
        if flip:
            pano = cv2.flip(pano, 1)
        return pano
    
    def showPano(self):
        cv2.imshow(self.panoName, self.pano)
        cv2.waitKey(0)

    def getZoom(self):
        """Returns pano's zoom level"""
        return int(np.ceil(self.pano.shape[0] / 512))

    def getSnaps(self, size=224, mode='list', rotation=0.0, flip=False, noise=False):
        """ Returns panorama snaps
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
            

    def getSnapswithInfo(self, size=224, colour = (255,255,255), text=None):
        """ Returns a list with snaps in directions 0, 90, -90, 180"""
        H, W = size if hasattr(size,'__iter__') else (size,size)
        thick = int(0.05 * H) # Thickness is 5 % 
        snaps = self.getSnaps(size)
        snaps = [cv2.copyMakeBorder(snap, thick,thick,thick,thick, cv2.BORDER_CONSTANT, None, colour) for snap in snaps] 
        directions = ['F', 'L', 'R', 'B']
        if text is not None:
            for i, direction in enumerate(directions):
                txt = 'ID: ' + text + ' ' + direction
                cv2.putText(snaps[i], txt, (10,size), cv2. FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1, cv2.LINE_AA)
        return snaps 

    def cropPano(self, fov, theta, pitch, h, w):
        """ Returns a pano the the specified parameters"""
        equ = E2P.Equirectangular(self.pano)
        snap = equ.GetPerspective(fov, theta, pitch, h, w)
        return snap

    def saveSnaps(self, size=224, directory=None, option='group'):
        savedir = os.getcwd() if directory == None else directory
        basename = os.path.join(savedir, self.panoName.split('.')[0]) 

        if option == 'group':
            snaps = self.getSnapswithInfo(size=size, text=None)
            row1 = np.concatenate([snaps[0], snaps[2]], axis=1) # FR
            row2 = np.concatenate([snaps[3], snaps[1]], axis=1) # BL
            image = np.concatenate([row1, row2], axis=0)
            filename = basename + '.jpg'
            cv2.imwrite(filename, image)    

        elif option == 'individual':
            snaps = self.getSnapswithInfo(size=size, text=None)
            directions = ['F', 'L', 'R', 'B']
            for i, snap in enumerate(snaps):
                direction = directions[i]
                filename = basename + '_' + direction + '.jpg'
                cv2.imwrite(filename, snap)
        else:
            print("Option not found, image not saved")

    def getCoordinates(self):
        filename = os.path.join( self.panoDir, 'nodes.txt' )
        names = ["pano_id", "yaw", "lat", "lon"]
        frame = pd.read_csv(filename, names=names)
        row = frame.loc[frame['pano_id'] == self.panoName.split('.')[0]]
        index = row.index[0]
        yaw, lat, lon = row['yaw'].values[0], row['lat'].values[0], row['lon'].values[0]
        return (index, lat, lon, yaw)

    def __str__(self):
        index, lat, lon, yaw = self.getCoordinates()
        return "Pano name: {}, index: {}, shape: {}, coordinates: ({},{},{})".format(self.panoName, index, self.pano.shape, lat, lon, yaw)

if __name__ == "__main__":

    panoDir = os.path.join( os.environ['DATASETS'],'streetlearn', 'jpegs_manhattan_2019')
    pano = Pano(panoDir, 'PreXwwylmG23hnheZ__zGw.jpg')
    snaps = pano.getSnapswithInfo(size=(256,340))
    pano.saveSnaps(size=(256,340), directory=None, option='individual')
    img = np.concatenate(snaps, axis=1)
    cv2.imshow("pano", img)
    cv2.waitKey(0)
