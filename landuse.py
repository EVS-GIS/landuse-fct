# coding: utf-8

"""
Warning, the operation could be time consuming if you have loaded the whole France
Program to create the Christophe Rousson map from the BD TOPO and the RPG

Ressources geocube : 
- https://gis.stackexchange.com/questions/151339/rasterize-a-shapefile-with-geopandas-or-fiona-python
- https://github.com/corteva/geocube
- https://corteva.github.io/geocube/stable/getting_started.html


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
from config.config import db_config, paths_config
import geopandas
import pandas
from sqlalchemy import create_engine, text
# rasterize geodataframe
from geocube.api.core import make_geocube
import rasterio.merge
from shapely.ops import snap

# variables
queries_dir_name = "queries"
geometry_col_name = "geom"
# list of landuse layers in the overlay order
# zone_etude il to compute the empty cells remaining in the spatial extent
landcover_list = ["surfaces_en_eau", "banc_de_galets", "infra", "naturel",
                  "bati", "culture", "prairie_permanente", "foret", "periurbain", "zone_etude"]

# pg database connexion
db_params = db_config()
con = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
engine = create_engine(con)

# paths
paths_params = paths_config()
wd_path = Path(os.getcwd())
queries_dir_path = os.path.join(wd_path, queries_dir_name)
dict_df = {}

# store all layer in dict as geodataframe and merge all features in one
with engine.connect() as condb:
    for layer in landcover_list:
        with open(os.path.join(queries_dir_path, layer + ".sql"), "r", encoding="UTF-8") as file:
            print(file)
            query = text(file.read())
            dict_df[layer] = geopandas.GeoDataFrame.from_postgis(query, condb, crs=2154, geom_col=geometry_col_name)
        # merge all features
        dict_df[layer] = dict_df[layer].dissolve()
        dict_df[layer] = dict_df[layer].rename_geometry("geometry")

# do different for each layer in the overlay order
n=1
# copy layers without zone_etude
keys_to_exclude = "zone_etude"
dict_diff = {k:v for k,v in dict_df.items() if k not in keys_to_exclude}
# difference mask on layers
for layer in landcover_list[1:-1]:
    for i in range (n):
        # print("i= "+str(i))
        # print("n= "+str(n))
        # print(layer)
        # print(landcover_list[i])
        dict_diff[layer]["geometry"] = dict_df[layer].loc[:,"geometry"].difference(dict_df[landcover_list[i]].loc[:,"geometry"], align=True)
    n+=1

# merging
merge = pandas.concat(dict_diff.values(), ignore_index=True)
# drop none geometry
merge = merge.dropna(subset=['geometry']).reset_index(drop=True)
# close sliver gap by closing (dilatation + erosion)
merge['geometry'] = merge.buffer(0.0001, 1, join_style="mitre").buffer(0.0001, 1, join_style="mitre")

# get the empty area in spatial extent
diff_zone_etude = dict_df["zone_etude"].loc[:,"geometry"].difference(merge.dissolve().loc[:,"geometry"], align=True)
diff_zone_etude = geopandas.GeoDataFrame(geometry=geopandas.GeoSeries(diff_zone_etude))
# empty area are define like naturel
diff_zone_etude.insert(0, "value", 2)
# merge all
merge = pandas.concat([merge, diff_zone_etude], ignore_index=True)
merge = merge.dropna(subset=['geometry']).reset_index(drop=True)

# save vector
merge.to_file(os.path.join(paths_params['outputs_dir'], paths_params['output_vector_name']), driver="GPKG", layer="merge")

# rasterisation en xarray
out_grid = make_geocube(
    vector_data=merge,
    measurements=["value"],
    resolution=(-5, 5),
)
# export en raster
out_grid["value"].rio.to_raster(raster_path = os.path.join(paths_params['outputs_dir'], paths_params['output_raster_name']), dtype = "uint8", nodata= 255)

print("end")
