import streamlit as st
import os
import shutil
import moviepy as mp
from audio_recorder_streamlit import audio_recorder

from speaking.extract_video_audio import extract_audio
from speaking.record_user import save_browser_audio
from speaking.transcribe import transcribe_audio
from speaking.compare_texts import load_transcripts, get_words_differences
from speaking.feedback import generate_feedback


# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------

st.set_page_config(
    page_title="ShadowSpeak",
    page_icon="🗣️",
    layout="centered"
)

st.title("🗣️ ShadowSpeak")
st.caption("Improve your English speaking skills through shadowing.")


# ---------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------

if "video_processed" not in st.session_state:
    st.session_state.video_processed = False

if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "results" not in st.session_state:
    st.session_state.results = None

if "clip_duration" not in st.session_state:
    st.session_state.clip_duration = 15

if "recorder_key" not in st.session_state:
    st.session_state.recorder_key = 0

if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None


# ---------------------------------------------------------
# Practice Selection
# ---------------------------------------------------------

st.header("Practice Speaking")

source_choice = st.radio(
    "Choose how you want to practice:",
    ["Use a sample video", "Upload my own video"],
    horizontal=True
)

selected_video_path = None
selected_video_id = None

# ---------------------------------------------------------
# Sample Videos Selection
# ---------------------------------------------------------

if source_choice == "Use a sample video":
    SAMPLE_VIDEOS = {
        "Sample 1: Weekend Market": "samples/sample1.mov",
        "Sample 2: Museum Visit": "samples/sample2.mov"
    }

    sample_option = st.selectbox(
        "Select a sample video:",
        list(SAMPLE_VIDEOS.keys())
    )

    sample_file_path = SAMPLE_VIDEOS[sample_option]

    if os.path.exists(sample_file_path):
        os.makedirs("data/videos", exist_ok=True)
        dest_path = os.path.join(
            "data/videos", os.path.basename(sample_file_path))

        # Copy sample to work directory if not already copied
        if not os.path.exists(dest_path):
            shutil.copy(sample_file_path, dest_path)

        selected_video_path = dest_path
        selected_video_id = sample_option
    else:
        st.warning(
            f"Sample video file not found at '{sample_file_path}'. Please verify the 'samples/' folder.")

# ---------------------------------------------------------
# Custom Upload Selection
# ---------------------------------------------------------

else:
    uploaded_video = st.file_uploader(
        "Upload a short speaking video",
        type=["mp4", "mov", "avi"]
    )

    if uploaded_video is not None:
        os.makedirs("data/videos", exist_ok=True)
        video_path = os.path.join("data/videos", uploaded_video.name)

        with open(video_path, "wb") as f:
            f.write(uploaded_video.getbuffer())
            f.flush()

        selected_video_path = video_path
        selected_video_id = uploaded_video.name


# ---------------------------------------------------------
# Process Selected Video
# ---------------------------------------------------------

if selected_video_path is not None:

    # Reset state if a NEW video/sample is selected
    if st.session_state.current_video_id != selected_video_id:
        st.session_state.current_video_id = selected_video_id
        st.session_state.video_processed = False
        st.session_state.video_path = None
        st.session_state.transcript = None
        st.session_state.results = None
        st.session_state.recorder_key += 1

    st.session_state.video_path = selected_video_path

    # Display video
    st.video(selected_video_path)

    # Automatically process video
    if not st.session_state.video_processed:

        with st.spinner("Preparing your practice clip..."):

            try:
                try:
                    video = mp.VideoFileClip(selected_video_path)
                    clip_duration = min(int(video.duration), 15)
                    video.close()
                except Exception:
                    clip_duration = 15

                clip_duration = max(clip_duration, 1)
                st.session_state.clip_duration = clip_duration

                # Extract audio
                audio_path = extract_audio(
                    selected_video_path,
                    duration=clip_duration
                )

                if audio_path:
                    # Transcribe reference audio
                    transcript = transcribe_audio(audio_path)

                    if transcript:
                        os.makedirs("data/transcripts", exist_ok=True)
                        transcript_path = "data/transcripts/video_transcript.txt"

                        with open(transcript_path, "w", encoding="utf-8") as f:
                            f.write(transcript)

                        st.session_state.transcript = transcript
                        st.session_state.video_processed = True
                        st.rerun()
                    else:
                        st.error(
                            "I couldn't understand the speech in this video.")
                else:
                    st.error("I couldn't process the video's audio.")

            except Exception as e:
                st.error(
                    f"Something went wrong while preparing the video: {e}")


# ---------------------------------------------------------
# Reference transcript
# ---------------------------------------------------------

if st.session_state.transcript:

    st.divider()

    st.subheader("📝 Reference Transcript")
    st.info(st.session_state.transcript)

    st.write(
        "Listen to the speaker once. Then try to say "
        "the same words at the same time as the speaker."
    )


# ---------------------------------------------------------
# Shadowing
# ---------------------------------------------------------

if st.session_state.video_processed:

    st.divider()

    st.subheader("🎙️ Ready to Shadow?")

    st.write("Click the microphone below to record your voice from the browser:")

    # Audio recorder with dynamic key for resetting
    audio_bytes = audio_recorder(
        text="Click to start/stop recording",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x",
        key=f"shadow_recorder_{st.session_state.recorder_key}"
    )

    if audio_bytes and st.session_state.results is None:

        user_audio_path = save_browser_audio(audio_bytes)

        if user_audio_path:

            st.success("✅ Recording complete!")

            # Play user's recording
            st.audio(user_audio_path, format="audio/wav")

            # Analyze user's speech
            with st.spinner("🤖 Analyzing your speech..."):

                # Transcribe user's recording
                user_transcript = transcribe_audio(user_audio_path)

                # Save user's transcript
                os.makedirs("data/transcripts", exist_ok=True)
                user_transcript_path = "data/transcripts/user_transcript.txt"

                with open(user_transcript_path, "w", encoding="utf-8") as f:
                    f.write(user_transcript)

                # Compare reference and user transcript
                video_text, user_text = load_transcripts(
                    "data/transcripts/video_transcript.txt",
                    "data/transcripts/user_transcript.txt"
                )

                comparison = get_words_differences(video_text, user_text)
                result = generate_feedback(comparison)

                # Save results and trigger rerun to update UI cleanly
                st.session_state.results = result
                st.rerun()

        else:
            st.error("Something went wrong while saving your recording.")


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

if st.session_state.results:

    st.divider()

    result = st.session_state.results
    st.markdown(result["feedback"])

    st.divider()

    st.write("💡 Listen to the reference one more time, then try shadowing it again.")

    if st.button("🔄 Try Again", use_container_width=True):
        st.session_state.results = None
        st.session_state.recorder_key += 1
        st.rerun()
