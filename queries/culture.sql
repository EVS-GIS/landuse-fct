-- culture
WITH
    grandes_cultures AS (
		SELECT public.rpg_parcelles_graphiques.geom AS geom
		FROM public.rpg_parcelles_graphiques, public.zone_etude
		WHERE
			ST_Intersects(public.rpg_parcelles_graphiques.geom, public.zone_etude.geom)
			AND public.rpg_parcelles_graphiques.code_group IN 
				('1', '2', '3', '4', '5', '6', '7', '8', '9',
				'11', '14', '15', '16', '24', '25', '26', '28')
	),
	arboriculture AS (
		SELECT public.rpg_parcelles_graphiques.geom AS geom
		FROM public.rpg_parcelles_graphiques, public.zone_etude
		WHERE
			ST_Intersects(public.rpg_parcelles_graphiques.geom, public.zone_etude.geom)
			AND public.rpg_parcelles_graphiques.code_group IN ('20', '22', '23')
	),
	vigne AS (
		SELECT public.rpg_parcelles_graphiques.geom AS geom
		FROM public.rpg_parcelles_graphiques, public.zone_etude
		WHERE
			ST_Intersects(public.rpg_parcelles_graphiques.geom, public.zone_etude.geom)
			AND public.rpg_parcelles_graphiques.code_group IN ('21')
	),
	culture AS (
		SELECT geom FROM grandes_cultures
		UNION ALL SELECT geom FROM arboriculture
		UNION ALL SELECT geom FROM vigne
	),
	clip_culture AS (
		SELECT ST_INTERSECTION(culture.geom, zone_etude.geom) AS geom
		FROM culture, zone_etude
	),
	parts_culture AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_culture
	)
	SELECT row_number() over() AS gid, 5 AS value, removeHoles(geom, 500) AS geom
	FROM parts_culture
	WHERE ST_GeometryType(geom) = 'ST_Polygon'