# coding: utf-8

"""
Postgresql / PostGIS database preparation after BD TOPO and RPG has been imported
Warning, the operation could be time consuming if you have loaded the whole France

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

# import modules
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import text
from config.config import config

# paths
wd_path = Path(os.getcwd())
queries_utils_dir_path = os.path.join(wd_path, "queries", "utils")
pg_utils_function = ['rename_if_exist.sql', 'add_pkey_if_not_exist.sql', 
                     'create_geom_index_if_not_exist.sql', 'removeholes.sql']
harmonize_srid_geomcol_filename = "harmonize_srid_geom_col_name.sql"
set_pkey_index_filename = "tables_pkey_index.sql"

# pg database connexion
params = config()
con = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
engine = create_engine(con)

# create function from utils files
for queryfile in pg_utils_function:
    with engine.connect() as condb:
        with open(os.path.join(queries_utils_dir_path, queryfile), "r", encoding="UTF-8") as file:
            query = text(file.read())
            engine.execute(query.execution_options(autocommit=True))

# harmonize SRID (set to 2154) and geometry column name (set to geom)
with engine.connect() as condb:
        with open(os.path.join(queries_utils_dir_path, harmonize_srid_geomcol_filename), "r", encoding="UTF-8") as file:
            query = text(file.read())
            engine.execute(query.execution_options(autocommit=True))

# create primary key and spatial index
with engine.connect() as condb:
        with open(os.path.join(queries_utils_dir_path, set_pkey_index_filename), "r", encoding="UTF-8") as file:
            query = text(file.read())
            engine.execute(query.execution_options(autocommit=True))