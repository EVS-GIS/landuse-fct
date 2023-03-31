# coding: utf-8

"""
DOCME

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os
from pathlib import Path
import numpy as np
import fiona
import fiona.crs
import geopandas
from config.config import db_config, paths_config, parameters_config
from sqlalchemy import create_engine, text

def CreateTileset(resolution: float = 1000.0):
    """
    Creates one tilesets in GeoPackage format (.gpkg) with rectangular polygons that tile the bounding box of 
    the given datasource according to a resolution parameter. The first tileset contains polygons that are 
    aligned with the bounding box, whereas the second tileset contains polygons that are shifted by half the 
    resolution in both the x and y directions.

    :param datasource: str, default='bdalti'
        The name of the datasource as specified in the application's configuration file.
    :param resolution: float, default=10000.0
        The width and height of the rectangular polygons in the tilesets.
    :param tileset1: str, default='../inputs/10k_tileset.gpkg'
        The filename of the first tileset to create.
    :return: None
    """

    db_params = db_config()
    paths = paths_config()
    params = parameters_config()

    schema = { 
        'geometry': 'Polygon', 
        'properties': {'GID': 'int',
                       'ROW': 'int',
                       'COL': 'int',
                       'X0': 'float',
                       'Y0': 'float'} }
    
    options = dict(
        driver='GPKG',
        schema=schema,
        crs=fiona.crs.from_epsg(params['crs']))
    
    # extract bounding box coordinates from zone_etude input
    zone_etude = geopandas.read_file(os.path.join(paths['inputs_dir'], paths['zone_etude_name']))
    minx, miny, maxx, maxy = [float(val) for val in zone_etude.total_bounds]

    # add resolution to max to get the whole extent and above
    maxx += resolution
    maxy += resolution

    # Tileset
    gx, gy = np.arange(minx, maxx, resolution), np.arange(miny, maxy, resolution)

    gid = 1
    with fiona.open(tileset, 'w', **options) as dst:   
        for i in range(len(gx)-1):
            for j in range(len(gy)-1):
                
                coordinates = [(gx[i],gy[j]),(gx[i],gy[j+1]),(gx[i+1],gy[j+1]),(gx[i+1],gy[j])]
                
                feature = {'geometry': {
                            'type':'Polygon',
                            'coordinates': [coordinates] 
                            },
                           'properties': {
                               'GID': gid,
                               'ROW': len(gy)-j-1,
                               'COL': i+1,
                               'Y0': gy[j+1],
                               'X0': gx[i]
                           }
                    }
                
                dst.write(feature)
                gid+=1

def pgenvelope_tile(
        tile):

    # pg database connexion
    db_params = db_config()
    con = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(con)

    with engine.connect() as condb:

        

from config.config import paths_config, parameters_config
paths=paths_config()
tileset= os.path.join(paths['outputs_dir'], 'tileset.gpkg')
data = geopandas.read_file(tileset).iloc[:1]

data.total_bounds

# extract_data_tile(tile = data)


def starcall_nokwargs(args):
    """
    Invoke first arg function with all other arguments.
    """

    fun = args[0]
    return fun(*args[1:])