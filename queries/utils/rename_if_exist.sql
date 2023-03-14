/*
Rename a column if the column exists
Ressource :  https://stackoverflow.com/questions/68247752/postgresql-rename-a-column-only-if-it-exists
Example : SELECT rename_if_exist('cimetiere', 'geometrie', 'geom');
*/

CREATE OR REPLACE FUNCTION rename_if_exist ( _tbl regclass, _colname name, _new_colname text)
RETURNS void
LANGUAGE plpgsql
AS
$$
BEGIN
   -- check in pg_attribute if the column we want to rename exist
   IF EXISTS (SELECT FROM pg_attribute
              WHERE  attrelid = _tbl
              AND    attname  = _colname
              AND    attnum > 0
              AND    NOT attisdropped) THEN
      -- the colum exist, rename it
      EXECUTE format('ALTER TABLE %s RENAME COLUMN %I TO %I', _tbl, _colname, _new_colname);
   ELSE
      -- the column doesn't exist
      RAISE NOTICE 'Column % of table % not found!', quote_ident(_colname), _tbl;
   END IF;
END
$$;