CREATE OR REPLACE FUNCTION data.mark_audio_message_failure(
    p_id INTEGER
)
RETURNS VOID AS $$
BEGIN
    UPDATE data.audio_message
    SET
        is_failure = TRUE,
        failure_at = NOW()
    WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;
