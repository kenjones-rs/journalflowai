CREATE OR REPLACE FUNCTION data.get_audio_message_by_filename(
    p_filename VARCHAR
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
    WHERE am.filename = p_filename;
END;
$$ LANGUAGE plpgsql;
