
This file describes how to generate 256x256 map and aerial tiles at zoom level 18 using data from the Ordnance Survey and aerial imagery (25 cm resolution) from Getmapping Plc. At London's latitude each map tile covers an area of 95x95 m^2 approximately. Tiles for each domain will be stored in a separate directory and named after the slippy map convention.

Requires QGIS (tested with version 3.16). 

### Downloading map data from Digimap

1. Go to Data Download in the Ordnance survey tab.
2. Select the area of interest using tile name, e.g. ST57SE.
3. In the OS MasterMap section select Topography.
4. Add to basket and select version. In the format field choose "File Geodatabase".
5. Send request order.

### Generating map tiles

1. Extract the zip file to a folder.
2. Drag and drop the ".gdb" folder into the layer panel in QGIS.
3. Select a transformation. We used Inverse of British National Grid + OSGB 1936 to WGS 84 (9).
4. Tick Topographicarea, Topographicline and Topographicpoint layers. 
5. Ensure the correct order of the layers (points on the top and areas at the bottom).
6. To apply the rendering style to each layer, go to its properties, then  Style -> Load Style and select the corresponding ".qml" file provided in the *aerial/styles* directory of this repository.  
7. In points' layer tick inland water, positioned nonconiferous and coniferous trees. In the case of lines and areas, tick all elements in each layer.
8. To generate the tiles go to the processing toolbox and search for the *Generate XYZ tiles (Directory)* tool. Fill the fields as shown below and run.

	- Extent: The geographical extent in EPGS:27700 e.g. 405000.0000,410000.0000,285000.0000,290000.0000 [EPSG:27700]
	- Minimum zoom: 18
	- Maximum zoom: 18
	- DPI: 96
	- Background color: White
	- Tile Format: png
	- Metatile size 4
	- Tile width: 256
	- Tile height: 256
	- Untick TMS convention
	- Choose an output directory and an optional path for an html leaflet.
	- Other fields can be let with default values.
	
### Downloading aerial data from Digimap 

1. Go to Data Download in the Aerial tab.
2. Select area and year of interest using tile name.
3. Add to basket and download.

### Generating aerial tiles
To generate aerial tiles, load data to QGIS, set CRS to EPSG:27700 (in properties) and follow a similar procedure to that described for map tiles. Save aerial images as '.jpg' into an empty directory.

### Directory structure

In the end, the structure of directories up to level 2 is:

```
dataroot/
├── aerial_tiles 			-> (all areas, including ST57SE2017)
│   ├── 18 
├── ST57SE_aerial_tiles_2014		-> (overlaping areas require a separate folder)
|   ├── 18
├── ST57SE_aerial_tiles_2016   
|   ├── 18
|
└── map_tiles
    ├── 18
```
You can choose your own folder names but modify accordingly the "directories" dictionary in the module: "area.Area".
