import difflib
import re


# Very common English words.
# We don't want these to dominate the learner's
# practice list.
COMMON_WORDS = {
    "a", "an", "the",
    "and", "or", "but",
    "to", "of", "in", "on", "at",
    "for", "with", "from",
    "is", "are", "was", "were",
    "am", "be", "been",
    "it", "this", "that",
    "i", "you", "he", "she",
    "we", "they",
    "my", "your", "his", "her",
    "me", "us", "them"
}


def load_transcripts(video_path, user_path):
    """Load the reference and learner transcripts."""

    with open(video_path, "r", encoding="utf-8") as f:
        video_text = f.read().strip()

    with open(user_path, "r", encoding="utf-8") as f:
        user_text = f.read().strip()

    return video_text, user_text


def clean_text(text):
    """Normalize text before comparison."""

    text = text.lower()

    # Make different apostrophe characters consistent
    text = text.replace("’", "'")

    # Remove punctuation but keep apostrophes
    text = re.sub(r"[^\w\s']", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_words_differences(video_text, user_text):
    """
    Compare the learner's transcript with the reference.

    Returns a dictionary containing:
        - similarity
        - practice_words
        - matched_words
        - missed_words
        - extra_words
        - reference_words
        - user_words
        - speech_detected
    """

    video_clean = clean_text(video_text)
    user_clean = clean_text(user_text)

    video_words = video_clean.split()
    user_words = user_clean.split()

    # ---------------------------------------------------------
    # Empty reference
    # ---------------------------------------------------------

    if not video_words:
        return {
            "similarity": 0.0,
            "practice_words": [],
            "matched_words": [],
            "missed_words": [],
            "extra_words": [],
            "reference_words": [],
            "user_words": [],
            "speech_detected": False
        }

    # ---------------------------------------------------------
    # No usable learner speech
    # ---------------------------------------------------------

    if not user_words:
        practice_words = [
            word for word in video_words
            if word not in COMMON_WORDS
        ]

        return {
            "similarity": 0.0,
            "practice_words": list(dict.fromkeys(practice_words))[:8],
            "matched_words": [],
            "missed_words": video_words,
            "extra_words": [],
            "reference_words": video_words,
            "user_words": [],
            "speech_detected": False
        }

    # ---------------------------------------------------------
    # Align the two transcripts
    # ---------------------------------------------------------

    matcher = difflib.SequenceMatcher(
        None,
        video_words,
        user_words
    )

    similarity = matcher.ratio() * 100

    matched_words = []
    missed_words = []
    extra_words = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():

        if opcode == "equal":

            matched_words.extend(
                video_words[i1:i2]
            )

        elif opcode == "delete":

            missed_words.extend(
                video_words[i1:i2]
            )

        elif opcode == "insert":

            extra_words.extend(
                user_words[j1:j2]
            )

        elif opcode == "replace":

            missed_words.extend(
                video_words[i1:i2]
            )

            extra_words.extend(
                user_words[j1:j2]
            )

    # ---------------------------------------------------------
    # Find useful practice words
    # ---------------------------------------------------------

    practice_words = []

    for word in missed_words:

        if word not in COMMON_WORDS:
            practice_words.append(word)

    # Remove duplicates while preserving order
    practice_words = list(
        dict.fromkeys(practice_words)
    )

    # Limit the amount of feedback
    practice_words = practice_words[:8]

    # Remove duplicates from other lists
    matched_words = list(
        dict.fromkeys(matched_words)
    )

    missed_words = list(
        dict.fromkeys(missed_words)
    )

    extra_words = list(
        dict.fromkeys(extra_words)
    )

    # ---------------------------------------------------------
    # Determine whether Whisper detected real speech
    # ---------------------------------------------------------

    speech_detected = len(user_words) >= 2

    return {
        "similarity": round(similarity, 2),
        "practice_words": practice_words,
        "matched_words": matched_words,
        "missed_words": missed_words,
        "extra_words": extra_words,
        "reference_words": video_words,
        "user_words": user_words,
        "speech_detected": speech_detected
    }
