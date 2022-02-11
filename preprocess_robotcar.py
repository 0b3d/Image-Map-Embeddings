"""Extract frames of oxfordrobotcar dataset every certain time stamp.

The required .csv files can be downloaded from https://robotcar-dataset.robots.ox.ac.uk/.

"""
import os
import sys 
import csv
import cv2
import numpy as np 
import pandas as pd 
from datetime import datetime as dt

def read_camera_frames(cfg):
    #Read camera frames
    camera = 'mono_left'
    timestamps_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], camera + '.timestamps')
    left_frame = pd.read_csv(timestamps_path,delim_whitespace=True)

    camera = 'mono_right'
    timestamps_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], camera + '.timestamps')
    right_frame = pd.read_csv(timestamps_path,delim_whitespace=True)

    camera = 'mono_rear'
    timestamps_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], camera + '.timestamps')
    rear_frame = pd.read_csv(timestamps_path,delim_whitespace=True)

    camera = 'stereo'
    timestamps_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], camera + '.timestamps')
    front_frame = pd.read_csv(timestamps_path,delim_whitespace=True)

    frames = {'front':front_frame, 'right': right_frame, 'left':left_frame, 'rear':rear_frame}
    return frames

def convert_yaw(yaw):
    # If yaw is negative add 360
    if yaw < 0:
        yaw += 2*np.pi
    # Substract pi/2 to change reference to north
    yaw = yaw - np.pi/2
    if yaw < 0:
        yaw += 2*np.pi
    # Convert to degrees
    yaw = np.degrees(yaw)
    return yaw

def find_nearest(frames, value):
    indexes = np.zeros((4),dtype=np.int32)
    for i,frame in enumerate(["front","left","right","rear"]):
        array = frames[frame].iloc[:,0].values
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        indexes[i] = idx
    return indexes

def find_nearest_index(frame, value, colidx=0):
    array = frame.iloc[:,colidx].values
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def getVO(frame, tsi, tsi_1):
    tsi_idx = find_nearest_index(frame, tsi, colidx=0) # Source 
    tsi_1idx = find_nearest_index(frame, tsi_1, colidx=1) # Destination
    subframe = frame[tsi_1idx:tsi_idx+1]
    delta_x = subframe['x'].sum()
    delta_y = subframe['y'].sum()
    delta_z = subframe['z'].sum()
    delta_roll = subframe['roll'].sum()
    delta_pitch = subframe['pitch'].sum()
    delta_yaw = subframe['yaw'].sum()
    return (delta_x, delta_y, delta_z, delta_roll, delta_pitch, delta_yaw)

def process(cfg):
    # create directory if it does not exist
    save_dir = os.path.join('datasets/robotcar/',cfg['datestr'],cfg['dirname']) # Save directory                     # 

    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    # Create dataframes
    gt_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], 'rtk.csv')
    gps_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], 'gps', 'gps.csv')
    vo_path = os.path.join('DATASETS', 'robotcar', cfg['datestr'], 'vo', 'vo.csv')

    gt_frame = pd.read_csv(gt_path)             # ground truth dataframe
    gps_frame = pd.read_csv(gps_path)           # gps dataframe
    vo_frame = pd.read_csv(vo_path)             # vo frame

    initial_ts = cfg['initial_ts']  #1446118262700898 #gt_frame.iloc[0,0]
    final_ts = cfg['final_ts']      #1446118644700898 #gt_frame.iloc[-1,0]

    n = int((final_ts - initial_ts) / (cfg['delta']*1000000))
    print("Frames to be processed %d locations" %n)

    # Prepare csv file
    metafile = os.path.join(save_dir, cfg['datestr'] + cfg['chunk'] + '.csv')
    with open(metafile, mode='w') as csv_file:
        fieldnames = ['ts', 
                      'front_ts', 
                      'left_ts', 
                      'right_ts', 
                      'rear_ts', 
                      'gt_lat', 
                      'gt_lon',
                      'gt_yaw',
                      'gt_index',
                      'gps_lat', 
                      'gps_lon',
                      'gps_index', 
                      'vo_x', 
                      'vo_y', 
                      'vo_z', 
                      'vo_roll', 
                      'vo_pitch', 
                      'vo_yaw']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

    camera_frames = read_camera_frames(cfg)
    # If save views 
    if cfg['saveViews']:
        sys.path.append(os.path.join(os.environ['RCSDK'], 'python'))
        import cv2
        from image import load_image
        from camera_model import CameraModel

    # For every sample
    for i in range(0,n+1):
        print("Processing frame {}/{}".format(i+1,n+1))

        tsi = initial_ts + int(i*cfg['delta']*1000000)
        tsi_1 = initial_ts + int((i-1)*cfg['delta']*1000000)  
        gt_idx = find_nearest_index(gt_frame,tsi)       # index of nearest ground truth
        gps_idx = find_nearest_index(gps_frame,tsi)     # index of nearest gps

        # Get visual odometry
        if i > 0:
            delta_x, delta_y, delta_z, delta_roll, delta_pitch, delta_yaw = getVO(vo_frame, tsi, tsi_1) 
        else:
            delta_x, delta_y, delta_z, delta_roll, delta_pitch, delta_yaw = (0,0,0,0,0,0) 
        
        metadata = {
            'ts' : tsi,

            # Gt_data
            'gt_lat' : gt_frame.loc[gt_idx,"latitude"],
            'gt_lon' : gt_frame.loc[gt_idx,"longitude"],
            'gt_yaw' : convert_yaw(gt_frame.loc[gt_idx,"yaw"]),
            'gt_index': gt_idx,

            # gps data
            'gps_lat' : gps_frame.loc[gps_idx,"latitude"],
            'gps_lon' : gps_frame.loc[gps_idx,"longitude"],
            'gps_index': gps_idx,
            
            # vo data
            'vo_x': delta_x,
            'vo_y': delta_y,
            'vo_z': delta_z,
            'vo_roll': delta_roll,
            'vo_pitch': delta_pitch,
            'vo_yaw': delta_yaw

        }

        # Process images
        idxs = find_nearest(camera_frames,tsi)         # indexes of nearest camera frames
        chunck_str = ''


        if cfg['saveViews']:

            for c, camera in enumerate(["front","left","right","rear"]):
                outfilename = os.path.join(save_dir, str(metadata['ts']) + '_' + camera + '.png')
                timestamp = camera_frames[camera].iloc[idxs[c],0] 
                metadata[camera + '_ts'] = timestamp
                chunck = camera_frames[camera].iloc[idxs[c],1]
                chunck_str += str(chunck) 

                if os.path.isfile(outfilename):
                    print('view exists ...')
                else:

                    model_dir = os.path.join(os.environ['RCSDK'], 'models')
                    
                    if camera == "front":
                        data_dir = os.path.join('DATASETS', 'robotcar', cfg['datestr'], "stereo", "centre")
                        filename = os.path.join(data_dir, str(timestamp) + '.png')
                    else:
                        data_dir = os.path.join('DATASETS', 'robotcar', cfg['datestr'], "mono_" + camera)
                        filename = os.path.join(data_dir, str(timestamp) + '.png')
                        

                    model = CameraModel(model_dir, data_dir)
                    datetime = dt.utcfromtimestamp(timestamp/1000000)

                    img = load_image(filename, model)
                    if camera == "front":
                        H,W,C = np.shape(img)
                        new_H = 128
                        new_W = int(W/H * 128)
                        img = cv2.resize(img, (new_W, new_H))
                        centre = new_W//2
                        img = img[:,centre-64:centre+64]
                    else:
                        img = cv2.resize(img, (128,128))

                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(outfilename, img) 

        else:
            for c, camera in enumerate(["front","left","right","rear"]):
                outfilename = os.path.join(save_dir, str(metadata['ts']) + '_' + camera + '.png')
                timestamp = camera_frames[camera].iloc[idxs[c],0] 
                metadata[camera + '_ts'] = timestamp
                chunck = camera_frames[camera].iloc[idxs[c],1]
                chunck_str += str(chunck)       
            metadata['chunck'] = chunck_str      

        # Save metadata
        with open(metafile, mode='a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(metadata)
        

if __name__ == "__main__":
    # configuration
    cfg = {
    'delta' : 0.2,                          # Delta time in seconds  
    'saveViews' : True,                     # If true process images
    'datestr' : '2015-10-29-10-55-43',      # Traversal
    'dirname' : 'processed_chunk1',         # Save directory    
    'chunk' : '_chunk1',          
    'initial_ts' : 1416586023959457,        # Stereo timestamp
    'final_ts' : 1416586398908563
    }
    process(cfg)
