import os


def save_browser_audio(audio_bytes, filename="user_recording.wav"):
    """
    Saves raw audio bytes sent from the browser recorder to disk.
    """
    try:
        os.makedirs("data/recordings", exist_ok=True)
        filepath = os.path.join("data", "recordings", filename)

        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        return filepath

    except Exception as e:
        print(f"Error saving audio: {e}")
        return None
