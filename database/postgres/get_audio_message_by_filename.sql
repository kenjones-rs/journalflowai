CREATE OR REPLACE FUNCTION data.get_audio_message_by_filename(
    p_filename VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    filename VARCHAR,
    message_type VARCHAR,
    status VARCHAR,
    audio_file_size_kb INT,
    audio_duration_seconds INT,
    transcript TEXT,
    transcription_duration_seconds INT,
    transcript_word_count INT,
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
        am.transcript,
        am.transcription_duration_seconds,
        am.transcript_word_count,
        am.metadata,
        am.enrichment,
        am.created_at,
        am.is_failure,
        am.failure_at
    FROM data.audio_message am
    WHERE am.filename = p_filename;
END;
$$ LANGUAGE plpgsql;
