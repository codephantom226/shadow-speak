from moviepy.editor import VideoFileClip
import os


def extract_audio(video_path, duration, output_audio_path="data/recordings/extracted_audio.wav"):
    try:
        # load the video file
        video = VideoFileClip(video_path)

        # Cut the Video to the first duration seconds
        if duration > video.duration:
            duration = int(video.duration)

        video = video.subclip(0, duration)

        # Extract the audio
        audio = video.audio

        # Make sure the folder where we want to save the ausio exists
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)

        # Write the audio to WAV file
        audio.write_audiofile(output_audio_path)

        return output_audio_path

    except Exception as e:
        print(f"❌ Failed to extract audio: {e}")
        return None
