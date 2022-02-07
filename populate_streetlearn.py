import os
import sys 
import pandas as pd
import numpy as np

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("No StreetLearn data set path was provided")
        quit()

    streetlearn_path = sys.argv[1]

    nodes_manhattan = os.path.join(streetlearn_path, 'jpegs_manhattan_2019','nodes.txt')
    nodes_pittsburgh = os.path.join(streetlearn_path, 'jpegs_pittsburgh_2019','nodes.txt')

    man_df = pd.read_csv(nodes_manhattan, names=['pano_id','yaw','lat','lon'])
    pit_df = pd.read_csv(nodes_pittsburgh, names=['pano_id','yaw','lat','lon'])

    # Train set
    filename = 'train_set.csv'
    path = os.path.join('slutils','metadata', filename)
    index_df = pd.read_csv(path)
    index_df['pano_id'] = ""
    index_df['yaw'] = 0
    index_df['lat'] = 0.0
    index_df['lon'] = 0.0
    print('Populating train set')

    indices_manhattan = index_df[index_df['city'] == 'manhattan']['global_index'].values
    pano_ids_man = man_df.pano_id.values[indices_manhattan]
    lats_man = man_df.lat.values[indices_manhattan]
    lons_man = man_df.lon.values[indices_manhattan]
    yaws_man = man_df.yaw.values[indices_manhattan]
    
    pano_ids_pit = pit_df.pano_id
    lats_pit = pit_df.lat.values
    lons_pit = pit_df.lon.values
    yaws_pit = pit_df.yaw.values    
    
    pano_ids = np.concatenate([pano_ids_man, pano_ids_pit],0)
    lats = np.concatenate([lats_man, lats_pit],0)
    lons = np.concatenate([lons_man, lons_pit],0)
    yaws = np.concatenate([yaws_man, yaws_pit],0)
    yaws[ yaws < 0] += 360
    
    index_df.yaw = yaws
    index_df.pano_id = pano_ids
    index_df.lat = lats
    index_df.lon = lons

    filename = 'train.csv'
    outpath = os.path.join('slutils','metadata', filename)
    index_df.to_csv(outpath, index=False)

    # Test sets
    for dataset in ['hudsonriver5k','unionsquare5k','wallstreet5k']:

        filename = dataset + '_set.csv'
        path = os.path.join('slutils','metadata', filename)
        index_df = pd.read_csv(path)

        filename = dataset + '.csv'
        outpath = os.path.join('slutils','metadata', filename)

        index_df['pano_id'] = ""
        index_df['yaw'] = 0
        index_df['lat'] = 0.0
        index_df['lon'] = 0.0

        print('Populating ', dataset)

        indices = index_df['global_index'].values
        index_df.pano_id = man_df.pano_id.values[indices]
        index_df.lat = man_df.lat.values[indices]
        index_df.lon = man_df.lon.values[indices]
        yaw = man_df.yaw.values[indices]
        yaw[ yaw < 0] += 360
        index_df.yaw = yaw
        index_df.to_csv(outpath, index=False)



                                    
