# prompt_builder.py
class PromptBuilder:
    def __init__(self, config_repo):
        self.config_repo = config_repo

    def build_prompt(self, prompt_label: str, param_values: dict) -> str:
        # Fetch prompt template
        prompt_rows = self.config_repo.fetch_prompt(prompt_label)
        if not prompt_rows:
            raise ValueError(f"No prompt found for label: {prompt_label}")
        prompt_template = prompt_rows[0]["prompt_template"]

        # Fetch parameter definitions
        params = self.config_repo.fetch_prompt_parameters(prompt_label)
        inputs = {}
        for p in params:
            name = p["parameter_name"]
            is_required = p["is_required"]
            default = p["default_value"]
            max_length = p.get("max_length", 500)

            if name in param_values:
                value = str(param_values[name])[:max_length]
                inputs[name] = value
            elif default is not None:
                value = str(default)[:max_length]
                inputs[name] = value
            elif is_required:
                raise ValueError(f"Missing required parameter: {name}")

        # Format the template with values
        return prompt_template.format(**inputs)

