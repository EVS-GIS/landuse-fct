-- surface en eau
WITH
    eau AS (
		SELECT public.surface_hydrographique.geom AS geom
		FROM public.surface_hydrographique
		WHERE
			ST_Intersects(public.surface_hydrographique.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
			AND public.surface_hydrographique.persistance LIKE 'Permanent'
			AND public.surface_hydrographique.nature NOT LIKE 'Glacier, névé'
	),
	clip_eau AS (
		SELECT ST_INTERSECTION(eau.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
		FROM eau
	),
	parts_eau AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_eau
	)
	SELECT row_number() over() AS gid, 0 as value, geom
	FROM parts_eau
	WHERE ST_GeometryType(geom) = 'ST_Polygon'