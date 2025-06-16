CREATE OR REPLACE FUNCTION data.insert_llm_usage(
    p_entity_type VARCHAR,
    p_entity_id INT,
    p_model_name VARCHAR,
    p_prompt_label VARCHAR,
    p_prompt_template TEXT,
    p_response_text TEXT,
    p_prompt_token_count INT,
    p_response_token_count INT,
    p_response_duration_seconds INT DEFAULT NULL,
    p_temperature NUMERIC(3,2) DEFAULT NULL,
    p_status VARCHAR DEFAULT 'success',
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO data.llm_usage (
        entity_type,
        entity_id,
        model_name,
        prompt_label,
        prompt_template,
        response_text,
        prompt_token_count,
        response_token_count,
        response_duration_seconds,
        temperature,
        status,
        error_message,
        created_at
    )
    VALUES (
        p_entity_type,
        p_entity_id,
        p_model_name,
        p_prompt_label,
        p_prompt_template,
        p_response_text,
        p_prompt_token_count,
        p_response_token_count,
        p_response_duration_seconds,
        p_temperature,
        p_status,
        p_error_message,
        NOW()
    );
END;
$$ LANGUAGE plpgsql;
