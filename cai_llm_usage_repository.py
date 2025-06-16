# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import logging
from logging.handlers import RotatingFileHandler
from cai_repository import Repository

# Set up logging for LLMUsageRepository
llm_logger = logging.getLogger('LLMUsageRepository')
llm_handler = RotatingFileHandler('./logs/llm_usage_repository.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
llm_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
llm_handler.setFormatter(llm_formatter)
llm_logger.addHandler(llm_handler)
llm_logger.setLevel(logging.INFO)

class LLMUsageRepository(Repository):
    def insert(self, usage_record):
        """
        Inserts a record into the llm_usage table using the stored procedure.
        """
        query = """
        SELECT data.insert_llm_usage(
            %s,             -- entity_type
            %s::INT,        -- entity_id
            %s,             -- model_name
            %s,             -- prompt_label
            %s,             -- prompt_template
            %s,             -- response_text
            %s::INT,        -- prompt_token_count
            %s::INT,        -- response_token_count
            %s::INT,        -- response_duration_seconds
            %s::NUMERIC,    -- temperature
            %s,             -- status
            %s              -- error_message
        )
        """

        params = [
            usage_record["entity_type"],
            usage_record["entity_id"],
            usage_record["model_name"],
            usage_record["prompt_label"],
            usage_record["prompt_template"],
            usage_record["response_text"],
            usage_record["prompt_token_count"],
            usage_record["response_token_count"],
            usage_record["response_duration_seconds"],
            usage_record["temperature"],
            usage_record["status"],
            usage_record.get("error_message")
        ]

        try:
            self.db.execute_query(query, params)
            llm_logger.info(f"Inserted LLM usage record: {usage_record}")
        except Exception as e:
            llm_logger.error(f"Failed to insert LLM usage record: {usage_record}. Error: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    from cai_postgres_database import PostgresDatabase

    postgres = {
        'host': 'dev02',
        'port': 5432,
        'user': 'dev',
        'password': 'Alpha909Time',
        'dbname': 'journalflowai'
    }

    db = PostgresDatabase(postgres)
    repo = LLMUsageRepository(db)

    usage_record = {
        "entity_type": "audio_message",
        "entity_id": 1,
        "model_name": "gpt-4.1",
        "prompt_label": "audio_message_metadata",
        "prompt_template": "Summarize this audio: {{ transcript }}",
        "response_text": "The speaker discusses quarterly sales targets and market challenges.",
        "prompt_token_count": 120,
        "response_token_count": 85,
        "response_duration_seconds": 3,
        "temperature": 0.7,
        "status": "success",
        "error_message": None
    }

    with repo.transaction():
        repo.insert(usage_record)
