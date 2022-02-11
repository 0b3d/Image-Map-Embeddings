import os, sys
import numpy as np 
import pandas as pd
import cv2 
from slutils.Pano import Pano

class LocationP(Pano):
    def __init__(self, dataset, ID, city, HD, theta_init=0, base_index='local', tile_style='s2v'):
        """ Initialize the Location class. It inherits from Tile and Pano classes.

        Parameters:
            dataset (str)   -- Name of the data set where location is. Example wallstreet5k
            ID (str or int) -- If ID is a string it should be the name of the panorama file asociated with the location (Example PreXwwylmG23hnheZ__zGw.jpg)
                            -- If ID is an integer and base_index is 'local' it will be intewrpreted as the local index of the location. 
                               According to the csv file asociated to that dataset. Range [1,5000] for (5k datasets)
                            -- If ID is an integer and base_index is 'global' it will be intewrpreted as the global index of the location. 
                               According to the nodes.txt file asociated to that dataset. Range [1,113767] 
                               (location index must be part of dataset)
            city (str)      -- Name of the city to work with (newyork, pittsburgh)
            base_index (str)-- Whether index is a 'local' or 'global' index.
            tile_style (str)-- The style of tiles to use "s2v|s2v_heigth"
        """
        self.datasetPath = os.path.join( os.environ['DATASETS'], dataset)
        self.city = city
        
        panoDir = os.path.join( self.datasetPath) # pano Directory
        
        if type(ID) is str:
            pano_id = ID
            yaw = HD # heading angle
        
        elif type(ID) is int and base_index == 'global':
            filename = os.path.join( panoDir, 'nodes.txt' )
            names = ["pano_id", "yaw", "lat", "lon"]
            frame = pd.read_csv(filename, names=names)
            pano_id = frame.loc[ID, 'pano_id']
            yaw = frame.loc[ID, 'yaw']

        elif type(ID) is int and base_index == 'local':
            filename = os.path.join( 'slutils', 'metadata', dataset + '.csv' )
            frame = pd.read_csv(filename)
            pano_id = frame.loc[ID, 'pano_id']
            yaw = frame.loc[ID, 'yaw']
        
        else:
            sys.exit("Pano ID not found")
                   
        Pano.__init__(self, panoDir, pano_id + '.jpg')
        self.pano_id = pano_id

if __name__ == "__main__":
    loc = LocationP("hudsonriver5k", 4000, 'manhattan', base_index='global')
    print(loc)
