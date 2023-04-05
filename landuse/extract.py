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
from osgeo import gdal

# parameters
# paths = paths_config()
# params = parameters_config()
# db_params = db_config()

# tileset= os.path.join(paths['outputs_dir'], 'tileset.gpkg')
# db_con_params: dict = db_params
# landcover_tables: list = params['landcover_tables']
# queries_dir_path: str = paths['query_dir_path']
# tables_names: str = params['landcover_tables'] 

# tile  = geopandas.read_file(tileset).iloc[:1]

# for gid in geopandas.read_file(tileset)['GID']:
#     print(gid)

# max(geopandas.read_file(tileset)['GID'])
# geopandas.read_file(tileset)['GID'] == 1
# test = geopandas.read_file(tileset)
# test2 = test[test['GID']==1]

# extract_data(tileset = os.path.join(paths['outputs_dir'], paths['output_tileset_name']), processes = 1)

# create_vrt_raster(paths['tiles_dir'], os.path.join(paths['outputs_dir'], paths['output_raster_name']))



# PAS COMPATIBLE AVEC WINDOWS!
def extract_data(
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
                extract_data_tile,
                gid,
                tileset,
                tile_dir,
                resolution,
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

def extract_data_tile(
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
    
    # create raser from the layers
    create_raster(geodataframe = tile, layers_dict = dict_df, 
                  raster_path = os.path.join(tile_dir, 'LANDUSE_'+id+'.tif'), 
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

# create_raster(tile, os.path.join(paths['outputs_dir'], paths['output_raster_name']), 5, 2)

def create_vrt_raster(tiles_dir, output_vrt):
    # Liste des fichiers GeoTIFF dans le répertoire d'entrée
    tiff_files = [os.path.join(tiles_dir, f) for f in os.listdir(tiles_dir) if f.endswith('.tif')]

    # Trier les fichiers GeoTIFF par ordre numérique de leur nom
    tiff_files.sort(key=lambda x: int(os.path.basename(x).split('_')[-1].split('.')[0]))

    # Créer un fichier raster virtuel à partir des fichiers GeoTIFF
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest')
    vrt = gdal.BuildVRT(output_vrt, tiff_files, options=vrt_options)

    # Fermer le fichier raster virtuel
    vrt = None

    print('Raster virtuel créé avec succès :', output_vrt)