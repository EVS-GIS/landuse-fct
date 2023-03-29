/*
Warning, the operation could be time consuming if you have loaded the whole France
Harmonize geom column name to geom and SRID to 2154
Raw SQL data from BD TOPO, col name = geometrie (change to geom) and SRID 4326 (change to 2154)

Check geometrie type and SRID example
SELECT ST_GeometryType(geom) FROM public.troncon_de_route LIMIT 10;
SELECT ST_SRID(geom) FROM surface_hydrographique LIMIT 1;
*/

-- BD TOPO and zone_etude
DO
$do$
DECLARE
  tbl text;
  arr text[] := array['public.batiment', 'public.construction_surfacique', 'public.cimetiere','public.reservoir',
      'public.construction_lineaire', 'public.piste_d_aerodrome', 'public.surface_hydrographique',
      'public.troncon_de_route', 'public.troncon_de_voie_ferree', 'public.zone_de_vegetation',
      'public.equipement_de_transport', 'public.zone_d_activite_ou_d_interet', 'public.zone_d_habitation', 'public.zone_etude'];
	colname text := 'geometrie';
	new_colname text := 'geom';
	geomtype text :='MULTIPOLYGON';
BEGIN
   FOREACH tbl IN ARRAY arr
   LOOP
   	RAISE NOTICE 'Table : %', tbl;
    -- if geometry column is geometrie in tables list, rename to geom, else do nothing
   	EXECUTE format('SELECT rename_if_exist(%L, %L, %L)', tbl, colname, new_colname);
    -- change 3D geom to 2D geom and transform SRID to 2154
		-- first, we need to extract geometry type and store it as a variable before alter table
    EXECUTE format('SELECT GeometryType(geom)::text FROM %s LIMIT 1', tbl) INTO geomtype;
    RAISE NOTICE 'geomtype : %', geomtype;
	EXECUTE format('ALTER TABLE %s ALTER COLUMN geom TYPE Geometry(%s, 2154) USING ST_Transform(ST_Force2D(geom), 2154);', tbl, geomtype);
   	RAISE NOTICE 'Reprojection % done', tbl;
   END LOOP;
END
$do$
;

-- RPG
DO
$do$
DECLARE
  tbl text := 'rpg_parcelles_graphiques';
	colname text := 'geometrie';
	new_colname text := 'geom';
	geomtype text :='MULTIPOLYGON';
BEGIN
  RAISE NOTICE 'Table : %', tbl;
  -- if geometry column is geometrie in tables list, rename to geom, else do nothing
  EXECUTE format('SELECT rename_if_exist(%L, %L, %L)', tbl, colname, new_colname);
  -- change 3D geom to 2D geom and transform SRID to 2154
  -- first, we need to extract geometry type and store it as a variable before alter table
  EXECUTE format('SELECT GeometryType(geom)::text FROM %s LIMIT 1', tbl) INTO geomtype;
  RAISE NOTICE 'geomtype : %', geomtype;
	EXECUTE format('ALTER TABLE %s ALTER COLUMN geom TYPE Geometry(%s, 2154) USING ST_Transform(ST_Force2D(geom), 2154);', tbl, geomtype);
  RAISE NOTICE 'Reprojection % done', tbl;
END
$do$
;