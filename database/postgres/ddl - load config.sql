-- Insert data into config.process_step
INSERT INTO config.process_step (id, message_type, status, action_label, next_status) VALUES
(1, 'memo', 'categorized', 'llm_audio_message_metadata', 'metadata'),
(2, 'memo', 'metadata',    'llm_audio_message_enrichment', 'enrichment');

-- Insert data into config.action
INSERT INTO config.action (action_label, description) VALUES
('llm_audio_message_metadata', 'Determine metadata for audio transcription using LLM'),
('llm_audio_message_enrichment', 'Determine enrichment for audio transcription using LLM');

-- Insert data into config.action_ai_llm
INSERT INTO config.action_ai_llm (action_label, ai_provider, model_name, prompt_label) VALUES
('llm_audio_message_metadata', 'openai', 'gpt-4.1', 'audio_message_metadata'),
('llm_audio_message_enrichment', 'openai', 'gpt-4.1', 'audio_message_enrichment');


-- Insert data into config.prompt
INSERT INTO config.prompt (prompt_label, prompt_template) VALUES
('audio_message_metadata', $$
Please review the following transcript and provide the json object defined below as your response.

{
	"category": "categorize as (idea, reminder, othera)",
	"client_label": "extract the client name if present or return None",
	"urgency": "categorize as (urgent, short-term, medium-term, long-term)",
	"data_sensitivity": "categorize as public or private, private if public not explicitly mentioned)"
}

Transcript:

{transcript}
$$),

('audio_message_enrichment', $$
Please review the following transcript and provide the json object defined below as your response.

{
	"rewrite_for_clarity": "please rewrite the transcript for clarity without losing any detail",
	"summary": "summarize the transcript in 100 words or less"
}

Transcript:

{transcript}
$$);

-- Insert data into config.prompt_parameter
INSERT INTO config.prompt_parameter (
    id, prompt_label, parameter_name, description, is_required, default_value
) VALUES
(1, 'audio_message_metadata', 'transcript', 'audio transcript', TRUE, NULL),
(2, 'audio_message_enrichment', 'transcript', 'audio transcript', TRUE, NULL);


-- Insert data into config.transcriber
INSERT INTO config.transcriber (provider, class_name, description, is_default) VALUES
('google', 'GoogleTranscriber', 'Uses Google Web Speech API via SpeechRecognition package', TRUE),
('openai', 'OpenAITranscriber', 'Uses OpenAI Whisper API or local Whisper model', FALSE);
