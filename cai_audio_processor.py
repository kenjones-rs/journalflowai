import os
import time
from cai_config_repository import ConfigRepository
from cai_audio_message_repository import AudioMessageRepository

class AudioProcessor:
    def __init__(self, config_repo: ConfigRepository, audio_repo: AudioMessageRepository, transcriber):
        """
        :param audio_repo: An instance of AudioMessageRepository
        :param transcriber: A service that implements transcribe(file_path) -> str
        """
        self.config_repo = config_repo
        self.audio_repo = audio_repo
        self.transcriber = transcriber

    def run(self):

        # transcribe new messages
        messages = self.audio_repo.get_by_status('new')
        for message in messages:
            print(message)
            self.transcribe_message(message)

        # categorize transcribed messages
        messages = self.audio_repo.get_by_status('transcribed')
        for message in messages:
            print(message)
            self.categorize_message(message)

        # process other message statuses

        # Complete
        #self.audio_repo.update_status(message_id, 'complete')


    def transcribe_message(self, message):
        file_path = message['filename']
        normalized_path = file_path.replace("\\", "/")

        # --- Transcription timing ---
        start_time = time.time()
        transcription = self.transcriber.transcribe(normalized_path)
        transcription_duration = round(time.time() - start_time)

        # --- Word count ---
        word_count = len(transcription.split())

        # --- Upsert all values ---
        record = {
            "filename": normalized_path,
            "message_type": message.get("message_type"),  # preserve if present
            "status": "transcribed",
            "audio_file_size_kb": message.get("audio_file_size_kb"),
            "audio_duration_seconds": message.get("audio_duration_seconds"),
            "transcription": transcription,
            "transcription_duration_seconds": transcription_duration,
            "transcription_word_count": word_count,
            "metadata": message.get("metadata", {}),
            "enrichment": message.get("enrichment", {})
        }

        if "id" in record:
            del record["id"]  # remove id before upsert if present

        with self.audio_repo.transaction():
            self.audio_repo.upsert(record)

    def categorize_message(self, message):
        file_path = message['filename']
        normalized_path = file_path.replace("\\", "/")

        # --- Categorization into message_type timing ---
        start_time = time.time()
        categorization_duration = round(time.time() - start_time)

        # --- Upsert all values ---
        record = {
            "filename": normalized_path,
            "message_type": message.get("message_type"),  # preserve if present
            "status": "categorized",
            "audio_file_size_kb": message.get("audio_file_size_kb"),
            "audio_duration_seconds": message.get("audio_duration_seconds"),
            "transcription": message.get("transcription"),
            "transcription_duration_seconds": message.get("transcription_duration"),
            "transcription_word_count": message.get("transcription_word_count"),
            "metadata": message.get("metadata", {}),
            "enrichment": message.get("enrichment", {})
        }

        if "id" in record:
            del record["id"]  # remove id before upsert if present

        with self.audio_repo.transaction():
            self.audio_repo.upsert(record)