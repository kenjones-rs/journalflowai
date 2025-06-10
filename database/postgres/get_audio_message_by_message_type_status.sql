CREATE OR REPLACE FUNCTION data.get_audio_message_by_message_type_status(
    p_message_type VARCHAR,
    p_status VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    filename VARCHAR,
    transcription TEXT,
    message_type VARCHAR,
    status VARCHAR,
    metadata JSONB,
    enrichment JSONB,
    created_at TIMESTAMP
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.id,
        am.filename,
        am.transcription,
        am.message_type,
        am.status,
        am.metadata,
        am.enrichment,
        am.created_at
    FROM data.audio_message am
    WHERE am.message_type = p_message_type
      AND am.status = p_status;
END;
$$ LANGUAGE plpgsql;
