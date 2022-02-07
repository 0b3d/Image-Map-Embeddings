import numpy as np 
import matplotlib.pyplot as plt 
from aerial.tile import MetaTile

class Robot():
    """ This class defines the robot """

    def __init__(self, name, area):
        self.lat = 0.0                  # robot's latitude
        self.lon = 0.0                  # robot's longitude
        self.yaw = 0.0                  # robot's orientation in radians
        
        self.vel = 5.0                  # robot's velocity in m/s
        self.acc = 0.0                  # robot's acceleration in m/s² (mean)
        self.turn_cmd = 0.0             # robot's turn command
        
        self.acc_std = 0.33             # robot's acceleration noise m/s²
        self.min_vel = 0.0              # robot's minimum velocity
        self.max_vel = 20.0             # robot's maximum velocity

        self.area = area                # Area where the robot moves

        self.reflection_flag = False    # A flag useful to reflect robot at boundaries
        self.turn_flag = False          # A flag used to smooth turns
        self.__name__ = name
        
    def set_random_initial_position(self, bbox, init_vel=5):
        self.lat = np.random.uniform(bbox[0],bbox[2])
        self.lon = np.random.uniform(bbox[1],bbox[3])
        self.yaw = np.random.uniform(0,2*np.pi)
        self.vel = init_vel
        self.acc = 0.0 
        self.turn_cmd = 0.0

    def set_noise_params(self, acc_std):
        self.acc_std = acc_std

    def set_max_min_velocities(self, min_vel, max_vel):
        self.min_vel = min_vel
        self.max_vel = max_vel

    def get_robot_state(self):
        return np.array([self.lat, self.lon, self.yaw])

    def get_motion_command(self):
        return np.array([self.vel, self.acc, self.turn_cmd])

    def move(self, time_step=1):

        innerbbox = self.area.innerbbox
        if (self.lat > innerbbox[2] or self.lat < innerbbox[0]) and not self.turn_flag:
            if (self.yaw >= 0 and self.yaw < np.pi/2) or (self.yaw >= np.pi and self.yaw < 3/2*np.pi):
                self.turn_cmd = 0.017
            else:
                self.turn_cmd = -0.017
            self.turn_flag =True

        elif (self.lon > innerbbox[3] or self.lon < innerbbox[1]) and not self.turn_flag:
            if (self.yaw >= 0 and self.yaw < np.pi/2) or (self.yaw >= np.pi and self.yaw < 3/2*np.pi):
                self.turn_cmd = -0.017
            else:
                self.turn_cmd = 0.017
            self.turn_flag =True
        elif not self.turn_flag:
            self.turn_cmd = 0.0 + np.random.normal(0.0, 0.017)
        
        self.yaw += self.turn_cmd

        
        workingbbox = self.area.workingbbox

        if (self.lat > workingbbox[2] or self.lat < workingbbox[0]) and not self.reflection_flag:
            self.reflection_flag = True
            self.yaw = np.pi - self.yaw
            self.turn_cmd = 0

        elif (self.lon > workingbbox[3] or self.lon < workingbbox[1]) and not self.reflection_flag:
            self.reflection_flag = True
            self.yaw = 2*np.pi - self.yaw
            self.turn_cmd = 0

        if self.yaw < 0.0:
            self.yaw += 2*np.pi

        self.yaw %= 2*np.pi
        
        # Reset flags
        if self.lat < innerbbox[2] and self.lat > innerbbox[0] and self.lon < innerbbox[3] and self.lon > innerbbox[1] and self.turn_flag:
            self.turn_flag = False
            self.reflection_flag = False
        
        # Displacement
        self.acc = np.random.normal(0,self.acc_std)
        self.vel += (self.acc * time_step) 
        self.vel = min(self.vel, self.max_vel)
        self.vel = max(self.vel, self.min_vel)      

        disp = self.vel * time_step 
        disp_x = disp * np.sin(self.yaw)
        disp_y = disp * np.cos(self.yaw)
        (disp_lat, disp_lon) = self.area.m2deg((disp_y, disp_x))
        self.lat += disp_lat
        self.lon += disp_lon

    def move_to(self,lat,lon,yaw):
        self.lat = lat
        self.lon = lon 
        self.yaw = yaw

    def sense(self, scale=1.0, zoom=18, tile_size=256):
        coords = (self.lat, self.lon, zoom)
        loc = MetaTile(coords, self.area.dataroot, aerial_dir=self.area.dir)
        aerial = loc.get_metatile(domains=['aerial'],rotation=self.yaw, scale=scale)[0]       
        gt_map = loc.get_metatile(domains=['map'],rotation=self.yaw, scale=1.0)[0]       
        return (aerial, gt_map)

    def __str__(self):
        return("lat {} lon {} yaw {} vel {}".format(self.lat, self.lon, self.yaw, self.vel))

    def __repr__(self):
        return ('{}_{}'.format(self.__class__.__name__, self.__name__))

    def show(self,zoom=18):
        coords = (self.lat,self.lon,zoom)
        MetaTile(coords, self.area.dataroot, self.area.dir).show()

