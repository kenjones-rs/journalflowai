import importlib
import logging

class ActionProcessor:
    def __init__(self, repo, prompt_repo, ai_client_registry):
        """
        :param repo: Repository with access to config.action, ai_llm_action, python_action
        :param prompt_repo: PromptRepository
        :param ai_client_registry: Dict mapping provider names to callable API clients
        """
        self.repo = repo
        self.prompt_repo = prompt_repo
        self.ai_client_registry = ai_client_registry
        self.logger = logging.getLogger("ActionProcessor")

    def execute(self, action_label, context: dict) -> str or dict:
        # Determine action type
        action_type = self._determine_action_type(action_label)

        if action_type == 'ai_llm':
            return self._run_ai_action(action_label, context)
        elif action_type == 'python':
            return self._run_python_action(action_label, context)
        else:
            raise ValueError(f"Unknown or unsupported action type for '{action_label}'")

    def _determine_action_type(self, action_label):
        if self.repo.fetch_record("ai_llm_action", {"action_label": action_label}):
            return "ai_llm"
        elif self.repo.fetch_record("python_action", {"action_label": action_label}):
            return "python"
        return None

    def _run_ai_action(self, action_label, context):
        record = self.repo.fetch_record("ai_llm_action", {"action_label": action_label})[0]
        prompt_template = self.prompt_repo.get_prompt_by_label(record["prompt_label"])["prompt_template"]
        rendered_prompt = prompt_template.format(**context)

        client = self.ai_client_registry[record["ai_provider"]]
        response = client.call(model=record["model_name"], prompt=rendered_prompt)

        self.logger.info(f"AI action '{action_label}' executed with prompt: {rendered_prompt}")
        return response

    def _run_python_action(self, action_label, context):
        record = self.repo.fetch_record("python_action", {"action_label": action_label})[0]
        module = importlib.import_module(record["module_name"])
        func = getattr(module, record["function_name"])

        args = record.get("args_json", {})
        result = func(context, **args)

        self.logger.info(f"Python action '{action_label}' executed from {record['module_name']}.{record['function_name']}")
        return result
