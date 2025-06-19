CREATE OR REPLACE FUNCTION config.get_action_ai_llm(
    p_action_label VARCHAR
)
RETURNS TABLE (
    action_label VARCHAR,
    ai_provider VARCHAR,
    model_name VARCHAR,
    prompt_label VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        aal.action_label,
        aal.ai_provider,
        aal.model_name,
        aal.prompt_label
    FROM config.action_ai_llm aal
    WHERE aal.action_label = p_action_label;
END;
$$ LANGUAGE plpgsql;
