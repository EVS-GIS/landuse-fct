-- foret
WITH
    foret AS (
		SELECT public.zone_de_vegetation.geom AS geom
		FROM public.zone_de_vegetation
		WHERE
			ST_Intersects(public.zone_de_vegetation.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
			AND public.zone_de_vegetation.nature IN ('Bois', 'Peupleraie', 
													'Forêt fermée mixte',
													'Forêt fermée de feuillus', 
													'Forêt fermée de conifères')
	),
	dilatation AS (
            SELECT ST_SnapToGrid(st_buffer(geom, 20, 'join=bevel'), 0.001) AS geom
            FROM foret
        ),
	erosion AS (
		SELECT st_buffer(st_union(geom), -20, 'join=bevel') AS geom
		FROM dilatation
	),
    clip_foret AS (
		SELECT st_intersection(erosion.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
		FROM erosion
	),
	parts_foret AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_foret
	)
	SELECT row_number() over() AS gid, 3 AS value, removeHoles(geom, 500) AS geom
	FROM parts_foret
	WHERE ST_GeometryType(geom) = 'ST_Polygon'
		AND ST_AREA(geom) >=2500;