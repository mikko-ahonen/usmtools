DO
$do$
DECLARE
   _tbl text;
BEGIN
FOR _tbl  IN
    SELECT quote_ident(table_schema) || '.'
        || quote_ident(table_name)      -- escape identifier and schema-qualify!
    FROM   information_schema.tables
    WHERE  table_name LIKE 'compliances_' || '%'  OR table_name LIKE 'projects_' || '%' -- your table name prefix
    AND    table_schema NOT LIKE 'pg\_%'    -- exclude system schemas
LOOP
   -- RAISE NOTICE '%',
   EXECUTE
  'DROP TABLE ' || _tbl || ' CASCADE';  -- see below
END LOOP;
END
$do$;
