-- prairie permanente
WITH
    prairie AS (
		SELECT public.rpg_parcelles_graphiques.geom AS geom
		FROM public.rpg_parcelles_graphiques, public.zone_etude
		WHERE
			ST_Intersects(public.rpg_parcelles_graphiques.geom, public.zone_etude.geom)
			AND public.rpg_parcelles_graphiques.code_group IN ('17', '18')
	),
	clip_prairie AS (
		SELECT ST_INTERSECTION(prairie.geom, zone_etude.geom) AS geom
		FROM prairie, zone_etude
	),
	parts_prairie AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_prairie
	)
	SELECT row_number() over() AS gid, 4 AS value, removeHoles(geom, 500) AS geom
	FROM parts_prairie
	WHERE ST_GeometryType(geom) = 'ST_Polygon'