from moviepy import VideoFileClip

def extract_audio(video_path, audio_output_path):
    clip = VideoFileClip(video_path)
    if clip.audio is not None:
        # Force export using a standard WAV/PCM audio codec
        clip.audio.write_audiofile(audio_output_path, codec='pcm_s16le')
        clip.close()
        return True
    else:
        clip.close()
        raise ValueError("No audio track found in the video file.")
