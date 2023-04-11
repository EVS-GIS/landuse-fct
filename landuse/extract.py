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
from multiprocessing import Pool
from pathlib import Path
# from config.config import db_config, paths_config, parameters_config
import geopandas
from sqlalchemy import create_engine, text
from tiles.tiles import starcall_nokwargs
import rasterio
from rasterio import Affine
import numpy
from rasterio import features
import click


# PAS COMPATIBLE AVEC WINDOWS!
def multiprocess_landuse_gid(
        tileset: str = 'tileset.gpkg',  # tileset path,
        gid_start: int = 1,
        gid_end:int = 1000,
        processes: int = 1, # number of processes
        tile_dir: str = './outputs/landuse/',
        resolution: int = 5,
        db_params: dict = {'host': 'localhost','port': '5432','database': 'mydb','user': 'myuser','password': 'mypwd'},
        queries_dir_path: str = './queries/', # The path to the directory containing the SQL query files
        landcover_tables: list = ['periurbain','foret','prairie_permanente','culture','bati','naturel','infra','banc_de_galets','surfaces_en_eau'], # A list of landcover tables to extract data from
        crs: str = '2154'
        ):
    
    # pg database connexion

    def arguments():

        gdf = geopandas.read_file(tileset)
        mask = (gdf['GID'] >= 1) & (gdf['GID'] <= 1000)
        tileset = gdf.loc[mask]
        
        for gid in tileset['GID']:
            yield (
                landuse_tile,
                gid,
                tileset,
                resolution,
                tile_dir,
                db_params,
                queries_dir_path,
                landcover_tables,
                crs
            )

    arguments = list(arguments())

    with Pool(processes=processes) as pool:

        pooled = pool.imap_unordered(starcall_nokwargs, arguments)
    
        with click.progressbar(pooled, length=len(arguments)) as iterator:
                for _ in iterator:
                    pass

# PAS COMPATIBLE AVEC WINDOWS!
def multiprocess_landuse(
        tileset: str = 'tileset.gpkg',  # tileset path,
        processes: int = 1, # number of processes
        tile_dir: str = './outputs/landuse/',
        resolution: int = 5,
        db_params: dict = {'host': 'localhost','port': '5432','database': 'mydb','user': 'myuser','password': 'mypwd'},
        queries_dir_path: str = './queries/', # The path to the directory containing the SQL query files
        landcover_tables: list = ['periurbain','foret','prairie_permanente','culture','bati','naturel','infra','banc_de_galets','surfaces_en_eau'], # A list of landcover tables to extract data from
        crs: str = '2154'
        ):
    
    # pg database connexion

    def arguments():
        
        for gid in geopandas.read_file(tileset)['GID']:
            yield (
                landuse_tile,
                gid,
                tileset,
                resolution,
                tile_dir,
                db_params,
                queries_dir_path,
                landcover_tables,
                crs
            )

    arguments = list(arguments())

    with Pool(processes=processes) as pool:

        pooled = pool.imap_unordered(starcall_nokwargs, arguments)
    
        with click.progressbar(pooled, length=len(arguments)) as iterator:
                for _ in iterator:
                    pass

def landuse_tile(
    gid: int = 1, # tile index
    tileset: str = './outputs/tileset.gpkg',  # tileset path
    resolution: int = 5, # outupt raster resolution
    tile_dir: str = './outputs/landuse/',
    db_params: dict = {'host': 'localhost','port': '5432','database': 'mydb','user': 'myuser','password': 'mypwd'},
    queries_dir_path: str = './queries/', # The path to the directory containing the SQL query files
    landcover_tables: list = ['periurbain','foret','prairie_permanente','culture','bati','naturel','infra','banc_de_galets','surfaces_en_eau'], # A list of landcover tables to extract data from
    crs: str = '2154'
):
    """
    Extract PostGIS data from a tile.

    :param gid: An integer .
    :param db_con_params: A dictionary containing the parameters required to connect to the PostgreSQL database.
    :param landcover_tables: A list of strings representing the names of the landcover tables to extract data from.
    :param resolution: an integer with the output raster resolution.
    :return: A raster containing the tile landuse.
    """

    # read 
    dataset = geopandas.read_file(tileset)
    tile = dataset[dataset['GID']==gid]
    id = f"{gid:05d}"
    raster_path = raster_path = os.path.join(tile_dir, 'LANDUSE_'+id+'.tif')

    if os.path.exists(raster_path):

        pass

    else:
        
        # Construct a connection string to the PostgreSQL database using the provided database parameters
        con = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        # Create a SQLAlchemy engine to connect to the database
        engine = create_engine(con)

        # Create an empty dictionary to store the extracted data
        dict_df = {}
        # Connect to the database and extract data from each landcover table
        with engine.connect() as condb:
            for layer in landcover_tables:
                # Open the SQL query file for the current landcover table
                with open(os.path.join(queries_dir_path, layer + ".sql"), "r", encoding="UTF-8") as file:
                    # Read the contents of the query file and replace the bounding box placeholders with the actual bounding box values
                    minx, miny, maxx, maxy = [float(val) for val in tile.total_bounds]
                    query = text(file.read().format(minx=minx, miny=miny, maxx=maxx, maxy=maxy))
                    # Extract the data from the database using the current query and store it in a GeoDataFrame
                    dict_df[layer] = geopandas.GeoDataFrame.from_postgis(query, condb, crs=crs, geom_col='geom')
                # Merge all features in the GeoDataFrame
                dict_df[layer] = dict_df[layer].dissolve()
                # Rename the geometry column to "geometry"
                dict_df[layer] = dict_df[layer].rename_geometry("geometry")
        # close connection
        engine.dispose()
        
        # create raser from the layers
        create_raster(geodataframe = tile, layers_dict = dict_df, 
                    raster_path = raster_path, 
                    resolution = resolution, default_value=2)

def create_raster(geodataframe, layers_dict, raster_path, resolution = 5, default_value=2, crs = '2154'):
    cell_size = int(resolution)
    # Obtenez l'emprise du GeoDataFrame
    bounds = geodataframe.total_bounds
    xmin, ymin, xmax, ymax = bounds

    # Calculez le nombre de cellules en x et y
    cols = int((xmax - xmin) / cell_size)
    rows = int((ymax - ymin) / cell_size)

    # Créez la transformation affine
    transform = Affine.translation(xmin, ymax) * Affine.scale(resolution, -resolution)

    profile = {
        'driver': 'GTiff',
        'dtype': rasterio.uint8,
        'nodata': 255,
        'compress': 'deflate',
        'count': 1,
        'height': rows,
        'width': cols,
        'crs': 'EPSG:'+ crs,
        'transform': transform,
        'dtype': rasterio.uint8
    }

    # Créez un nouveau raster vide
    with rasterio.open(
        raster_path,
        'w',
        **profile
    ) as dst:
        # Créez un tableau avec la valeur par défaut
        data = default_value * numpy.ones((rows, cols), dtype=rasterio.uint8)

        for gdf in layers_dict.values():
            if gdf.geometry.isnull().all()==False:
                shapes = ((geom,value) for geom, value in zip(gdf.geometry, gdf.value))
                raster = features.rasterize(shapes = shapes, out_shape = (rows, cols), fill=-1, transform=transform)
                mask = raster > -1
                data[mask] = raster[mask]
        # Écrire le tableau sur le raster
        dst.write(data, 1)