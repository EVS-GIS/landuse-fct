/*
Add primary key with a define column if a primary key is not already define
Exemple : SELECT add_pkey_if_not_exist('public.cimetiere', 'cleabs')
*/

CREATE OR REPLACE FUNCTION add_pkey_if_not_exist (_tbl regclass, _pkey text)
RETURNS void
LANGUAGE plpgsql
AS
$$
DECLARE
	pkeyactual text := 'cleab';
	primary_key text := 'PRIMARY KEY';
BEGIN
	IF EXISTS (
			-- check if a primary key is already define
			SELECT constraint_name::text
			FROM information_schema.table_constraints  
			WHERE constraint_type = 'PRIMARY KEY'   
			AND table_name = _tbl::text) THEN
		-- yes, already define, extract and store the pkey name
		EXECUTE format('SELECT constraint_name::text 
					   FROM information_schema.table_constraints  
					   WHERE constraint_type = %L
					   AND table_name = %L', primary_key, _tbl) INTO pkeyactual;
		-- print the actual pkey name
		RAISE NOTICE 'A primary key id already defined as %', pkeyactual;
	ELSE
		-- A pkey is not defined, add it to the table
		EXECUTE format('ALTER TABLE %s ADD PRIMARY KEY (%I)', _tbl, _pkey);
		RAISE NOTICE 'Primary key define on column %', _pkey;
	END IF;
END
$$;