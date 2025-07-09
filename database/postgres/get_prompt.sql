CREATE OR REPLACE FUNCTION config.get_prompt(
    p_prompt_label VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    prompt_label VARCHAR,
    prompt_template TEXT,
    temperature FLOAT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.prompt_label,
        p.prompt_template,
        p.temperature
    FROM config.prompt p
    WHERE p.prompt_label = p_prompt_label;
END;
$$ LANGUAGE plpgsql;
