-- infra
WITH
    route AS (
		SELECT 
			CASE
				WHEN public.troncon_de_route.largeur_de_chaussee < 8
					OR public.troncon_de_route.largeur_de_chaussee IS NULL
				THEN ST_BUFFER(public.troncon_de_route.geom, 4, 'join=bevel')
				ELSE ST_BUFFER(public.troncon_de_route.geom, public.troncon_de_route.largeur_de_chaussee/2, 'join=bevel')
			END AS geom
		FROM
			public.troncon_de_route
		WHERE
			ST_Intersects(public.troncon_de_route.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
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
            public.troncon_de_voie_ferree
        WHERE
            ST_Intersects(public.troncon_de_voie_ferree.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
            AND public.troncon_de_voie_ferree.position_par_rapport_au_sol IN ('0', '1')
    ),
    infra AS (
        SELECT geom FROM route
        UNION ALL SELECT geom FROM voie_ferree
    ),
	clip_infra AS (
		SELECT ST_INTERSECTION(infra.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
		FROM infra
	),
    parts_infra AS (
        SELECT (st_dump(st_union(geom))).geom
        FROM clip_infra
    )
	SELECT row_number() over() AS gid, 8 AS value, removeHoles(geom, 500) as geom
	FROM parts_infra
	WHERE ST_GeometryType(geom) = 'ST_Polygon'