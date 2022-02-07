import os
import numpy as np

import math
import torch
import time

from localizer import BaseLocalizer
from aerial.interpolate import trilinear_interpolation_numpy
from aerial.grid_utils import *
from aerial.motion_estimate import Homography as Mestimator
from sklearn.metrics import pairwise_distances
from utils.util import haversine

from aerial.robot import Robot
from aerial.area import Area
from aerial.utils import *

class AerialPFLocalizer(BaseLocalizer):
    def __init__(self, opt):
        BaseLocalizer.__init__(self, opt)
        self.np = opt.np
        self.trials = opt.trials
        self.steps = opt.steps
        self.particles = np.zeros((opt.np,4))
        self.opt = opt

    @staticmethod
    def modify_commandline_options(parser):
        """Add new dataset-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.
        """
        # Set defaults related to dataset and model
        parser.set_defaults(name='v3_17a',
                            model='street2vec', embedding_dim=16, 
                            preprocess='normalize',  
                            tile_zoom=[18], tile_size=128,
                            panorama_mode = 'grid', # To ensure compatibility with street2vec model
                            gpu_ids="-1" # Work using CPU only. 
                            )
        
        # Parameters defined for the 
        parser.add_argument('--expname', type=str, default = 'untitled', help="Name of the experiment")
        parser.add_argument('--np', type=int, default = 20000, help='Number of particles')
        parser.add_argument('--particles_noise', type=float, nargs='+', default = [10,10], help="Particles's noise standard deviation in meters")
        parser.add_argument('--trials', type=int, nargs='+', default=None, help='Trial route indexes, if none will test all')
        parser.add_argument('--states', action='store_true', help='If set, it will save a numpy array with the particles states at each step')
        parser.add_argument('--no_scale', action='store_true', help='If set, it disables changes in the scale')
        parser.add_argument('--pano_size', type=int, default=128, help='The size of the sensed image by the robot')

        return parser

    def set_model(self,model):
        def map_model(batch):
            with torch.no_grad():
                X_f = model.netX(batch)
                X_d = X_f.view(X_f.size(0),-1)
                X_o = model.netEMBX(X_d)
                return X_o

        def aerial_model(batch):
            with torch.no_grad():
                Y_f = model.netY(batch)
                Y_d = Y_f.view(Y_f.size(0),-1)
                Y_o = model.netEMBY(Y_d)
                return Y_f, Y_o

        self.map_net =  map_model
        self.aerial_net =  aerial_model
        self.device = torch.device('cuda:{}'.format(self.opt.gpu_ids[0])) if self.opt.gpu_ids else torch.device('cpu')  # get device name: CPU or GPU

    def observation_model(self, observation, pano_size=128):
        aerial = prepare_tile(observation, pano_size, preprocess=self.opt.preprocess).to(self.device)
        _, aerial_descriptor = self.aerial_net(aerial)
        return aerial_descriptor

    def setup(self): 
        # Set up test area
        self.area = Area(self.opt.area, self.opt.dataroot, self.opt.results_dir)                              
        map_features, working_frame = self.area.get_map_descriptors(self.opt.name, self.opt.epoch)
        self.map_features = map_features
        
        self.wf_min_lon = working_frame[0,:,0,1].min() 
        self.wf_max_lon = working_frame[0,:,0,1].max()
        self.wf_min_lat = working_frame[:,0,0,0].min()
        self.wf_max_lat = working_frame[:,0,0,0].max()

        # Read testing routes for the selected area
        path = os.path.join('aerial','routes','{}_{}.npz'.format(self.area.name,self.opt.seed)) 
        self.routes = np.load(path)['routes']

    def init_particles(self):
        area = self.area
        lat = np.random.uniform(area.workingbbox[0],area.workingbbox[2],self.np)
        lon = np.random.uniform(area.workingbbox[1],area.workingbbox[3],self.np) 
        yaw = np.random.uniform(0,2*np.pi,self.np)
        weights = 1 / self.np * np.ones((self.np))
        states = np.stack([lat,lon,yaw,weights],axis=1)
        self.particles = states

    def motion_update(self,step, dx, dy, turn):
        """ This method updates particles states """
        arcllat, arcllon = self.area.get_arclength()
        nparticles = self.particles.shape[0]
        
        # Apply rotation
        self.particles[:,2] += turn
        
        # Convert translation to world coordinates (rotate by estimated yaw)
        dlon_m = dx*np.cos(-self.particles[:,2]) - dy*np.sin(-self.particles[:,2]) 
        dlat_m = dx*np.sin(-self.particles[:,2]) + dy*np.cos(-self.particles[:,2]) 
        
        # Apply translation & add some noise
        yaw_noise = np.random.normal(0.0, 0.087, nparticles)                   
        lat_noise_m = np.random.normal(0.0, self.opt.particles_noise[0],nparticles)
        lon_noise_m = np.random.normal(0.0, self.opt.particles_noise[1],nparticles)
       
        dlat_m = dlat_m + lat_noise_m
        dlon_m = dlon_m + lon_noise_m

        (disp_lat, disp_lon) = self.area.m2deg((dlat_m, dlon_m))
        
        self.particles[:,0] += disp_lat
        self.particles[:,1] += disp_lon
        self.particles[:,2] += yaw_noise

        # 0 <= yaw <= 2*pi
        self.particles[:,2] = np.where(self.particles[:,2] < 0.0, 
                                       self.particles[:,2] + 2*np.pi, 
                                       self.particles[:,2])
        self.particles[:,2] %= 2*np.pi

        # Kill particles outside bbox 
        a = np.greater(self.particles[:,0], self.area.workingbbox[2])
        c = np.greater(self.particles[:,1], self.area.workingbbox[3])
        b = np.less(self.particles[:,0], self.area.workingbbox[0])
        d = np.less(self.particles[:,1], self.area.workingbbox[1])
        mask = (1-a) * (1-b) * (1-c) * (1-d) 
        self.particles[:,3] *= mask

    def update_weights(self, aerial_features):
        """ Update particle's weigths"""

        # Interpolate descriptors
        H, W, T, _ = self.map_features.shape
        x = (self.particles[:,1] - self.wf_min_lon) * (W - 1) / (self.wf_max_lon-self.wf_min_lon) 
        y = (self.wf_max_lat - self.particles[:,0]) * (H - 1) / (self.wf_max_lat-self.wf_min_lat) 
        t = self.particles[:,2] * T / (2*np.pi)

        descriptors = trilinear_interpolation_numpy(self.map_features, y, x ,t)                # interpolated descriptors
        particles_descriptors = self.opt.scale * descriptors

        distances = pairwise_distances(particles_descriptors, aerial_features).squeeze()
        probs = (self.opt.scale*2 - distances) / (self.opt.scale*2)

        self.particles[:,-1] *= probs
        sp = self.particles[:,-1].sum()
        self.particles[:,-1] /= sp
        
    def systematic_resample(self):
        """ Get indices of particles to resample using systematic method """

        # Remove 10 % of particles if needed
        sorted_idx = np.argsort(self.particles[:,-1])[::-1]
        nparticles = self.particles.shape[0]
        
        if nparticles > 5000:
            nparticles = int(0.90*self.particles.shape[0])
            nparticles = max(nparticles, 5000)
            if self.opt.verbose:
                print("The number of particles is now ", nparticles)        
        
            sorted_idx = sorted_idx[0:nparticles] 
            self.particles = self.particles[sorted_idx,:]
            sp = self.particles[:,-1].sum()
            self.particles[:,-1] /= sp
        
        # resample
        sample = np.random.rand(1)
        arange = np.arange(0,self.particles.shape[0])
        positions = (sample + arange) / self.particles.shape[0]
        
        indexes = np.zeros((self.particles.shape[0]))
        cumulative_sum = np.cumsum(self.particles[:, -1], axis=0)
        cumulative_sum[-1] = 1.0
        i, j = 0, 0
        while i < self.particles.shape[0]:
            if positions[i] < cumulative_sum[j]:
                indexes[i] = j
                i += 1
            else:
                j += 1
    
        self.particles = self.particles[indexes.astype(np.int64),:]
        self.particles[:, -1] = 1.0 / self.particles.shape[0]        

    def get_estimate(self):
        mean_lat = np.average(self.particles[:, 0], weights=self.particles[:, -1], axis=0)
        mean_lon = np.average(self.particles[:, 1], weights=self.particles[:, -1], axis=0)
        pc = np.cos(self.particles[:,2])
        ps = np.sin(self.particles[:,2])
        mc = np.average(pc,weights=self.particles[:,-1])
        ms = np.average(ps,weights=self.particles[:,-1])
        mean_yaw = np.arctan2(ms,mc)
        weighted_mean = np.asarray([mean_lat,mean_lon, mean_yaw])
        return weighted_mean 

    def update_vo_estimate(self, vo_estimate, dx, dy, turn):                
        vo_estimate[2] += turn
        
        # Convert translation to world coordinates (rotate by estimated yaw)
        dlon_m = dx*np.cos(-vo_estimate[2]) - dy*np.sin(-vo_estimate[2]) 
        dlat_m = dx*np.sin(-vo_estimate[2]) + dy*np.cos(-vo_estimate[2]) 
        (disp_lat, disp_lon) = self.area.m2deg((dlat_m, dlon_m))

        vo_estimate[0] += disp_lat  
        vo_estimate[1] += disp_lon
        return vo_estimate
        

    def localize(self):   
        """ Perform PF algorithm """
        routes = self.routes
        print("Particle filter experiment in {}".format(self.area.name))
        
        ntrials, nsteps = routes.shape[:2]
        
        trials = self.opt.trials if self.opt.trials is not None else range(0,ntrials)
        steps = self.opt.steps if self.opt.steps is not None else nsteps 

        Nt = len(trials)

        estimates = np.zeros((ntrials,steps,3))       # lat, lon, yaw
        vo = np.zeros((ntrials,steps,6))              # lat, lon, yaw, dx, dy, dturn
        
        if self.opt.states:
            states = np.zeros((Nt,steps,self.np,4))    # lat, lon, yaw, weight

        if self.opt.visualize:
            area_map = self.area.get_map(style='OSM')

        for lidx, trial in enumerate(trials):
            trial_start_time = time.time()

            robot = Robot('myaircraft', self.area)
            lat, lon, yaw = routes[trial,0]
            robot.move_to(lat, lon, yaw)
            vo_estimate = np.array([lat, lon, yaw])
            aerial, _ = robot.sense(scale=1.0)
            motion_estimator = Mestimator(aerial,verbose=self.opt.verbose)
            self.init_particles()
            estimate = self.get_estimate()

            vo[trial,0,0:3] = vo_estimate            
            estimates[trial,0,:] = estimate 

            if self.opt.states:
                states[lidx,0,:,:] = self.particles

            if self.opt.visualize: 
                visualize(trial, 0, self.area, area_map, robot, 
                          self.particles, estimate, vo_estimate, zoom=18)


            for step in range(1,steps):                                     # MCL           
                step_start_time = time.time()
                
                # Move the robot and estimate movement
                lat, lon, yaw = routes[trial,step]
                robot.move_to(lat, lon, yaw)
                
                delta_yaw, translation, _ = motion_estimator.estimate(aerial)    # Displacement in pixels (x,y) -> (lon, lat)                
                dx = translation[0] * 0.37
                dy = translation[1] * 0.37
                turn = -delta_yaw 
                
                self.update_vo_estimate(vo_estimate, dx, dy, turn)
                self.motion_update(step,dx,dy,turn)

                # Sense and estimate location
                
                if self.opt.no_scale:
                    scale = 1.0
                else:
                    delta_z = 0.25 * math.sin(2*math.pi*step/50)
                    scale = 2 ** delta_z
                
                aerial, _ = robot.sense(scale=scale)
                aerial_features = self.observation_model(aerial,self.opt.pano_size)
                self.update_weights(aerial_features)
                neff = 1.0 / np.sum(np.power(self.particles[:,-1], 2))      # Number of effective particles
                if  neff < 2*self.particles.shape[0] / 3:                   # resample                          
                    self.systematic_resample()                              # Get indices of particles to resample
                estimate = self.get_estimate()
                MLE = 1000 * haversine(estimate[0], estimate[1], robot.lat, robot.lon)
                best_particle_index = np.argmax(self.particles[:,-1])
                best_particle = self.particles[best_particle_index,:2]
                t_step = time.time() - step_start_time
                if self.opt.verbose:
                    print('Trial: {} Step: {} MLE {} Time: {} s'.format(trial, step, MLE, t_step))
                
                # Save data
                estimates[trial,step,:] = estimate
                vo[trial,step,:] = np.concatenate([vo_estimate,np.array([dx,dy,turn])],0)
                
                if self.opt.states:
                    states[lidx,step,0:self.particles.shape[0],:] = self.particles
                
                if self.opt.visualize: 
                    visualize(trial, step, self.area, area_map, robot, 
                              self.particles, estimate, vo_estimate, best_particle, zoom=18)
        
            t_comp = time.time() - trial_start_time
            print("Trial {} with {} steps finished in {} s".format(trial,steps,t_comp))

        #now = datetime.datetime.now()
        #current_time = now.strftime("%H:%M:%S")
        #today = datetime.date.today()
        
        if not self.opt.nosave:
            filename = 'localisation-{}-{}-{}.npz'.format(self.opt.expname, self.area.name, self.opt.seed)
            path = os.path.join(self.opt.results_dir, self.opt.name, filename)
            if self.opt.states:
                np.savez(path,estimates=estimates, vo=vo, states=states)
            else:
                np.savez(path,estimates=estimates,vo=vo)