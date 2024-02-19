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
from tiles.tiles import check_tiles_outputs

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()

check_tiles_outputs(tileset_path = os.path.join(paths['outputs_dir'], paths['tileset_name']),
                    tiles_dir_path = paths['tiles_dir'])