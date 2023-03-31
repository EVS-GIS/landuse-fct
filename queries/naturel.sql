-- naturel
WITH
    naturel AS (
		SELECT public.zone_de_vegetation.geom AS geom
		FROM public.zone_de_vegetation
		WHERE
			ST_Intersects(public.zone_de_vegetation.geom, ST_GeomFromText('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'))
			AND public.zone_de_vegetation.nature IN ('Haie', 'Lande ligneuse', 
													 'Forêt ouverte', 'Zone arborée')
	),
	clip_naturel AS (
		SELECT ST_INTERSECTION(naturel.geom, ST_GeomFromText('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})')) AS geom
		FROM naturel
	),
	parts_naturel AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_naturel
	)
	SELECT row_number() over() AS gid, 2 AS value, removeHoles(geom, 500) AS geom
	FROM parts_naturel
	WHERE ST_GeometryType(geom) = 'ST_Polygon'