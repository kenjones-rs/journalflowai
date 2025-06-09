from cai_google_transcriber import GoogleTranscriber
from cai_openai_transcriber import WhisperTranscriber

def create_transcriber(class_name: str):
    """
    Factory method to instantiate a Transcriber based on class_name.

    :param class_name: String from config.transcriber (e.g., "GoogleTranscriber")
    :return: An instance of the transcriber class
    """
    class_map = {
        "GoogleTranscriber": GoogleTranscriber,
        "WhisperTranscriber": WhisperTranscriber
    }

    cls = class_map.get(class_name)
    if not cls:
        raise ValueError(f"Unsupported transcriber class: {class_name}")

    return cls()
