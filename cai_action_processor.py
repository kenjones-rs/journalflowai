# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import importlib
import logging
from cai_chat_session import ChatSession

class ActionProcessor:
    def __init__(self, data_repo, config_repo, llm_usage_repo):
        """
        :param data_repo: Repository for data.audio_message
        :param config_repo: ConfigRepository for configuration access
        :param llm_usage_repo: LLMUsageRepository to log usage
        """
        self.data_repo = data_repo
        self.config_repo = config_repo
        self.llm_usage_repo = llm_usage_repo
        self.logger = logging.getLogger("ActionProcessor")

    def execute(self, action_label, context: dict) -> dict:
        action_type = self._determine_action_type(action_label)

        if action_type == 'ai_llm':
            return self._run_ai_action(action_label, context)
        elif action_type == 'python':
            return self._run_python_action(action_label, context)
        else:
            raise ValueError(f"Unknown or unsupported action type for '{action_label}'")

    def _determine_action_type(self, action_label):
        if self.config_repo.get_action_ai_llm_config(action_label):
            return "ai_llm"
        elif self.config_repo.fetch_record("python_action", {"action_label": action_label}, schema="config"):
            return "python"
        return None

    def _run_ai_action(self, action_label, context):
        record = self.config_repo.get_action_ai_llm_config(action_label)[0]
        prompt_record = self.config_repo.get_prompt_template(record["prompt_label"])[0]
        prompt_template = prompt_record["prompt_template"]
        rendered_prompt = prompt_template.format(**context)

        client = self.ai_client_registry[record["ai_provider"]]
        chat_session = ChatSession(system_message="You are a helpful assistant.")
        chat_session.add_message("user", rendered_prompt)

        try:
            response_data = client.chat(chat_session, temperature=0.0)
            self.logger.info(f"AI action '{action_label}' executed with model={record['model_name']} prompt={rendered_prompt}")

            # Persist LLM usage
            usage_record = {
                "entity_type": context.get("entity_type", "unknown"),
                "entity_id": context.get("entity_id", 0),
                "model_name": record["model_name"],
                "prompt_label": record["prompt_label"],
                "prompt_template": prompt_template,
                "response_text": response_data["response"],
                "prompt_token_count": response_data["prompt_token_count"],
                "response_token_count": response_data["response_token_count"],
                "response_duration_seconds": context.get("response_duration_seconds", 0),
                "temperature": 0.0,
                "status": "success",
                "error_message": None
            }

            self.llm_usage_repo.insert(usage_record)

        except Exception as e:
            self.logger.error(f"Error executing LLM action '{action_label}': {str(e)}", exc_info=True)
            raise

        return response_data["response"]

    def _run_python_action(self, action_label, context):
        record = self.config_repo.fetch_record("python_action", {"action_label": action_label}, schema="config")[0]
        module = importlib.import_module(record["module_name"])
        func = getattr(module, record["function_name"])

        args = record.get("args_json", {}) or {}
        result = func(context, **args)

        self.logger.info(f"Python action '{action_label}' executed from {record['module_name']}.{record['function_name']}")
        return result
