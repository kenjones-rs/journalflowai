class ChatSession:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def reset(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]
