"""
Module to extract data and rasterize tile
"""

from config.config import db_config, paths_config, parameters_config, raster_config

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()
rast_params = raster_config()