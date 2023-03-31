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
        db_con_params = db_params,
        tile = 1,
        landcover_tables = params['landcover_tables'],
        queries_dir_path = paths['query_dir_path'],
        tables_names = params['landcover_tables']):
    
    con = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(con)

    dict_df = {}
    with engine.connect() as condb:
        for layer in landcover_tables:
            with open(os.path.join(queries_dir_path, layer + ".sql"), "r", encoding="UTF-8") as file:
                print(file)
                minx, miny, maxx, maxy = [float(val) for val in tile.total_bounds]
                query = text(file.read().format(minx=minx, miny=miny, maxx=maxx, maxy=maxy))
                dict_df[layer] = geopandas.GeoDataFrame.from_postgis(query, condb, crs=2154, geom_col=params['pg_col_name'])
            # merge all features
            dict_df[layer] = dict_df[layer].dissolve()
            dict_df[layer] = dict_df[layer].rename_geometry("geometry")
    
    return dict_df

# tileset= os.path.join(paths['outputs_dir'], 'tileset.gpkg')
# data = geopandas.read_file(tileset).iloc[:1]
# extract_data_tile(tile = data)

