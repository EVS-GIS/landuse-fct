#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
-------------------------------------------------------------------------------
"This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-------------------------------------------------------------------------------
"""

import os
import numpy as np
import fiona
import fiona.crs
import geopandas
from shapely.geometry import Polygon

def CreateTileset(tile_size: float = 1000.0,
                  study_area_path: str = './inputs/zone_etude.gpkg',
                  tileset_path: str = './outputs/tileset.gpkg',
                  crs = '2154'):
    """
    Creates a GeoPackage tileset containing rectangular polygons that tile the bounding box of the given
    study area according to a resolution parameter.

    :param tile_size: float, default=1000.0
        The width and height of the rectangular polygons in the tilesets.
    :param study_area_path: str, default='./inputs/zone_etude.gpkg'
        The path to the study area file in GeoPackage format.
    :param tileset_path: str, default='./outputs/tileset.gpkg'
        The path to the tileset file in GeoPackage format.
    :param crs: str or int, default='2154'
        The CRS code or name for the tileset.
    :return: None
    """

    # Define the schema for the output GeoPackage.
    schema = {
        'geometry': 'Polygon', 
        'properties': {
            'GID': 'int',
            'ROW': 'int',
            'COL': 'int',
            'X0': 'float',
            'Y0': 'float'
        }
    }

    # Define options for the output GeoPackage.
    options = dict(
        driver='GPKG',
        schema=schema,
        crs=fiona.crs.from_epsg(crs)
    )

    # Read the study area file to extract the bounding box coordinates.
    study_area = geopandas.read_file(study_area_path)
    minx, miny, maxx, maxy = [float(val) for val in study_area.total_bounds]

    # Add the tile size to the maximum coordinates to get the whole extent and above.
    maxx += tile_size
    maxy += tile_size

    # Create a mesh grid of the bounding box coordinates with a spacing of `tile_size`.
    gx, gy = np.arange(minx, maxx, tile_size), np.arange(miny, maxy, tile_size)

    # Create the tileset file and write each tile feature.
    gid = 1
    with fiona.open(tileset_path, 'w', **options) as dst:
        for i in range(len(gx)-1):
            for j in range(len(gy)-1):
                # Define the coordinates of the tile polygon.
                coordinates = [(gx[i],gy[j]),(gx[i],gy[j+1]),(gx[i+1],gy[j+1]),(gx[i+1],gy[j])]

                # Define the feature properties and geometry.
                feature = {
                    'geometry': {
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

                # Write only features that intersect with the study area.
                if study_area.intersects(Polygon(coordinates)).any() == True:
                    dst.write(feature)
                    gid += 1


def starcall_nokwargs(args):
    """
    Invoke first arg function with all other arguments.
    """

    fun = args[0]
    return fun(*args[1:])

def check_tiles_outputs(
        tileset_path: str,
        tiles_dir_path: str):
    """
    Check if all files in outputs folder has been created
    """
    # read tileset
    tileset = geopandas.read_file(tileset_path)
    missing_tile = []
    
    # generate the tile name from gid in tileset then check fi the file exist in tiles output folder
    for gid in tileset['GID']:
        id = f"{gid:05d}"
        tile_name = 'LANDUSE_'+str(id)+'.tif'
        file_path = os.path.join(tiles_dir_path, tile_name)
        if os.path.isfile(file_path)==False:
            missing_tile.append(tile_name)
    # return the missing tiles in tilset if missing_file not empty
    if missing_tile:
        return False, print(missing_tile)
    else:
        return True, print('All tiles created for tileset')
