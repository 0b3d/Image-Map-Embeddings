import cv2
import numpy as np
from math import cos, sin, acos, atan2

def rotate_panorama(image, roll=0.0, pitch=0.0, yaw=0.0):
    """ Rotates a equirectangular image given angles

        Parameters:
            image (Numpy array) -> equirectangular image
            roll (float) -> Roll angle in degrees
            pitch (float) -> Pitch angle in degrees 
            yaw (float) -> Yaw angle in degrees 
    """
    
    h,w = image.shape[0:2]
    euler_angles = np.radians(np.array([roll,pitch,yaw]))
    [R, _] = cv2.Rodrigues(euler_angles) 
    
    # Project equirectangular points to original sphere
    lat = np.pi / h * np.arange(0,h)
    lat = np.expand_dims(lat,1)
    lon = (2*np.pi / w * np.arange(0,w)).T
    lon = np.expand_dims(lon,0)

    # Convert to cartesian coordinates
    x = np.sin(lat)*np.cos(lon)
    y = np.sin(lat)*np.sin(lon)
    z = np.tile(np.cos(lat), [1,w])

    # Rotate points
    xyz = np.stack([x,y,z],axis=2).reshape(h*w,3).T
    rotated_points = np.dot(R,xyz).T    
    
    # Go back to spherical coordinates
    new_lat = np.arccos(rotated_points[:,2]).reshape(h,w)
    new_lon = np.arctan2(rotated_points[:,1],rotated_points[:,0]).reshape(h,w)
    neg = np.where(new_lon<0)
    new_lon[neg] += 2*np.pi
    
    # Remap image
    y_map = new_lat * h / np.pi
    x_map = new_lon * w / (2 * np.pi)
    new_image = cv2.remap(image, x_map.astype(np.float32), y_map.astype(np.float32), cv2.INTER_NEAREST, 0, cv2.BORDER_REPLICATE)   #cv2.INTER_CUBIC

    return new_image


