import whisper


# Load Whisper model once
model = whisper.load_model("base")


def transcribe_audio(audio_path):
    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe"
    )

    return result["text"].strip()
