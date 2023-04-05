import os
from config.config import db_config, paths_config, parameters_config
from tiles.tiles import CreateTileset
from landuse.extract import multiprocess_landuse, landuse_tile

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()

# processes cores
processes = params['processes']

# create tileset from input spatial extent
CreateTileset(
    tile_size = params['tile_size'],
    zone_etude_path = os.path.join(paths['inputs_dir'], paths['zone_etude_name']),
    tileset_path = os.path.join(paths['outputs_dir'], paths['tileset_name']),
    crs = params['crs'])

# landuse_tile(
#     gid = 3, # tile index
#     tileset = os.path.join(paths['outputs_dir'], paths['tileset_name']),  # tileset path
#     resolution = params['resolution'], # outupt raster resolution
#     tile_dir = paths['tiles_dir'],
#     db_params = db_params,
#     queries_dir_path = paths['query_dir_path'],
#     landcover_tables = params['landcover_tables'],
#     crs = params['crs'])


# create landuse raster
multiprocess_landuse(tileset = os.path.join(paths['outputs_dir'], paths['tileset_name']), 
             processes = processes,
             tile_dir = paths['tiles_dir'],
             resolution = params['resolution'],
             db_params = db_params,
             queries_dir_path = paths['query_dir_path'],
             landcover_tables = params['landcover_tables'],
             crs = params['crs'])

# create_vrt_raster(paths['tiles_dir'],  os.path.join(paths['outputs_dir'], paths['vrt_name']))