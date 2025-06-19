import os
import time
from cai_config_repository import ConfigRepository
from cai_audio_message_repository import AudioMessageRepository
from cai_llm_usage_repository import LLMUsageRepository
from cai_action_processor import ActionProcessor
from cai_llm_factory import create_llm

class AudioProcessor:
    def __init__(self, config_repo: ConfigRepository, audio_message_repo: AudioMessageRepository, llm_usage_repo: LLMUsageRepository, transcriber):
        """
        :param audio_message_repo: An instance of AudioMessageRepository
        :param transcriber: A service that implements transcribe(file_path) -> str
        """
        self.config_repo = config_repo
        self.audio_message_repo = audio_message_repo
        self.llm_usage_repo = llm_usage_repo
        self.transcriber = transcriber

    def run(self):

        # transcribe new messages
        messages = self.audio_message_repo.get_by_status('new')
        for message in messages:
            print(message)
            self.transcribe_message(message)

        # process transcribed messages
        messages = self.audio_message_repo.get_by_status('transcribed')
        for message in messages:
            print(message)
            self.process_message(message)

        # Complete
        #self.audio_message_repo.update_status(message_id, 'complete')


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

        with self.audio_message_repo.transaction():
            self.audio_message_repo.upsert(record)

    def process_message(self, message):
        entity_type = 'audio_message'
        message_type = message.get("message_type")
        message_id = message.get("id")
        status = message.get("status")

        # 1. Get process steps and action definitions
        process_steps = self.config_repo.get_process_steps(message_type, status)
        if not process_steps:
            print(f"No process steps found for message_type='{message_type}', status='{status}'")
            return

        for step in process_steps:
            action_label = step['action_label']
            next_status = step['next_status']
            action_processor = ActionProcessor(self.config_repo, self.audio_message_repo, self.llm_usage_repo, 
                                               ai_client_registry={ "openai": create_llm("openai", "gpt-4.1") })

            try:
                response = action_processor.execute(action_label, message, entity_type=entity_type)
                with self.audio_message_repo.transaction():
                    self.audio_message_repo.update_status(message_id, next_status)

            except Exception as e:
                print(f"Error executing action '{action_label}' for message {message['id']}: {e}")
