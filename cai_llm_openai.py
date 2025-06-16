# llm_openai.py
import openai
from openai.error import OpenAIError
from cai_llm_base import LLM
from cai_chat_session import ChatSession  # Adjust import path as needed

class OpenAILLM(LLM):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def chat(self, chat_session: ChatSession) -> dict:
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=chat_session.messages
            )
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI chat request failed: {str(e)}")

        content = response.choices[0].message.content.strip()
        chat_session.add_message("assistant", content)

        return {
            "response": content,
            "prompt_token_count": response.usage.prompt_tokens,
            "response_token_count": response.usage.completion_tokens,
            "chat_session": chat_session
        }
