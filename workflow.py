import os
from config.config import db_config, paths_config, parameters_config, raster_config
from landuse import extract

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()
rast_params = raster_config()

extract.extract_data(tileset = os.path.join(paths['outputs_dir'], paths['output_tileset_name']), processes = 4)