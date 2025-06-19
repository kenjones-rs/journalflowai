CREATE OR REPLACE FUNCTION config.get_process_step_by_type_and_status(
    p_message_type VARCHAR,
    p_status VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    message_type VARCHAR,
    status VARCHAR,
    action_label VARCHAR,
    next_status VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ps.id,
        ps.message_type,
        ps.status,
        ps.action_label,
        ps.next_status
    FROM config.process_step ps
    WHERE ps.message_type = p_message_type
      AND ps.status = p_status;
END;
$$ LANGUAGE plpgsql;
