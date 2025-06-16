# llm_base.py
from abc import ABC, abstractmethod
from cai_chat_session import ChatSession  # Adjust the import path as needed

class LLM(ABC):
    @abstractmethod
    def chat(self, chat_session: ChatSession) -> dict:
        pass
