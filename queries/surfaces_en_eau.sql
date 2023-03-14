-- surface en eau
WITH
    eau AS (
		SELECT public.surface_hydrographique.geom AS geom
		FROM public.surface_hydrographique, public.zone_etude
		WHERE
			ST_Intersects(public.surface_hydrographique.geom, public.zone_etude.geom)
			AND public.surface_hydrographique.persistance LIKE 'Permanent'
			AND public.surface_hydrographique.nature NOT LIKE 'Glacier, névé'
	),
	clip_eau AS (
		SELECT ST_INTERSECTION(eau.geom, zone_etude.geom) AS geom
		FROM eau, zone_etude
	),
	parts_eau AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_eau
	)
	SELECT row_number() over() AS gid, 0 as value, geom
	FROM parts_eau
	WHERE ST_GeometryType(geom) = 'ST_Polygon'