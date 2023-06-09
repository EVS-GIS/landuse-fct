-- periurbain
WITH peri AS (
    SELECT public.zone_d_habitation.geom AS geom
    FROM public.zone_d_habitation
    WHERE ST_Intersects(public.zone_d_habitation.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
),
erosion AS (
    SELECT st_buffer(st_union(peri.geom), -20, 'join=bevel') AS geom
    FROM peri
),
clip AS (
    SELECT ST_INTERSECTION(erosion.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
    FROM erosion
),
parts AS (
    SELECT (st_dump(clip.geom)).geom
    FROM clip
)
SELECT row_number() over() AS gid, 6 AS value, removeHoles(geom, 500) AS geom
FROM parts
WHERE ST_GeometryType(geom)='ST_Polygon'
AND ST_AREA(geom)>=2500;
