/*
Ressources : 
https://gis.stackexchange.com/questions/372931/creating-a-new-custom-postgis-function
pas concluant https://gis.stackexchange.com/questions/252012/filling-holes-by-acres-threshold-using-postgis
https://gis.stackexchange.com/questions/431664/deleting-small-holes-in-polygons-specifying-the-size-with-postgis
*/

CREATE OR REPLACE FUNCTION removeHoles (geom GEOMETRY, dist INT)
RETURNS GEOMETRY
AS 
$BODY$
SELECT ST_Collect( 
    ARRAY( SELECT ST_MakePolygon( 
              ST_ExteriorRing(geom),
              ARRAY( SELECT ST_ExteriorRing( rings.geom )
                      FROM ST_DumpRings(geom) AS rings
                      WHERE rings.path[1] > 0 AND ST_Area( rings.geom ) >= dist
            )
    )
    FROM ST_Dump(geom) AS poly ) 
  ) AS geom;
$BODY$
LANGUAGE SQL