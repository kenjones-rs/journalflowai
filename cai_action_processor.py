# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import time
from datetime import datetime, UTC
import json
import importlib
import logging
from cai_chat_session import ChatSession

class ActionProcessor:
    def __init__(self, config_repo, audio_message_repo, llm_usage_repo, ai_client_registry):
        """
        :param audio_message_repo: Repository for data.audio_message
        :param config_repo: ConfigRepository for configuration access
        :param llm_usage_repo: LLMUsageRepository to log usage
        """
        self.config_repo = config_repo
        self.audio_message_repo = audio_message_repo
        self.llm_usage_repo = llm_usage_repo
        self.ai_client_registry = ai_client_registry
        self.logger = logging.getLogger("ActionProcessor")

    def execute(self, action_label, context: dict, entity_type: str) -> dict:
        action_type = self._determine_action_type(action_label)

        if action_type == 'ai_llm':
            return self._run_ai_action(action_label, context, entity_type)
        elif action_type == 'python':
            return self._run_python_action(action_label, context, entity_type)
        else:
            raise ValueError(f"Unknown or unsupported action type for '{action_label}'")

    def _determine_action_type(self, action_label):
        if self.config_repo.get_action_ai_llm(action_label):
            return "ai_llm"
        elif self.config_repo.get_action_python(action_label):
            return "python"
        return None

    def _run_ai_action(self, action_label, context, entity_type):
        records = self.config_repo.get_action_ai_llm(action_label)
        if not records:
            raise ValueError(f"No AI/LLM configuration found for action_label='{action_label}'")
        
        record = records[0]
        prompt_record = self.config_repo.get_prompt(record["prompt_label"])
        if not prompt_record:
            raise ValueError(f"No prompt template found for label='{record['prompt_label']}'")
        
        prompt_template = prompt_record[0]["prompt_template"]
        temperature = prompt_record[0]["temperature"]
        #temperature = 0.0
        
        try:
            rendered_prompt = prompt_template.format(**context)
        except KeyError as e:
            raise KeyError(f"Missing context variable for prompt formatting: {e}") from e

        client = self.ai_client_registry[record["ai_provider"]]
        chat_session = ChatSession("You are a helpful assistant.")
        chat_session.add_message("user", rendered_prompt)

        try:
            start_time = time.time()
            response_data = client.chat(chat_session, temperature)
            response_duration = round(time.time() - start_time)
            
            self.logger.info(f"AI action '{action_label}' executed with model={record['model_name']}")

            usage_record = {
                "entity_type": entity_type,
                "entity_id": context.get("id", 0),
                "model_name": record["model_name"],
                "prompt_label": record["prompt_label"],
                "prompt_template": prompt_template,
                "response_text": response_data["response"],
                "prompt_token_count": response_data["prompt_token_count"],
                "response_token_count": response_data["response_token_count"],
                "response_duration_seconds": response_duration,
                "temperature": 0.0,
                "status": "success",
                "error_message": None
            }

            print(usage_record)
            with self.llm_usage_repo.transaction():
                self.llm_usage_repo.insert(usage_record)

            # Convert the response_data["response"] to a dictionary
            try:
                response_dict = json.loads(response_data["response"])
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode LLM response as JSON: {str(e)}")
                raise

            # Apply the prompt output using configuration
            try:
                self.apply_prompt_output(
                    prompt_label=record["prompt_label"],
                    entity_id=context.get("id", 0),
                    response_dict=response_dict,
                    entity_type=entity_type
                )
            except Exception as e:
                self.logger.error(f"Failed to apply prompt output for action '{action_label}': {str(e)}", exc_info=True)
                raise

        except Exception as e:
            self.logger.error(f"Error executing LLM action '{action_label}': {str(e)}", exc_info=True)

            usage_record = {
                "entity_type": entity_type,
                "entity_id": context.get("id", 0),
                "model_name": record.get("model_name", "unknown"),
                "prompt_label": record.get("prompt_label", "unknown"),
                "prompt_template": prompt_template,
                "response_text": None,
                "prompt_token_count": 0,
                "response_token_count": 0,
                "response_duration_seconds": 0,
                "temperature": 0.0,
                "status": "error",
                "error_message": str(e)[:1000]  # truncate long errors if needed
            }

            with self.llm_usage_repo.transaction():
                self.llm_usage_repo.insert(usage_record)

            raise

        return context


    def _run_python_action(self, action_label, context, entity_type):
        record = self.config_repo.get_action_python(action_label)[0]
        module = importlib.import_module(record["module_name"])
        func = getattr(module, record["function_name"])

        args = record.get("args_json", {}) or {}
        result = func(context, **args)

        self.logger.info(f"Python action '{action_label}' executed from {record['module_name']}.{record['function_name']}")
        return context

    def apply_prompt_output(self, prompt_label, entity_id, response_dict, entity_type):
        """
        Applies the output from an LLM response to the appropriate table columns or JSONB keys
        using the config.prompt_output table definitions.
        """
        output_defs = self.config_repo.get_prompt_outputs(prompt_label)

        for output in output_defs:
            output_key = output["output_key"]
            schema = output["schema_name"]
            table = output["table_name"]
            id_column = output["id_column"]
            column = output["column_name"]
            column_type = output["column_type"]
            json_key = output.get("json_key")  # may be None
            mode = output.get("mode", "replace")  # default to 'replace'

            if output_key not in response_dict:
                self.logger.warning(f"Key '{output_key}' not found in response_dict for prompt_label='{prompt_label}'")
                continue

            value = response_dict[output_key]
            versioned_value = {
                "value": value,
                "model": "llm",
                "timestamp": datetime.now(UTC).isoformat()
            }

            try:
                if column_type == "jsonb":
                    with self.audio_message_repo.transaction():
                        self.audio_message_repo.update_json_key_with_version(
                            schema=schema,
                            table=table,
                            id_column=id_column,
                            id_value=entity_id,
                            json_column=column,
                            json_key=json_key,
                            json_value=versioned_value,
                            mode=mode
                        )
                elif column_type == "column":
                    with self.audio_message_repo.transaction():
                        self.audio_message_repo.update_column_value(
                            schema=schema,
                            table=table,
                            id_column=id_column,
                            id_value=entity_id,
                            column_name=column,
                            column_value=value
                        )
                else:
                    self.logger.warning(f"Unknown column_type='{column_type}' in prompt_output for key='{output_key}'")
            except Exception as e:
                self.logger.error(f"Failed to apply output for key '{output_key}': {str(e)}", exc_info=True)


if __name__ == "__main__":
    import os
    import logging
    from cai_postgres_database import PostgresDatabase
    from cai_audio_message_repository import AudioMessageRepository
    from cai_config_repository import ConfigRepository
    from cai_llm_usage_repository import LLMUsageRepository
    from cai_llm_factory import create_llm

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Database config
    postgres = {
        'host': 'dev02',
        'port': 5432,
        'user': 'dev',
        'password': 'Alpha909Time',
        'dbname': 'journalflowai'
    }

    # Instantiate repositories
    db = PostgresDatabase(postgres)
    config_repo = ConfigRepository(db)
    audio_message_repo = AudioMessageRepository(db)
    llm_usage_repo = LLMUsageRepository(db)

    # Build registry with OpenAI client
    ai_client_registry = {
        "openai": create_llm("openai", "gpt-4.1")
    }

    # Inject into ActionProcessor
    processor = ActionProcessor(config_repo, audio_message_repo, llm_usage_repo, ai_client_registry)

    # Action label configured in your database
    action_label = "llm_audio_message_categorize"

    # Get the message from DB
    filename = "audio/Ken Jones-20250606-173425.mp3"
    messages = audio_message_repo.get_by_filename(filename)
    message = messages[0]

    # Execute
    message = processor.execute(action_label, message, entity_type='audio_message')
    print("LLM Response:", message)
