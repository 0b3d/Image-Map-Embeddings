import os
import cv2
import numpy as np 

from aerial.tile import Tile, deg2num, num2deg
from utils.util import haversine


def get_area_extents():
    areas = {
        'London_test' : [51.4601825, -0.1282832, 51.5477509, -0.0544434],
        'SP50NW':  [51.7414809, -1.2772553, 51.7859644, -1.2040581],
        'ST57SE2014' : [51.4272088, -2.6486388, 51.4725403, -2.5772934 ],
        'ST57SE2016' : [51.4272088, -2.6486388, 51.4725403, -2.5772934 ],
        'ST57SE2017' : [51.4272088, -2.6486388, 51.4725403, -2.5772934 ]
    }
    return areas

def get_aerial_directory(areaname):
    directories = {
        'London_test' : 'aerial_tiles',
        'SP50NW':  'aerial_tiles',
        'ST57SE2014' : 'ST57SE_aerial_tiles_2014',
        'ST57SE2016' : 'ST57SE_aerial_tiles_2016',
        'ST57SE2017' : 'aerial_tiles'
    }
    return directories[areaname]

def get_readable_name(areaname):
    areas = {
        'London_test' : 'London',
        'SP50NW':  'Oxford',
        'ST57SE2014' : 'Bristol 2014',
        'ST57SE2016' : 'Bristol 2016',
        'ST57SE2017' : 'Bristol 2017'
    }
    return areas[areaname]

class Area():
    def __init__(self, name, dataroot, results_dir, extent=None, zoom=18):
        self.name = name 
        self.dataroot = dataroot
        self.results_dir = results_dir
        self.zoom = zoom
        self.dir = get_aerial_directory(name)
        self.readable_name = get_readable_name(name)

        total_extent_of_the_area = get_area_extents()[name]
        self.totalbbox = total_extent_of_the_area

        if extent is None:
            # Remove 5% in edges
            strip_lat = 0.05*(total_extent_of_the_area[2] - total_extent_of_the_area[0])
            strip_lon = 0.05*(total_extent_of_the_area[3] - total_extent_of_the_area[1])
            extent_without_edges = [total_extent_of_the_area[0]+strip_lat, 
                        total_extent_of_the_area[1]+strip_lon, 
                        total_extent_of_the_area[2]-strip_lat, 
                        total_extent_of_the_area[3]-strip_lon] 
        else:
            extent_without_edges = extent

        self.workingbbox = extent_without_edges
        self.world_size_x = haversine(extent_without_edges[0],
                                      extent_without_edges[1],
                                      extent_without_edges[0],
                                      extent_without_edges[3])

        self.world_size_y = haversine(extent_without_edges[0],
                                      extent_without_edges[1],
                                      extent_without_edges[2],
                                      extent_without_edges[1])

        self.arcllat = self.workingbbox[2]-self.workingbbox[0]
        self.arcllon = self.workingbbox[3]-self.workingbbox[1]

        # Define an inner boundary where the robot should start to turn
        strip_lat = 0.10*(extent_without_edges[2] - extent_without_edges[0])
        strip_lon = 0.10*(extent_without_edges[3] - extent_without_edges[1])        
        innerbbox = [extent_without_edges[0]+strip_lat, 
                  extent_without_edges[1]+strip_lon, 
                  extent_without_edges[2]-strip_lat, 
                  extent_without_edges[3]-strip_lon] 

        self.innerbbox = innerbbox

    def get_routes(self, seed=440):
        path = os.path.join('aerial','routes', self.name + '_' + str(seed) + '.npz')
        routes = np.load(path)['routes']
        return routes

    def get_commands(self, seed=440):
        path = os.path.join('aerial', 'routes', self.name + '_' + str(seed) + '.npz')
        routes = np.load(path)['commands']
        return routes

    def get_working_bbox_in_tile_coordinates(self):
        extent =self.workingbbox
        xmin, ymin = deg2num(extent[2],extent[1],self.zoom)
        xmax, ymax = deg2num(extent[0],extent[3],self.zoom)
        return [ymin, xmin, ymax, xmax]

    def get_total_bbox_in_tile_coordinates(self):
        extent =self.totalbbox
        xmin, ymin = deg2num(extent[2],extent[1],self.zoom)
        xmax, ymax = deg2num(extent[0],extent[3],self.zoom)
        return [ymin, xmin, ymax, xmax]

    def get_area_size_in_tiles(self):
        ymin, xmin, ymax, xmax = self.get_working_bbox_in_tile_coordinates()
        W = xmax - xmin + 1
        H = ymax - ymin + 1 
        return (H,W)

    def get_arclength(self):
        arcllat = self.workingbbox[2]-self.workingbbox[0]
        arcllon = self.workingbbox[3]-self.workingbbox[1]
        return (arcllat,arcllon)

    def get_tile_coords(self):
        coords = []
        tile_zooms = [self.zoom]    
        for z in tile_zooms:
            x = np.arange(self.xmin,self.xmax+1,1)
            y = np.arange(self.ymin,self.ymax+1,1) 
            x = np.tile(x,self.H)
            y = np.repeat(y,self.W)
            z = np.tile(z,self.H*self.W)
            grid = np.stack([x,y,z],1)
            coords.append(grid)
        coords = np.concatenate(coords, 0)
        return coords

    def get_map_grid_for_mpl(self):
        ymin, xmin, ymax, xmax = self.get_working_bbox_in_tile_coordinates()
        max_lat, min_lon = num2deg(xmin, ymin, self.zoom)
        min_lat, max_lon = num2deg(xmax+1,ymax+1, self.zoom)
        grid = [min_lon,max_lon,min_lat,max_lat]
        return grid

    def get_map(self, style='ordnance',filepath=None):
        if filepath is None:
            filename = os.path.join('aerial','maps',self.name + '_' + style + '.png') 
        else:
            filename = filepath  
        area_map = cv2.imread(filename)
        if area_map is None:
            raise FileExistsError(filename)
        return area_map
            
    def create_area_map(self, H, W, save=False, name=None):
        area_map = []
        ymin, xmin, ymax, xmax = self.get_working_bbox_in_tile_coordinates()
        for i in range( ymin, ymax+1):
            row = []
            for j in range(xmin, xmax+1):
                coords = (int(j),int(i), self.zoom)
                mapa = Tile(coords, self.dataroot).get_tile(domain='map')
                #mapa = cv2.resize(mapa,(64,64))
                row.append(mapa)

            row = np.concatenate(row,1)
            area_map.append(row)
            
        area_map = np.concatenate(area_map, axis=0)
        area_map = cv2.resize(area_map,(W,H))
        if save:
            map_name = self.name + '_ordnance.png' if name is None else name
            cv2.imwrite(os.path.join('aerial','maps', map_name), area_map)
        return area_map

    def m2deg(self, disp_in_meters):
        arclengthlat = disp_in_meters[0] * self.arcllat / (1000*self.world_size_y)
        arclengthlon = disp_in_meters[1] * self.arcllon / (1000*self.world_size_x)
        return (arclengthlat, arclengthlon)

    def get_map_descriptors(self, model, epoch='latest'):
        dataFilename = os.path.join( self.results_dir, model, epoch + '_' + self.name + '_z_' + str(self.zoom) + '.npz')
        descriptors = np.load(dataFilename)['X']
        area_coords = np.load(dataFilename)['coords'] 

        # Take descriptors of the subarea only
        ymin, xmin, ymax, xmax = self.get_working_bbox_in_tile_coordinates()

        indices_x = np.arange( xmin , xmax + 1 ) - area_coords[0,:,0,3].min()
        indices_y = np.arange( ymin , ymax + 1 ) - area_coords[:,0,0,2].min()

        indices_x = np.expand_dims(indices_x,0).astype(int)
        indices_y = np.expand_dims(indices_y,1).astype(int)      
        descriptors = descriptors[indices_y,indices_x]   
        working_coords = area_coords[indices_y,indices_x]

        return (descriptors, working_coords)

    def show(self):
        area_map = self.get_map(1280, 720)
        cv2.imshow(self.name, area_map)
        cv2.waitKey(0)
    
if __name__ == "__main__" :
    dataroot = os.path.join(os.environ['DATASETS'],'digimap_data')
    area = Area('ST57SE', dataroot)
    mymap = area.create_area_map(512,512)
    cv2.imshow('mymap', mymap)
    cv2.waitKey(0)
    cv2.destroyWindow('mymap')