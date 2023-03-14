/*
Create geometry index with GIST if not already define
Ressources :  
- https://stackoverflow.com/questions/45983169/checking-for-existence-of-index-in-postgresql
- https://docs.postgresql.fr/15/catalog-pg-class.html
Example : SELECT create_geom_index_if_not_exist('cimetiere', 'geom');
*/

CREATE OR REPLACE FUNCTION create_geom_index_if_not_exist ( 
	_tbl regclass, 
	_geomcolname text)
RETURNS void
LANGUAGE plpgsql
AS
$$
DECLARE
	actual_indexgeomname text := 'geom';
	relkind_param text := 'r';
	new_indexgeomname text := 'idx_' || _geomcolname || '_' || _tbl::text;
BEGIN
   -- check in pg admin table if and index id define on geometry column
   IF EXISTS (
   SELECT
		t.relname as table_name,
		i.relname as index_name,
		a.attname as column_name
	FROM
		pg_class t,
		pg_class i,
		pg_index ix,
		pg_attribute a
	WHERE
		t.oid = ix.indrelid
		AND i.oid = ix.indexrelid
		AND a.attrelid = t.oid
		AND a.attnum = ANY(ix.indkey)
		AND t.relkind = 'r'
		AND t.relname like _tbl::text
		AND a.attname LIKE _geomcolname) THEN
      -- the geometrie index exist, print the index name
	  EXECUTE format(
		  'SELECT
				i.relname as index_name
			FROM
				pg_class t,
				pg_class i,
				pg_index ix,
				pg_attribute a
			WHERE
				t.oid = ix.indrelid
				AND i.oid = ix.indexrelid
				AND a.attrelid = t.oid
				AND a.attnum = ANY(ix.indkey)
				AND t.relkind = %L
				AND t.relname like %L
				AND a.attname LIKE %L', relkind_param, _tbl, _geomcolname) 
				INTO actual_indexgeomname;
	  -- print the actual index geometry name
	  RAISE NOTICE 'An index already exist on geom column as %', actual_indexgeomname;
   ELSE
      -- the index doesn't exist, create it
	  EXECUTE format('CREATE INDEX %s ON %s USING gist (%I);'
					 , new_indexgeomname, _tbl, _geomcolname);
      RAISE NOTICE 'New geometry index define on % as %', _geomcolname, new_indexgeomname;
   END IF;
END
$$;