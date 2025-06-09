CREATE OR REPLACE FUNCTION config.get_transcriber(p_is_default BOOLEAN)
RETURNS TABLE (
    id INT,
    provider VARCHAR,
    class_name VARCHAR,
    description TEXT,
    is_default BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.provider, t.class_name, t.description, t.is_default
    FROM config.transcriber t
    WHERE t.is_default = p_is_default;
END;
$$ LANGUAGE plpgsql;
