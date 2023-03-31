-- banc de galets
WITH
    galet AS (
		SELECT public.surface_hydrographique.geom AS geom
		FROM public.surface_hydrographique
		WHERE
			ST_Intersects(public.surface_hydrographique.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
			AND public.surface_hydrographique.persistance LIKE 'Intermittent'
	),
	clip_galet AS (
		SELECT ST_INTERSECTION(galet.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
		FROM galet
	),
	parts_galet AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_galet
	)
	SELECT row_number() over() AS gid, 1 as value, geom
	FROM parts_galet
	WHERE ST_GeometryType(geom) = 'ST_Polygon'