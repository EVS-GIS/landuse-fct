import os
from config.config import db_config, paths_config, parameters_config
from tiles.tiles import check_tiles_outputs

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()

check_tiles_outputs(tileset_path = os.path.join(paths['outputs_dir'], paths['tileset_name']),
                    tiles_dir_path = paths['tiles_dir'])