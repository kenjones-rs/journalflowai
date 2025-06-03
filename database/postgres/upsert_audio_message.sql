CREATE OR REPLACE FUNCTION data.upsert_audio_message(
    p_filename VARCHAR,
    p_transcription TEXT,
    p_message_type VARCHAR,
    p_status VARCHAR,
    p_metadata JSONB,
    p_enrichment JSONB
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO data.audio_message (
        filename, transcription, message_type, status, metadata, enrichment
    )
    VALUES (
        p_filename,
        p_transcription,
        COALESCE(p_message_type, 'unknown'),
        COALESCE(p_status, 'new'),
        COALESCE(p_metadata, '{}'::jsonb),
        COALESCE(p_enrichment, '{}'::jsonb)
    );
END;
$$ LANGUAGE plpgsql;
