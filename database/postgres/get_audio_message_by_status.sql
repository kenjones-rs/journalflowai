CREATE OR REPLACE FUNCTION data.get_audio_message_by_status(
    p_status VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    filename VARCHAR,
    message_type VARCHAR,
    status VARCHAR,
    audio_file_size_kb INT,
    audio_duration_seconds INT,
    transcription TEXT,
    transcription_duration_seconds INT,
    transcription_word_count INT,
    metadata JSONB,
    enrichment JSONB,
    created_at TIMESTAMP,
    is_failure BOOLEAN,
    failure_at TIMESTAMP
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.id,
        am.filename,
        am.message_type,
        am.status,
        am.audio_file_size_kb,
        am.audio_duration_seconds,
        am.transcription,
        am.transcription_duration_seconds,
        am.transcription_word_count,
        am.metadata,
        am.enrichment,
        am.created_at,
        am.is_failure,
        am.failure_at
    FROM data.audio_message am
    WHERE am.status = p_status;
END;
$$ LANGUAGE plpgsql;
