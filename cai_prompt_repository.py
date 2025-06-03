from cai_repository import Repository

class PromptRepository(Repository):
    def get_prompt_by_label(self, label):
        results = self.fetch_record("prompt", {"prompt_label": label})
        return results[0] if results else None

    def upsert(self, prompt_record):
        self.upsert_record("prompt", prompt_record)
