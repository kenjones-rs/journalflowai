class AudioProcessor:
    def __init__(self, audio_repo, transcriber):
        """
        :param audio_repo: An instance of AudioMessageRepository
        :param transcriber: A service that implements transcribe(file_path) -> str
        """
        self.audio_repo = audio_repo
        self.transcriber = transcriber

    def run(self):
        messages = self.audio_repo.get_pending_messages()
        for message in messages:
            self.process_message(message)

    def process_message(self, message):
        message_id = message['id']
        file_path = message['filename']

        # Transcribe
        transcription = self.transcriber.transcribe(file_path)
        self.audio_repo.upsert({
            "id": message_id,
            "transcription": transcription,
            "status": "transcribed"
        })

        # Complete
        self.audio_repo.update_status(message_id, "complete")
