from cai_audio_message_repository import AudioMessageRepository

class AudioProcessor:
    def __init__(self, audio_repo: AudioMessageRepository, transcriber):
        """
        :param audio_repo: An instance of AudioMessageRepository
        :param transcriber: A service that implements transcribe(file_path) -> str
        """
        self.audio_repo = audio_repo
        self.transcriber = transcriber

    def run(self):
        messages = self.audio_repo.get_by_status('new')
        for message in messages:
            print(message)
            self.process_message(message)

    def process_message(self, message):
        file_path = message['filename']
        transcription = self.transcriber.transcribe(file_path)

        # Update only the relevant fields
        message['transcription'] = transcription
        message['status'] = 'transcribed'

        # remove keys not expected in upsert
        message.pop('id', None)
        message.pop('created_at', None)
        with self.audio_repo.transaction():
            self.audio_repo.upsert(message)

        # Complete
        #self.audio_repo.update_status(message_id, 'complete')
