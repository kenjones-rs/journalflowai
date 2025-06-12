# llm_openai.py
import openai
from llm_base import LLM

class OpenAILLM(LLM):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def chat(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
