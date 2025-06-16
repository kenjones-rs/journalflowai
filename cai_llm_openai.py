# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import openai
from openai import OpenAIError
from cai_llm_base import LLM
from cai_chat_session import ChatSession

class OpenAILLM(LLM):
    def __init__(self, model_name: str, api_key: str = None):
        self.model_name = model_name
        self.client = openai.Client(api_key=api_key)

    def set_model_name(self, model_name: str):
        """Dynamically change the model name used for future requests."""
        self.model_name = model_name

    def chat(self, chat_session: ChatSession, temperature:float = 0.0) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=chat_session.messages,
                temperature=temperature
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

if __name__ == "__main__":
    # Example usage
    chat_session = ChatSession('You are a helpful technology advisor')
    chat_session.add_message("user", "What are the benefits of using PostgreSQL for analytics?")

    llm = OpenAILLM("gpt-4o")  # Assumes OPENAI_API_KEY is in environment or set explicitly
    llm.set_model_name("gpt-4.1")
    result = llm.chat(chat_session)

    print("Response:", result["response"])
    print("Prompt tokens:", result["prompt_token_count"])
    print("Response tokens:", result["response_token_count"])
