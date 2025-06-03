-- Create schemas
CREATE SCHEMA IF NOT EXISTS config;
CREATE SCHEMA IF NOT EXISTS data;

-- Config: Stores reusable prompts for LLM actions
CREATE TABLE config.prompt (
    id SERIAL PRIMARY KEY,
    prompt_label VARCHAR NOT NULL,          -- e.g., 'message_classification'
    prompt_template TEXT NOT NULL,
    UNIQUE(prompt_label)
);

-- Config: Stores prompt parameters for LLM actions
CREATE TABLE config.prompt_parameter (
    id SERIAL PRIMARY KEY,
    parameter_name VARCHAR NOT NULL,           -- e.g., 'client_name'
    description TEXT,                          -- human-readable explanation
    required BOOLEAN DEFAULT TRUE,             -- is it mandatory for prompt execution?
    default_value TEXT                         -- fallback if not supplied at runtime
);

-- Config: Master list of possible actions (AI or Python)
CREATE TABLE config.action (
    action_label VARCHAR PRIMARY KEY,       -- e.g., 'classify_topic'
    description TEXT NOT NULL
);

-- Config: Actions implemented as AI LLM calls
CREATE TABLE config.ai_llm_action (
    action_label VARCHAR PRIMARY KEY,       -- symbolic name of the action
    ai_provider VARCHAR NOT NULL,           -- e.g., 'openai', 'perplexity'
    model_name VARCHAR NOT NULL,            -- e.g., 'gpt-4'
    prompt_label VARCHAR NOT NULL           -- label of the prompt to use
);

-- Config: Actions implemented as deterministic Python functions
CREATE TABLE config.python_action (
    action_label VARCHAR PRIMARY KEY,       -- symbolic name of the action
    module_name VARCHAR NOT NULL,           -- e.g., 'myapp.enrichment.steps'
    function_name VARCHAR NOT NULL,         -- e.g., 'extract_dates'
    args_json JSONB DEFAULT '{}',           -- optional arguments
    version VARCHAR NOT NULL                -- e.g., 'v1.0', '2025-06-01'
);

-- Config: Configuration of what action to take based on message type and status
CREATE TABLE config.process_step (
    id SERIAL PRIMARY KEY,
    message_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    action_label VARCHAR NOT NULL
);

-- Data: Main table holding transcripted messages with hybrid schem
DROP TABLE data.audio_message;
CREATE TABLE data.audio_message (
    id SERIAL PRIMARY KEY,
    filename VARCHAR NOT NULL,
    transcription TEXT,
    message_type VARCHAR DEFAULT 'unknown', -- top-level for easy querying
    status VARCHAR DEFAULT 'new',           -- processing state
    metadata JSONB DEFAULT '{}',            -- extra fields like timestamps, flags
    enrichment JSONB DEFAULT '{}',          -- results from enrichment steps
    created_at TIMESTAMP DEFAULT NOW()
);
