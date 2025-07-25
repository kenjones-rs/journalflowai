-- Insert data into config.process_step
TRUNCATE TABLE config.process_step;
INSERT INTO config.process_step (id, message_type, status, action_label, next_status) VALUES
(1, 'unknown', 'transcribed', 'llm_audio_message_categorize', 'categorized'),
(2, 'memo', 'categorized', 'llm_audio_message_get_metadata', 'metadata'),
(3, 'memo', 'metadata',    'llm_audio_message_enrich', 'enrichment');

-- Insert data into config.action
TRUNCATE TABLE config.action;
INSERT INTO config.action (action_label, description) VALUES
('llm_audio_message_categorize', 'Determine the message type for audio transcription using LLM'),
('llm_audio_message_get_metadata', 'Determine metadata for audio transcription using LLM'),
('llm_audio_message_enrich', 'Determine enrichment for audio transcription using LLM');

-- Insert data into config.action_ai_llm
TRUNCATE TABLE config.action_ai_llm;
INSERT INTO config.action_ai_llm (action_label, ai_provider, model_name, prompt_label) VALUES
('llm_audio_message_categorize', 'openai', 'gpt-4.1', 'audio_message_categorize'),
('llm_audio_message_get_metadata', 'openai', 'gpt-4.1', 'audio_message_metadata'),
('llm_audio_message_enrich', 'openai', 'gpt-4.1', 'audio_message_enrichment');

-- Insert data into config.prompt
TRUNCATE TABLE config.prompt;
INSERT INTO config.prompt (prompt_label, prompt_template) VALUES
('audio_message_categorize', $$
You are an expert at analyzing voice transcripts. Categorize the following message as either "memo" or "meeting" based on these guidelines:

memo: A short message with only one speaker (e.g., a voice memo, reminder, or single-person note).
meeting: A longer message with multiple speakers (e.g., a team discussion or group call).

Consider the following attributes:
Number of words: {transcript_word_count}
Transcript: 

{transcript}

Output a json object with the format:

{{
    "message_type": "memo" // or "meeting"
}}
$$),

('audio_message_metadata', $$
Please review the following transcript and provide the json object defined below as your response.

{{
	"category": "categorize as (idea, reminder, other)",
	"client_label": "extract the client name if present or return None",
	"urgency": "categorize as (urgent, short-term, medium-term, long-term)",
	"data_sensitivity": "categorize as public or private, choose private if public not explicitly mentioned)"
}}

Transcript:

{transcript}
$$),

('audio_message_enrichment', $$
Please review the following transcript and provide the json object defined below as your response.

{{
	"rewrite_for_clarity": "please rewrite the transcript for clarity without losing any detail",
	"summary": "summarize the transcript in 100 words or less"
}}

Transcript:

{transcript}
$$);

-- Insert data into config.prompt_parameter
TRUNCATE TABLE config.prompt_parameter;
INSERT INTO config.prompt_parameter (
    id, prompt_label, parameter_name, description, is_required, default_value
) VALUES
(1, 'audio_message_categorize', 'transcript_word_count', 'transcript word count', TRUE, NULL),
(2, 'audio_message_categorize', 'transcript', 'audio transcript', TRUE, NULL),
(3, 'audio_message_metadata', 'transcript', 'audio transcript', TRUE, NULL),
(4, 'audio_message_enrichment', 'transcript', 'audio transcript', TRUE, NULL);

-- Insert data into config.prompt_output
INSERT INTO config.prompt_output (
    prompt_label,
    output_key,
    schema_name,
    table_name,
    id_column,
    column_name,
    column_type,
    json_key,
    mode
) VALUES (
    'audio_message_categorize',     -- prompt_label
    'message_type',                 -- output_key in JSON response
    'data',                         -- schema_name
    'audio_message',                -- table_name
    'id',                           -- id_column
    'message_type',                 -- column_name
    'column',                       -- column_type
    NULL,                           -- json_key not needed
    'replace'                       -- mode (ignored for column type)
);


-- Insert data into config.transcriber
TRUNCATE TABLE config.transcriber;
INSERT INTO config.transcriber (provider, class_name, description, is_default) VALUES
('google', 'GoogleTranscriber', 'Uses Google Web Speech API via SpeechRecognition package', FALSE),
('openai', 'WhisperTranscriber', 'Uses OpenAI Whisper API or local Whisper model', TRUE);
