# llm_factory.py
from cai_llm_openai import OpenAILLM

def create_llm(provider: str, model_name: str):
    if provider.lower() == "openai":
        return OpenAILLM(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
