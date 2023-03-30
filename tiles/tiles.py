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
from config.config import db_config
from sqlalchemy import create_engine, text

def CreateTileset(resolution: float = 1000.0, 
                  tileset1: str = './outputs/1k_tileset.gpkg'):
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
        crs=fiona.crs.from_epsg(2154))
    
    # pg database connexion
    params = db_config()
    con = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
    engine = create_engine(con)

    # extract bounding box coordinate from postgis database zone_etude table
    with engine.connect() as condb:
        with open(os.path.join(Path(os.getcwd()), "queries", "utils", "zone_etude_extent.sql"), "r", encoding="UTF-8") as file:
            query = text(file.read())
            result = condb.execute(query)
            extent = result.fetchall()

    # extract bbox values from postgis extent
    box_str = extent[0][0]  # extract string from extent
    box_vals = box_str.replace("BOX(", "").replace(")", "").replace(" ", ",")  # reshape string
    box_list = box_vals.split(",")  # create list from string
    minx, miny, maxx, maxy = [float(val) for val in box_list]  # convert to float

    # add resolution to max to get the whole extent and above
    maxx += resolution
    maxy += resolution

    # Tileset 1
    gx, gy = np.arange(minx, maxx, resolution), np.arange(miny, maxy, resolution)

    gid = 1
    with fiona.open(tileset1, 'w', **options) as dst:   
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