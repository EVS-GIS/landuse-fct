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
from config.config import db_config, paths_config, parameters_config
from tiles.tiles import CreateTileset
from landuse.extract import multiprocess_landuse_gid

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()

# create tileset from input spatial extent
# CreateTileset(
#     tile_size = params['tile_size'],
#     study_area_path = os.path.join(paths['inputs_dir'], paths['study_area_name']),
#     tileset_path = os.path.join(paths['outputs_dir'], paths['tileset_name']),
#     crs = params['crs'])

# create landuse raster
multiprocess_landuse_gid(tileset = os.path.join(paths['outputs_dir'], paths['tileset_name']), 
             gid_start = 1,
             gid_end = 5866,
             processes = params['processes'],
             tile_dir = paths['tiles_dir'],
             resolution = params['resolution'],
             db_params = db_params,
             queries_dir_path = paths['query_dir_path'],
             landcover_tables = params['landcover_tables'],
             crs = params['crs'],
             study_area_path = os.path.join(paths['inputs_dir'], paths['study_area_name']))

# create_vrt_raster(paths['tiles_dir'],  os.path.join(paths['outputs_dir'], paths['vrt_name']))