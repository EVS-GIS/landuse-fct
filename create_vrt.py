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
from osgeo import gdal
from config.config import db_config, paths_config, parameters_config

# parameters
paths = paths_config()
params = parameters_config()
db_params = db_config()


def create_vrt_raster(tiles_dir, output_vrt):
    # Liste des fichiers GeoTIFF dans le répertoire d'entrée
    tiff_files = [os.path.join(tiles_dir, f) for f in os.listdir(tiles_dir) if f.endswith('.tif')]

    # Trier les fichiers GeoTIFF par ordre numérique de leur nom
    tiff_files.sort(key=lambda x: int(os.path.basename(x).split('_')[-1].split('.')[0]))

    # Créer un fichier raster virtuel à partir des fichiers GeoTIFF
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest')
    vrt = gdal.BuildVRT(output_vrt, tiff_files, options=vrt_options)

    # Fermer le fichier raster virtuel
    vrt = None

    print('Raster virtuel créé avec succès :', output_vrt)

create_vrt_raster('C:/Users/lmanie01/Documents/Projets/Mapdo/Data/landuse-fct/france_metropolitaine/tiles/', 
                  'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/landuse-fct/france_metropolitaine/landuse.vrt')