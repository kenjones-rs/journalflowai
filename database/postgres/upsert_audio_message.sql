CREATE OR REPLACE FUNCTION data.upsert_audio_message(
    p_filename VARCHAR,
    p_message_type VARCHAR,
    p_status VARCHAR,
    p_audio_file_size_kb INT,
    p_audio_duration_seconds INT,
    p_transcription TEXT,
    p_transcription_duration_seconds INT,
    p_transcription_word_count INT,
    p_metadata JSONB,
    p_enrichment JSONB
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO data.audio_message (
        filename,
        message_type,
        status,
        audio_file_size_kb,
        audio_duration_seconds,
        transcription,
        transcription_duration_seconds,
        transcription_word_count,
        metadata,
        enrichment
    )
    VALUES (
        p_filename,
        COALESCE(p_message_type, 'unknown'),
        COALESCE(p_status, 'new'),
        COALESCE(p_audio_file_size_kb, 0),
        COALESCE(p_audio_duration_seconds, 0),
        p_transcription,
        COALESCE(p_transcription_duration_seconds, 0),
        COALESCE(p_transcription_word_count, 0),
        COALESCE(p_metadata, '{}'::jsonb),
        COALESCE(p_enrichment, '{}'::jsonb)
    )
    ON CONFLICT (filename) DO UPDATE SET
        message_type = EXCLUDED.message_type,
        status = EXCLUDED.status,
        audio_file_size_kb = EXCLUDED.audio_file_size_kb,
        audio_duration_seconds = EXCLUDED.audio_duration_seconds,
        transcription = EXCLUDED.transcription,
        transcription_duration_seconds = EXCLUDED.transcription_duration_seconds,
        transcription_word_count = EXCLUDED.transcription_word_count,
        metadata = EXCLUDED.metadata,
        enrichment = EXCLUDED.enrichment;
END;
$$ LANGUAGE plpgsql;
