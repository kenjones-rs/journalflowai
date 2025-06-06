import speech_recognition as sr
from cai_transcriber import Transcriber  # adjust import path as needed


class GoogleTranscriber(Transcriber):
    def __init__(self, chunk_length_ms=30000, temp_dir=None):
        super().__init__(chunk_length_ms, temp_dir)
        self.recognizer = sr.Recognizer()

    def transcribe(self, input_path):
        wav_path = self.convert_to_wav(input_path)
        chunks = self.chunk_audio(wav_path)

        for chunk_path in chunks:
            with sr.AudioFile(chunk_path) as source:
                audio_data = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio_data)
                self.transcription.append(text)
            except sr.UnknownValueError:
                self.transcription.append("[Unrecognized speech]")
            except sr.RequestError:
                self.transcription.append("[Error processing request]")

        return " ".join(self.transcription)
