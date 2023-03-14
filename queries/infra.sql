-- infra
WITH
    route AS (
		SELECT 
			CASE
				WHEN public.troncon_de_route.largeur_de_chaussee < 4
					OR public.troncon_de_route.largeur_de_chaussee IS NULL
				THEN ST_BUFFER(public.troncon_de_route.geom, 2, 'join=bevel')
				ELSE ST_BUFFER(public.troncon_de_route.geom, public.troncon_de_route.largeur_de_chaussee/2, 'join=bevel')
			END AS geom
		FROM
			public.troncon_de_route,
			public.zone_etude
		WHERE
			ST_Intersects(public.troncon_de_route.geom, public.zone_etude.geom)
			AND public.troncon_de_route.position_par_rapport_au_sol IN ('0', '1')
			AND (public.troncon_de_route.nature IN (
				 	'Bretelle', 
				 	'Rond-point', 
				 	'Route à 1 chaussée',
				 	'Route à 2 chaussées',
				 	'Type autoroutier'))
		),
    voie_ferree AS (
        SELECT
            CASE
                WHEN public.troncon_de_voie_ferree.nature LIKE 'LGV'
                THEN ST_BUFFER(public.troncon_de_voie_ferree.geom, 15, 'join=bevel')
                WHEN public.troncon_de_voie_ferree.nature LIKE 'Voie ferrée principale'
                THEN ST_BUFFER(public.troncon_de_voie_ferree.geom, 8, 'join=bevel')
                ELSE ST_BUFFER(public.troncon_de_voie_ferree.geom, 5, 'join=bevel')
            END AS geom
        FROM
            public.troncon_de_voie_ferree,
            public.zone_etude
        WHERE
            ST_Intersects(public.troncon_de_voie_ferree.geom, public.zone_etude.geom)
            AND public.troncon_de_voie_ferree.position_par_rapport_au_sol IN ('0', '1')
    ),
    infra AS (
        SELECT geom FROM route
        UNION ALL SELECT geom FROM voie_ferree
    ),
	clip_infra AS (
		SELECT ST_INTERSECTION(infra.geom, zone_etude.geom) AS geom
		FROM infra, zone_etude
	),
    parts_infra AS (
        SELECT (st_dump(st_union(geom))).geom
        FROM clip_infra
    )
	SELECT row_number() over() AS gid, 8 AS value, removeHoles(geom, 500) as geom
	FROM parts_infra
	WHERE ST_GeometryType(geom) = 'ST_Polygon'