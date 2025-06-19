CREATE OR REPLACE FUNCTION config.get_prompt_output(
    p_prompt_label VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    prompt_label VARCHAR,
    output_key VARCHAR,
    schema_name VARCHAR,
    table_name VARCHAR,
    id_column VARCHAR,
    column_name VARCHAR,
    column_type VARCHAR,
    json_key VARCHAR,
    mode VARCHAR,
    created_at TIMESTAMP
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        po.id,
        po.prompt_label,
        po.output_key,
        po.schema_name,
        po.table_name,
        po.id_column,
        po.column_name,
        po.column_type,
        po.json_key,
        po.mode,
        po.created_at
    FROM config.prompt_output po
    WHERE po.prompt_label = p_prompt_label;
END;
$$ LANGUAGE plpgsql;
