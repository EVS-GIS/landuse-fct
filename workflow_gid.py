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
             gid_start = 5001,
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