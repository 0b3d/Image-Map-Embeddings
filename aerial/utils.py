
import cv2
import math 
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import colors
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms

from utils.util import haversine
from aerial.tile import MetaTile, Tile

def get_transforms(preprocess):
    transform_list = []
    transform_list += [transforms.ToTensor()]
    if 'normalize':
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    return transforms.Compose(transform_list)

def prepare_tile(tile, tile_size=128, preprocess='none'):
    tile = cv2.resize(tile, (tile_size, tile_size))
    tile = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
    tile = Image.fromarray(tile)
    tile = get_transforms(preprocess)(tile)
    tile = tile.view(1,3,tile_size,tile_size)
    return tile

def visualize(trial, step, area, area_map, robot, particles, estimate, vo_estimate, best_particle=None, zoom=18):
    
    """ Visualize robot and particles in the world """    
    plt.title('PF, trial {}, step {}'.format(trial+1,step))
    grid = area.get_map_grid_for_mpl()

    plt.imshow(cv2.cvtColor(area_map, cv2.COLOR_BGR2RGB),extent=grid)
    plt.autoscale(False)
    plt.grid()
    
    # Draw particles
    if particles is not None:
        particles = particles[particles[:,-1].argsort(),:]
        plt.scatter(particles[:,1], particles[:,0], s=2, c=particles[:,-1], cmap='Blues',norm=colors.Normalize(0,1/particles.shape[0]))
    
    # draw drone position
    robot_marker = plt.scatter(robot.lon, robot.lat, color='red', alpha=1.0)
    arrow = plt.Arrow(robot.lon, robot.lat, 0.003*np.cos(np.pi/2-robot.yaw), 0.003*np.sin(np.pi/2-robot.yaw), alpha=1.0, facecolor='r', edgecolor='r',width=0.001)
    plt.gca().add_patch(arrow)

    # Draw vo estimated pos
    vo_marker = plt.scatter(vo_estimate[1], vo_estimate[0], color='black', alpha=1.0)
    arrow = plt.Arrow(vo_estimate[1], vo_estimate[0], 0.003*np.cos(np.pi/2-vo_estimate[2]), 0.003*np.sin(np.pi/2-vo_estimate[2]), alpha=1.0, facecolor='k', edgecolor='k',width=0.001)
    plt.gca().add_patch(arrow)

    # Draw estimate position
    estimate_marker = plt.scatter(estimate[1], estimate[0], color='green', alpha=1.0)
    arrow = plt.Arrow(estimate[1], estimate[0], 0.003*np.cos(np.pi/2-estimate[2]), 0.003*np.sin(np.pi/2-estimate[2]), alpha=1.0, facecolor='g', edgecolor='g',width=0.001)
    plt.gca().add_patch(arrow)

    markers = [robot_marker, estimate_marker, vo_marker]
    legend = ['Ground truth', 'Estimated', 'VO']        
    # draw best particle
    if best_particle is not None:
        best_marker = plt.scatter(best_particle[1], best_particle[0], color='yellow', alpha=0.8)
        markers.append(best_marker)
        legend.append('best particle')

    plt.legend(markers, legend, loc='upper right')

    plt.pause(0.001)
    plt.gca().clear()

def visualize2(trial, step, area, area_map, robot, particles, estimate, vo_estimate, best_particle=None, zoom=18):
    """ Visualize robot and particles in the world """

    # calculate scale 
    delta_z = 0.25 * math.sin(2*math.pi*step/50)
    scale = 2 ** delta_z
    MLE = 1000 * haversine(estimate[0], estimate[1], robot.lat, robot.lon)

    # mean particle's view
    mp_map = MetaTile((estimate[0], estimate[1], zoom), area.dataroot).get_meta_tile(domains=['map'],rotation=estimate[2])[0]
    mp_map = draw_north(mp_map,estimate[2])
    
    # Aerial image
    aerial, _ = robot.sense(scale=scale)
    aerial = draw_north(aerial, robot.yaw)
    
    white_strip1 = np.ones(((720-512)//4,256,3), dtype=np.uint8)*255
    cv2.putText(white_strip1, "Aircraft's view", (10,20), cv2. FONT_HERSHEY_PLAIN, 1.25, (255, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(white_strip1, "scale: {:.2f}".format(scale), (10,40), cv2. FONT_HERSHEY_PLAIN, 1.2, (0, 0, 0), 1, cv2.LINE_AA)
    
    white_strip2 = np.ones(((720-512)//4,256,3), dtype=np.uint8)*255
    img_pil = Image.fromarray(white_strip2)
    fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 20)
    draw = ImageDraw.Draw(img_pil)
    draw.text((10, 10),"© Getmapping Plc",font=fnt,fill = (0, 0, 0, 0))
    white_strip2 = np.array(img_pil)
    
    
    white_strip3 = np.ones(((720-512)//4,256,3), dtype=np.uint8)*255
    cv2.putText(white_strip3, "Estimated map location", (10,20), cv2. FONT_HERSHEY_PLAIN, 1.25, (255, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(white_strip3, "MLE: {:.2f} m".format(MLE), (10,40), cv2. FONT_HERSHEY_PLAIN, 1.2, (0, 0, 0), 1, cv2.LINE_AA)
    white_strip4 = np.ones(((720-512)//4,256,3), dtype=np.uint8)*255


    img = np.concatenate([white_strip1, aerial, white_strip2, white_strip3, mp_map, white_strip4], axis=0)

    plt.title('Particle filter test in {}, step {}'.format(area.readable_name,step))
    grid = area.get_map_grid_for_mpl()

    plt.imshow(cv2.cvtColor(area_map, cv2.COLOR_BGR2RGB),extent=grid)
    plt.autoscale(False)
    plt.grid()

    markers = []
    legend = []
    

    if particles is not None:
        particles = particles[particles[:,-1].argsort(),:]
        plt.scatter(particles[:,1], particles[:,0], s=2, c=particles[:,-1], cmap='Blues',norm=colors.Normalize(0,1/particles.shape[0]))

  
    robot_marker = plt.scatter(robot.lon, robot.lat, color='red', alpha=1.0)
    arrow = plt.Arrow(robot.lon, robot.lat, 0.003*np.cos(np.pi/2-robot.yaw), 0.003*np.sin(np.pi/2-robot.yaw), alpha=1.0, facecolor='r', edgecolor='r',width=0.0015)
    plt.gca().add_patch(arrow)
    markers.append(robot_marker)
    legend.append('Ground truth (GT)')


    if vo_estimate is not None:
        vo_marker = plt.scatter(vo_estimate[1], vo_estimate[0], color='magenta', alpha=0.6)
        arrow = plt.Arrow(vo_estimate[1], vo_estimate[0], 0.003*np.cos(np.pi/2-vo_estimate[2]), 0.003*np.sin(np.pi/2-vo_estimate[2]), alpha=1.0, facecolor='magenta', edgecolor='magenta',width=0.001)
        plt.gca().add_patch(arrow)
        markers.append(vo_marker)
        legend.append('Estimate (VO)')


    if best_particle is not None:
        best_marker =plt.scatter(best_particle[1], best_particle[0], color='yellow', alpha=0.6)
        arrow = plt.Arrow(best_particle[1], best_particle[0], 0.003*np.cos(np.pi/2-best_particle[2]), 0.003*np.sin(np.pi/2-best_particle[2]), alpha=1.0, facecolor='y', edgecolor='y',width=0.001)
        plt.gca().add_patch(arrow)
        markers.append(best_marker)
        legend.append('Best particle')


    estimate_marker = plt.scatter(estimate[1], estimate[0], color='green', alpha=1.0)
    arrow = plt.Arrow(estimate[1], estimate[0], 0.003*np.cos(np.pi/2-estimate[2]), 0.003*np.sin(np.pi/2-estimate[2]), alpha=1.0, facecolor='g', edgecolor='g',width=0.001)
    plt.gca().add_patch(arrow)
    markers.append(estimate_marker)
    legend.append('Estimate (VO+ES)')


    plt.legend(markers, legend, loc='upper left')
    plt.xlabel(r" $\copyright$ Crown copyright and database rights 2020 Ordance Survey (100025252)")

    tmpfile = './temp/temp.png'
    plt.savefig(tmpfile, dpi=150)
    chart = cv2.imread(tmpfile)
    chart = cv2.resize(chart, (1280-256,720))
    image = np.concatenate([chart,img], axis=1)

    plt.pause(0.01)
    plt.gca().clear()
    return image

def visualize3(ax, trial, step, area, area_map, robot, particles, estimate, vo_estimate, best_particle=None, zoom=18):
    
    """ Visualize robot and particles in the world """    
    #ax.title('PF, trial {}, step {}'.format(trial+1,step))
    grid = area.get_map_grid_for_mpl()

    ax.imshow(cv2.cvtColor(area_map, cv2.COLOR_BGR2RGB),extent=grid)
    ax.autoscale(False)
    ax.grid()
    
    # Draw particles
    if particles is not None:
        particles = particles[particles[:,-1].argsort(),:]
        ax.scatter(particles[:,1], particles[:,0], s=2, c=particles[:,-1], cmap='Blues',norm=colors.Normalize(0,1/particles.shape[0]))
    
    # draw drone position
    robot_marker = ax.scatter(robot.lon, robot.lat, color='red', alpha=1.0)
    arrow = plt.Arrow(robot.lon, robot.lat, 0.003*np.cos(np.pi/2-robot.yaw), 0.003*np.sin(np.pi/2-robot.yaw), alpha=1.0, facecolor='r', edgecolor='r',width=0.001)
    ax.add_patch(arrow)

    # Draw vo estimated pos
    vo_marker = ax.scatter(vo_estimate[1], vo_estimate[0], color='black', alpha=1.0)
    arrow = plt.Arrow(vo_estimate[1], vo_estimate[0], 0.003*np.cos(np.pi/2-vo_estimate[2]), 0.003*np.sin(np.pi/2-vo_estimate[2]), alpha=1.0, facecolor='k', edgecolor='k',width=0.001)
    ax.add_patch(arrow)

    # Draw estimate position
    estimate_marker = ax.scatter(estimate[1], estimate[0], color='green', alpha=1.0)
    arrow = plt.Arrow(estimate[1], estimate[0], 0.003*np.cos(np.pi/2-estimate[2]), 0.003*np.sin(np.pi/2-estimate[2]), alpha=1.0, facecolor='g', edgecolor='g',width=0.001)
    ax.add_patch(arrow)
            
    # draw best particle
    if best_particle is not None:
        ax.scatter(best_particle[1], best_particle[0], color='yellow', alpha=0.8)

    ax.legend((robot_marker, estimate_marker, vo_marker), ('Ground truth', 'Estimated', 'vo'), loc='upper right')

    
    #ax.clear()


def get_map(extent, zoom=18, scale=1.0):
    area_map = []
    for i in range(extent[1],extent[3]+1):
        row = []
        for j in range(extent[0],extent[2]+1):
            coords = (int(j),int(i), zoom)
            mapa = Tile(coords).getTile(domain='map')
            mapa = cv2.resize(mapa,(64,64))
            row.append(mapa)

        row = np.concatenate(row,1)
        area_map.append(row)
        
    
    area_map = np.concatenate(area_map, axis=0)
    H,W = area_map.shape[:2]
    area_map = cv2.resize(area_map,(int(W*scale),int(H*scale)))
    return area_map

def cv2cvo(p, origin=np.asarray([128,128])):
    return p - origin

def cvo2cv(p, origin=np.asarray([128,128])):
    origin = np.asarray(origin)
    return p + origin

def get_R_2D(angle):
    c = np.cos(angle)
    s = np.sin(angle)
    return np.array([[c,-s],[s,c]])

def draw_north(image, angle=0.0, origin=np.asarray([128,128])):
    thickness = 2

    O_cvo  = np.array([0,0])
    E_cvo  = np.array([64,0])
    N_cvo  = np.array([0,-64])

    origin_text = np.array([0,-80])
    
    R = get_R_2D(-angle)
    E_cvo = np.matmul(R,E_cvo).astype(np.int16)
    N_cvo = np.matmul(R,N_cvo).astype(np.int16)
    origin_text = np.matmul(R,origin_text).astype(np.int16)
    
    image = cv2.arrowedLine(image, tuple(cvo2cv(O_cvo, origin)), tuple(cvo2cv(E_cvo, origin)), (255,0,0), thickness) 
    image = cv2.arrowedLine(image, tuple(cvo2cv(O_cvo, origin)), tuple(cvo2cv(N_cvo, origin)), (0,0,255), thickness) 
    cv2.putText(image, "N", tuple(cvo2cv(origin_text,origin)), cv2. FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 1, cv2.LINE_AA)
    return image
