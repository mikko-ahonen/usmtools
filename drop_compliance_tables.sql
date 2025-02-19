DO $do$
DECLARE
   _tbl text;
BEGIN
FOR _tbl  IN
    SELECT quote_ident(table_schema) || '.'
        || quote_ident(table_name)      -- escape identifier and schema-qualify!
    FROM   information_schema.tables
    WHERE  ((table_name LIKE 'compliances_' || '%') OR (table_name LIKE 'workflows_' || '%') OR (table_name LIKE 'projects_' || '%') OR (table_name LIKE 'admin_' || '%') OR (table_name LIKE 'registration_' || '%') OR (table_name LIKE 'mir_' || '%') OR (table_name LIKE 'xref_' || '%') OR (table_name LIKE 'auth_' || '%') OR (table_name LIKE 'sequences_' || '%') OR (table_name LIKE 'onboarding_' || '%') OR (table_name LIKE 'survey_' || '%') OR (table_name LIKE 'accounts_' || '%') OR (table_name LIKE 'taggit_' || '%') OR (table_name LIKE 'django_' || '%') OR (table_name LIKE 'stats_' || '%')) AND (table_name NOT LIKE '%_authorizations')
      AND    table_schema NOT LIKE 'pg\_%'    -- exclude system schemas
LOOP
   -- RAISE NOTICE '%',
   EXECUTE
  'DROP TABLE ' || _tbl || ' CASCADE';  -- see below
END LOOP;
END
$do$;
