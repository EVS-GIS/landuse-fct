/*
Warning, the operation could be time consuming if you have loaded the whole France
Create primary key on unique id and create spatial index if they don't already exist
An UNIQUE INDEX is create when primary key is define
*/

-- BD TOPO and zone_etude
DO
$do$
DECLARE
    tbl   text;
    arr text[] := array['public.batiment', 'public.construction_surfacique', 'public.cimetiere','public.reservoir',
      'public.construction_lineaire', 'public.piste_d_aerodrome', 'public.surface_hydrographique',
      'public.troncon_de_route', 'public.troncon_de_voie_ferree', 'public.zone_de_vegetation',
      'public.equipement_de_transport', 'public.zone_d_activite_ou_d_interet', 'public.zone_d_habitation', 'public.zone_etude'];
	pkeycolname text := 'cleabs';
	geomcolname text := 'geom';
BEGIN
   FOREACH tbl IN ARRAY arr
   LOOP
   	RAISE NOTICE 'Table : %', tbl;
    -- create primary key if doesn't exist
   	EXECUTE format('SELECT add_pkey_if_not_exist(%L, %L)', tbl, pkeycolname);
	-- create spatial index if doesn't exist
	EXECUTE format('SELECT create_geom_index_if_not_exist(%L, %L)', tbl, geomcolname);
   	RAISE NOTICE 'Pkey and % index on % done', geomcolname, tbl;
   END LOOP;
END
$do$
;

-- RPG
DO
$do$
DECLARE
    tbl text := 'rpg_parcelles_graphiques';
	pkeycolname text := 'id';
	geomcolname text := 'geom';
BEGIN
    RAISE NOTICE 'Table : %', tbl;
    -- create primary key if doesn't exist
    EXECUTE format('SELECT add_pkey_if_not_exist(%L, %L)', tbl, pkeycolname);
    -- create spatial index if doesn't exist
    EXECUTE format('SELECT create_geom_index_if_not_exist(%L, %L)', tbl, geomcolname);
    RAISE NOTICE 'Pkey and % index on % done', geomcolname, tbl;
END
$do$
