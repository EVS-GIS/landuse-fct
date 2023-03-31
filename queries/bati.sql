-- bati
WITH
	bati AS (
			SELECT public.batiment.geom AS geom 
			FROM public.batiment
			WHERE ST_Intersects(public.batiment.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
		UNION 
			SELECT public.construction_surfacique.geom AS geom 
			FROM public.construction_surfacique
			WHERE st_intersects(public.construction_surfacique.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
		UNION 
			SELECT public.cimetiere.geom AS geom 
			FROM public.cimetiere
			WHERE st_intersects(public.cimetiere.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
		UNION 
			SELECT public.reservoir.geom AS geom 
			FROM public.reservoir
			WHERE st_intersects(public.reservoir.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
		UNION 
			-- polyligne, create a 2m buffer 
			SELECT ST_BUFFER(public.construction_lineaire.geom, 2) AS geom
			FROM public.construction_lineaire
			WHERE st_intersects(ST_BUFFER(public.construction_lineaire.geom, 2), ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
		UNION 
			SELECT public.piste_d_aerodrome.geom AS geom
			FROM public.piste_d_aerodrome
			WHERE st_intersects(public.piste_d_aerodrome.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
		UNION 
			SELECT public.equipement_de_transport.geom AS geom
			FROM public.equipement_de_transport
			WHERE st_intersects(public.equipement_de_transport.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
			AND nature IN ('Parking', 'Péage')
		UNION 
			SELECT public.zone_d_activite_ou_d_interet.geom AS geom
			FROM public.zone_d_activite_ou_d_interet
			WHERE st_intersects(public.zone_d_activite_ou_d_interet.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154))
			AND nature LIKE 'Usine'
	),
	-- closing process
	dilatation AS (
		SELECT st_buffer(bati.geom, 20, 'join=bevel') AS geom
		FROM bati
	),
	erosion AS (
		SELECT st_buffer(st_union(dilatation.geom), -20, 'join=bevel') AS geom
		FROM dilatation
	),
	buff AS (
		SELECT ST_buffer(erosion.geom, 5, 'join=bevel') AS geom
		FROM erosion
	),
	clip_bati AS (
		SELECT st_intersection(buff.geom, ST_POLYGON('LINESTRING({minx} {miny},{maxx} {miny},{maxx} {maxy}, {minx} {maxy}, {minx} {miny})'::geometry, 2154)) AS geom
		FROM buff
	),
	parts_bati AS (
		SELECT (st_dump(clip_bati.geom)).geom
		FROM clip_bati
	)
	SELECT row_number() over() AS gid, 7 as value, removeHoles(geom, 2000) as geom
	FROM parts_bati
	WHERE ST_GeometryType(geom) = 'ST_Polygon'
		AND ST_AREA(geom) >=2500