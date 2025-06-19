CREATE OR REPLACE FUNCTION config.get_prompt_parameter(
    p_prompt_label VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    prompt_label VARCHAR,
    parameter_name VARCHAR,
    description TEXT,
    is_required BOOLEAN,
    default_value TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pp.id,
        pp.prompt_label,
        pp.parameter_name,
        pp.description,
        pp.is_required,
        pp.default_value
    FROM config.prompt_parameter pp
    WHERE pp.prompt_label = p_prompt_label;
END;
$$ LANGUAGE plpgsql;
