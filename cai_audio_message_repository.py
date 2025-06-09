from cai_repository import Repository

class AudioMessageRepository(Repository):
    def get_by_id(self, message_id):
        return self.fetch_record("audio_message", {"id": message_id})

    def get_by_status(self, status):
        return self.fetch_record("audio_message", {"status": status})

    def get_pending_messages(self):
        return self.get_by_status("new")

    def upsert(self, record):
        self.upsert_record("audio_message", record)

    def update_status(self, message_id, new_status):
        self.db.execute_query(
            "UPDATE data.audio_message SET status = %s WHERE id = %s",
            (new_status, message_id)
        )

