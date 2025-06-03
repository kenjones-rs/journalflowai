class AudioProcessor:
    def __init__(self, audio_repo, transcriber, classifier, enricher):
        """
        :param audio_repo: An instance of AudioMessageRepository
        :param transcriber: A service that implements transcribe(file_path) -> str
        :param classifier: A service that implements classify(text) -> str
        :param enricher: A service that implements enrich(text, message_type) -> dict
        """
        self.audio_repo = audio_repo
        self.transcriber = transcriber
        self.classifier = classifier
        self.enricher = enricher

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

        # Classify
        message_type = self.classifier.classify(transcription)
        self.audio_repo.upsert({
            "id": message_id,
            "message_type": message_type,
            "status": "classified"
        })

        # Enrich
        enrichment = self.enricher.enrich(transcription, message_type)
        self.audio_repo.update_json_column("audio_message", {"id": message_id}, "enrichment", enrichment)

        # Complete
        self.audio_repo.update_status(message_id, "complete")
