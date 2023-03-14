-- banc de galets
WITH
    galet AS (
		SELECT public.surface_hydrographique.geom AS geom
		FROM public.surface_hydrographique, public.zone_etude
		WHERE
			ST_Intersects(public.surface_hydrographique.geom, public.zone_etude.geom)
			AND public.surface_hydrographique.persistance LIKE 'Intermittent'
	),
	clip_galet AS (
		SELECT ST_INTERSECTION(galet.geom, zone_etude.geom) AS geom
		FROM galet, zone_etude
	),
	parts_galet AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_galet
	)
	SELECT row_number() over() AS gid, 1 as value, geom
	FROM parts_galet
	WHERE ST_GeometryType(geom) = 'ST_Polygon'