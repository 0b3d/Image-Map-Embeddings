import os
import pandas as pd
from slutils.location import Location

class Area():
    
    def __init__(self, name, dataroot):
        self.name = name 
        self.dataroot = dataroot 
        self.metafile = os.path.join('slutils', 'metadata', name + '.csv')
        self.frame = pd.read_csv(self.metafile)
        self.N = len(self.frame)

    def get_location(self, index, zooms=[18,19]):
        
        if type(index) == int:
            row = self.frame.iloc[index,:]
        elif type(index) == str:
            index = self.frame[ self.frame['pano_id'] == index].index.to_list()[0]
            row = self.frame.iloc[index,:]
        else:
            raise Exception("Not valid location")
        
        row = row.to_dict()
        loc = Location(index=index, area_name=self.name, dataroot=self.dataroot, zooms=zooms, **row)
        return loc
        

    def __str__(self) -> str:
        return 'Area: {} Locations: {}'.format(self.name, self.N)


if __name__ == '__main__':
    path = os.path.join(os.environ['DATASETS'],'streetlearn')
    area = Area('unionsquare5k', dataroot=path) 
    print(area)
    loc = area.get_location(index=0)
    print(loc)
    loc.show_location()
