import os
import tempfile
import shutil
from abc import ABC, abstractmethod
from pydub import AudioSegment


class Transcriber(ABC):
    def __init__(self, chunk_length_ms=30000, temp_dir=None):
        self.chunk_length_ms = chunk_length_ms
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self.transcription = []

    def convert_to_wav(self, input_path):
        ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        if ext not in ("m4a", "mp3"):
            raise ValueError(f"Unsupported input format: .{ext}")

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        wav_path = os.path.join(self.temp_dir, f"{base_name}.wav")

        with open(input_path, "rb") as f:
            audio = AudioSegment.from_file(f, format=ext)
            audio.export(wav_path, format="wav").close()

        return wav_path

    def chunk_audio(self, wav_path):
        audio = AudioSegment.from_wav(wav_path)
        chunks = []
        for i in range(0, len(audio), self.chunk_length_ms):
            chunk = audio[i:i + self.chunk_length_ms]
            chunk_path = os.path.join(self.temp_dir, f"chunk_{i // self.chunk_length_ms}.wav")
            chunk.export(chunk_path, format="wav").close()
            chunks.append(chunk_path)
        return chunks

    def cleanup(self):
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @abstractmethod
    def transcribe(self, input_path):
        pass
