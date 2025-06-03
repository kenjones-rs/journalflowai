from cai_repository import Repository

class AudioMessageRepository(Repository):
    def get_by_id(self, message_id):
        return self.fetch_record("audio_message", {"id": message_id})

    def get_by_status(self, status):
        return self.fetch_record("audio_message", {"status": status})

    def get_pending_messages(self):
        return self.get_by_status("new")

    def upsert(self, message_record):
        self.upsert_record("audio_message", message_record)

    def update_status(self, message_id, new_status):
        self.update_json_column(
            table="audio_message",
            key_columns={"id": message_id},
            json_key="status",
            json_value=new_status
        )
