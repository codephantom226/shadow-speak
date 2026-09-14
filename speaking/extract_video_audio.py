from moviepy import VideoFileClip
import subprocess
import os

def extract_audio(video_path, audio_output_path="temp_audio.wav"):
    # Try extracting with direct FFmpeg command line first (most reliable for MOV)
    try:
        command = [
            "ffmpeg", "-y", "-i", video_path, 
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", 
            audio_output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return audio_output_path
    except Exception:
        # Fallback to MoviePy if FFmpeg CLI isn't reachable directly
        clip = VideoFileClip(video_path)
        if clip.audio is not None:
            clip.audio.write_audiofile(
                audio_output_path, 
                fps=44100, 
                nbytes=2, 
                codec='pcm_s16le'
            )
            clip.close()
            return audio_output_path
        else:
            clip.close()
            raise ValueError("No audio track found in the video file.")
