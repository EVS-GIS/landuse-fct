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
from config.config import db_config, paths_config, parameters_config
import geopandas
from sqlalchemy import create_engine, text
from tiles.tiles import starcall_nokwargs

# list of landuse layers in the overlay order
# zone_etude il to compute the empty cells remaining in the spatial extent

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()
# wd_path = Path(os.getcwd())
# queries_dir_path = os.path.join(wd_path, queries_dir_name)
# dict_df = {}

def extract_data(
        db_con_params = db_params,
        tables_names = params['landcover_tables'],
        tileset= os.path.join(paths['outputs_dir'], 'tileset.gpkg'),
        processes=1):
    
    # pg database connexion

    def arguments():
        
        for row in geopandas.read_file(tileset).iterrows():
            yield (
                extract_data_tile(tile=row)
            )

    arguments = list(arguments())

    with Pool(processes=processes) as pool:
        pooled = pool.imap_unordered(starcall_nokwargs, arguments)

def extract_data_tile(
    tile=1,  # The tile to extract data from
    db_con_params: dict = db_params,  # The parameters to connect to the PostgreSQL database
    landcover_tables: list = params['landcover_tables'],  # A list of landcover tables to extract data from
    queries_dir_path: str = paths['query_dir_path'],  # The path to the directory containing the SQL query files
    tables_names: str = params['landcover_tables']  # The names of the tables to extract data from
) -> dict:
    """
    Extract PostGIS data from a tile.

    :param tile: A GeoPandas GeoDataFrame object representing the tile from the tileset to extract data from.
    :param db_con_params: A dictionary containing the parameters required to connect to the PostgreSQL database.
    :param landcover_tables: A list of strings representing the names of the landcover tables to extract data from.
    :param queries_dir_path: A string representing the path to the directory containing the SQL query files.
    :param tables_names: A string representing the names of the tables to extract data from.
    :return: A dictionary containing the extracted data.
    """
    
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
                dict_df[layer] = geopandas.GeoDataFrame.from_postgis(query, condb, crs=params['crs'], geom_col=params['pg_col_name'])
            # Merge all features in the GeoDataFrame
            dict_df[layer] = dict_df[layer].dissolve()
            # Rename the geometry column to "geometry"
            dict_df[layer] = dict_df[layer].rename_geometry("geometry")
    
    # Return the dictionary containing the extracted data
    return dict_df

# A continuer directement avec a rasterisation