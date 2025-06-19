# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import logging
from logging.handlers import RotatingFileHandler
from cai_repository import Repository

# Set up logging for ConfigRepository
config_logger = logging.getLogger('ConfigRepository')
config_handler = RotatingFileHandler('./logs/config_repository.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
config_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
config_handler.setFormatter(config_formatter)
config_logger.addHandler(config_handler)
config_logger.setLevel(logging.INFO)


class ConfigRepository(Repository):
    def get_transcriber(self, is_default=True):
        config_logger.info(f"Fetching transcriber with is_default={is_default}")
        return self.fetch_record("transcriber", {"is_default": is_default}, schema="config")

    def get_process_steps(self, message_type, status):
        config_logger.info(f"Fetching process_step for message_type={message_type}, status={status}")
        return self.fetch_record("process_steps", {"message_type": message_type, "status": status}, schema="config")

    def get_action_ai_llm(self, action_label):
        config_logger.info(f"Fetching AI/LLM config for action_label={action_label}")
        return self.fetch_record("action_ai_llm", {"action_label": action_label}, schema="config")
    
    def get_action_python(self, action_label):
        config_logger.info(f"Fetching python config for action_label={action_label}")
        return self.fetch_record("action_python", {"action_label": action_label}, schema="config")

    def get_prompt(self, prompt_label):
        config_logger.info(f"Fetching prompt template for prompt_label={prompt_label}")
        return self.fetch_record("prompt", {"prompt_label": prompt_label}, schema="config")

    def get_prompt_parameters(self, prompt_label):
        config_logger.info(f"Fetching prompt parameters for prompt_label={prompt_label}")
        return self.fetch_record("prompt_parameter", {"prompt_label": prompt_label}, schema="config")
    
    def get_prompt_outputs(self, prompt_label):
        config_logger.info(f"Fetching prompt outputs for prompt_label={prompt_label}")
        return self.fetch_record("prompt_output", {"prompt_label": prompt_label}, schema="config")
