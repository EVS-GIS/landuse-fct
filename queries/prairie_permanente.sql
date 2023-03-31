-- prairie permanente
WITH
    prairie AS (
		SELECT public.rpg_test.geom AS geom
		FROM public.rpg_test
		WHERE
			ST_Intersects(public.rpg_test.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
			AND public.rpg_test.code_group IN ('17', '18')
	),
	clip_prairie AS (
		SELECT ST_INTERSECTION(prairie.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
		FROM prairie
	),
	parts_prairie AS (
            SELECT (st_dump(st_union(geom))).geom
            FROM clip_prairie
	)
	SELECT row_number() over() AS gid, 4 AS value, removeHoles(geom, 500) AS geom
	FROM parts_prairie
	WHERE ST_GeometryType(geom) = 'ST_Polygon'