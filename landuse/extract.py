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
# multiprocess with tiles selection
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
        crs: str = '2154',
        study_area_path:str = './inputs/zone_etude.gpkg'
        ):
    
    # pg database connexion

    def arguments():

        # gdf = geopandas.read_file(tileset)
        # mask = (gdf['GID'] >= gid_start) & (gdf['GID'] <= gid_end)
        # tileset = gdf.loc[mask]
        
        for gid in geopandas.read_file(tileset).loc[(geopandas.read_file(tileset)['GID'] >=gid_start) & (geopandas.read_file(tileset)['GID'] <= gid_end), 'GID']:
            yield (
                landuse_tile,
                gid,
                tileset,
                resolution,
                tile_dir,
                db_params,
                queries_dir_path,
                landcover_tables,
                crs,
                study_area_path
            )

    arguments = list(arguments())

    with Pool(processes=processes) as pool:

        pooled = pool.imap_unordered(starcall_nokwargs, arguments)
    
        with click.progressbar(pooled, length=len(arguments)) as iterator:
                for _ in iterator:
                    pass

# PAS COMPATIBLE AVEC WINDOWS!
def multiprocess_landuse(
        tileset: str = 'tileset.gpkg',  # Path to the tileset
        processes: int = 1, # Number of processes
        tile_dir: str = './outputs/landuse/', # Directory where the output files will be written
        resolution: int = 5, # Resolution of the landuse rasters
        db_params: dict = {'host': 'localhost','port': '5432','database': 'mydb','user': 'myuser','password': 'mypwd'}, # Database connection parameters
        queries_dir_path: str = './queries/', # The path to the directory containing the SQL query files
        landcover_tables: list = ['periurbain','foret','prairie_permanente','culture','bati','naturel','infra','banc_de_galets','surfaces_en_eau'], # A list of landcover tables to extract data from
        crs: str = '2154', # EPSG code of the tileset
        study_area_path:str = './inputs/zone_etude.gpkg' # Path to the study area shapefile
        ) -> None:
    """
    This function extracts the landuse data from a tileset using SQL queries and
    writes the result to a raster file. It uses multiple processes to speed up the
    computation.

    Parameters:
    -----------
    tileset: str
        Path to the tileset GeoPackage file.
    processes: int
        Number of processes to use for parallel execution.
    tile_dir: str
        Path to the directory where the output tiles will be saved.
    resolution: int
        The resolution of the landuse classification in meters.
    db_params: dict
        A dictionary containing the parameters for the database connection.
        The following keys are required: host, port, database, user, password.
    queries_dir_path: str
        The path to the directory containing the SQL query files.
    landcover_tables: list
        A list of landcover tables to extract data from.
    crs: str
        The EPSG code of the tileset.
    study_area_path: str
        Path to the shapefile of the study area.

    Returns:
    --------
    None
    """
    
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
                crs,
                study_area_path
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
    crs: str = '2154',
    study_area_path:str = './inputs/zone_etude.gpkg'
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
    raster_path = os.path.join(tile_dir, 'LANDUSE_'+id+'.tif')

    if os.path.exists(raster_path):

        pass

    else:
        
        # Construct a connection string to the PostgreSQL database using the provided database parameters
        con = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        # Create a SQLAlchemy engine to connect to the database
        engine = create_engine(con, pool_pre_ping=True)

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
        # close connection and free ressource
        engine.dispose()
        
        # create raser from the layers
        create_raster(geodataframe = tile, layers_dict = dict_df, 
                    raster_path = raster_path, 
                    resolution = resolution, default_value=2, crs = '2154', study_area_path = study_area_path)

def create_raster(
        geodataframe:geopandas.GeoDataFrame, # tile geodataframe 
        layers_dict:dict, 
        raster_path:str = './outputs/landuse/', 
        resolution:int = 5, 
        default_value:int =2, 
        crs:str = '2154', 
        study_area_path:str = './inputs/zone_etude.gpkg'):
    """
    Creates a new raster file from a GeoDataFrame and a dictionary of layers.

    Parameters:
    geodataframe (GeoDataFrame): The GeoDataFrame containing the geometry for the new raster.
    layers_dict (dictionary): A dictionary of layers containing the geometry and value to rasterize.
    raster_path (string): The path to save the new raster.
    resolution (int): The resolution of the new raster. Default is 5.
    default_value (int): The default value to use when creating the raster. Default is 2.
    crs (string): The coordinate reference system of the new raster. Default is '2154'.
    study_area_path (string): The path to the study area GeoPackage file. Default is './inputs/zone_etude.gpkg'.
    """

    # Calculate cell size from resolution parameter
    cell_size = int(resolution)

    # Get the bounds of the GeoDataFrame
    bounds = geodataframe.total_bounds
    xmin, ymin, xmax, ymax = bounds

    # Calculate the number of cells in x and y directions
    cols = int((xmax - xmin) / cell_size)
    rows = int((ymax - ymin) / cell_size)

    # Create the affine transformation for the raster
    transform = Affine.translation(xmin, ymax) * Affine.scale(resolution, -resolution)

    # Create the profile for the new raster
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

    # Create a new empty raster file
    with rasterio.open(raster_path, 'w', **profile) as dst:
        # Create a data array with the default value
        data = default_value * numpy.ones((rows, cols), dtype=rasterio.uint8)

        # Read the study area GeoPackage file
        gdf_study_area = geopandas.read_file(study_area_path)

        # Set the nodata value for the new raster
        nodata_value = 255

        # Rasterize each layer in the layers dictionary
        for gdf in layers_dict.values():
            # Check if the geometry column is not null
            if gdf.geometry.isnull().all() == False:
                # Create shapes and rasterize
                shapes = ((geom,value) for geom, value in zip(gdf.geometry, gdf.value))
                raster = features.rasterize(shapes = shapes, out_shape = (rows, cols), fill=-1, transform=transform)
                # Create a mask to update the data array
                mask = raster > -1
                data[mask] = raster[mask]

        # Mask the data array with the study area geometry
        data = numpy.where(rasterio.features.geometry_mask(gdf_study_area.geometry, out_shape=data.shape, transform=transform, invert=False), nodata_value, data)

        # Write the data array to the raster file
        dst.write(data, 1)
