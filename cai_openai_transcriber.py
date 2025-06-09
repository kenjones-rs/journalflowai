import os
import tempfile
import shutil
import whisper
from cai_transcriber import Transcriber  # Adjust path if needed


class WhisperTranscriber(Transcriber):
    def __init__(self, model_size="base", chunk_length_ms=30000, temp_dir=None):
        super().__init__(chunk_length_ms=chunk_length_ms, temp_dir=temp_dir)
        self.model = whisper.load_model(model_size)

    def transcribe(self, input_path):
        wav_path = self.convert_to_wav(input_path)

        # Whisper transcribes the entire file at once
        result = self.model.transcribe(wav_path)
        self.transcription.append(result["text"])

        return result["text"]
