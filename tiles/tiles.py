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

import numpy as np
import fiona
import fiona.crs
import geopandas

def CreateTileset(tile_size: float = 1000.0,
                  zone_etude_path: str = './inputs/zone_etude.gpkg',
                  tileset_path: str = './outputs/tileset.gpkg',
                  crs = '2154'):
    """
    Creates one tilesets in GeoPackage format (.gpkg) with rectangular polygons that tile the bounding box of 
    the given datasource according to a resolution parameter. The first tileset contains polygons that are 
    aligned with the bounding box, whereas the second tileset contains polygons that are shifted by half the 
    resolution in both the x and y directions.

    :param resolution: float, default=1000.0
        The width and height of the rectangular polygons in the tilesets.
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
        crs=fiona.crs.from_epsg(crs))
    
    # extract bounding box coordinates from zone_etude input
    zone_etude = geopandas.read_file(zone_etude_path)
    minx, miny, maxx, maxy = [float(val) for val in zone_etude.total_bounds]

    # add resolution to max to get the whole extent and above
    maxx += tile_size
    maxy += tile_size

    # Tileset
    gx, gy = np.arange(minx, maxx, tile_size), np.arange(miny, maxy, tile_size)
    tileset = tileset_path

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

def starcall_nokwargs(args):
    """
    Invoke first arg function with all other arguments.
    """

    fun = args[0]
    return fun(*args[1:])