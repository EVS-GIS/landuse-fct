-- bati
WITH
	bati AS (
			SELECT public.batiment.geom AS geom 
			FROM public.batiment, public.zone_etude
			WHERE ST_Intersects(public.batiment.geom, public.zone_etude.geom)
		UNION 
			SELECT public.construction_surfacique.geom AS geom 
			FROM public.construction_surfacique, public.zone_etude
			WHERE st_intersects(public.construction_surfacique.geom, public.zone_etude.geom)
		UNION 
			SELECT public.cimetiere.geom AS geom 
			FROM public.cimetiere, public.zone_etude
			WHERE st_intersects(public.cimetiere.geom, public.zone_etude.geom)
		UNION 
			SELECT public.reservoir.geom AS geom 
			FROM public.reservoir, public.zone_etude
			WHERE st_intersects(public.reservoir.geom, public.zone_etude.geom)
		UNION 
			-- polyligne, create a 2m buffer 
			SELECT ST_BUFFER(public.construction_lineaire.geom, 2) AS geom
			FROM public.construction_lineaire, public.zone_etude
			WHERE st_intersects(ST_BUFFER(public.construction_lineaire.geom, 2), public.zone_etude.geom)
		UNION 
			SELECT public.piste_d_aerodrome.geom AS geom
			FROM public.piste_d_aerodrome, public.zone_etude
			WHERE st_intersects(public.piste_d_aerodrome.geom, public.zone_etude.geom)
		UNION 
			SELECT public.equipement_de_transport.geom AS geom
			FROM public.equipement_de_transport, public.zone_etude
			WHERE st_intersects(public.equipement_de_transport.geom, public.zone_etude.geom)
			AND nature IN ('Parking', 'Péage')
		UNION 
			SELECT public.zone_d_activite_ou_d_interet.geom AS geom
			FROM public.zone_d_activite_ou_d_interet, public.zone_etude
			WHERE st_intersects(public.zone_d_activite_ou_d_interet.geom, public.zone_etude.geom)
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
		SELECT st_intersection(buff.geom, public.zone_etude.geom) AS geom
		FROM buff, public.zone_etude
	),
	parts_bati AS (
		SELECT (st_dump(clip_bati.geom)).geom
		FROM clip_bati
	)
	SELECT row_number() over() AS gid, 7 as value, removeHoles(geom, 2000) as geom
	FROM parts_bati
	WHERE ST_GeometryType(geom) = 'ST_Polygon'
		AND ST_AREA(geom) >=2500