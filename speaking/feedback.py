def generate_feedback(comparison):
    """
    Create simple and actionable feedback for an English learner.
    """

    similarity = comparison["similarity"]
    practice_words = comparison["practice_words"]
    speech_detected = comparison["speech_detected"]

    # ---------------------------------------------------------
    # No usable speech
    # ---------------------------------------------------------

    if not speech_detected:
        return {
            "similarity": 0.0,
            "feedback": """
## Your Shadowing Result

### We couldn't understand your recording

We did not hear enough clear speech to analyze your attempt.

### 🎙️ Try again

Check your microphone and speak clearly while the speaker is talking.

**Listen → Shadow → Try again**
""".strip()
        }

    # ---------------------------------------------------------
    # Simple performance message
    # ---------------------------------------------------------

    if similarity >= 85:
        message = "Excellent! You matched most of the speaker's words."
    elif similarity >= 70:
        message = "Great job! You matched many of the speaker's words."
    elif similarity >= 50:
        message = "Good start! You matched some of the speaker's words."
    else:
        message = "Let's try again. Listen closely and speak with the speaker."

    # ---------------------------------------------------------
    # Practice words
    # ---------------------------------------------------------

    if practice_words:
        words = " · ".join(practice_words[:6])

        practice_section = f"""
### 🔎 Focus on these words

**{words}**

Listen to the speaker say each word.
Then say it yourself.
"""
    else:
        practice_section = """
### 🎉 Great work

We did not find any important words to practice.
"""

    # ---------------------------------------------------------
    # Final feedback
    # ---------------------------------------------------------

    feedback = f"""
## 🎯 Your Shadowing Result

### Word Match: {similarity}%

{message}

{practice_section}

### 🎧 Try this next

**Listen to the speaker again.**

Then speak **at the same time** as the speaker.

Try to copy their **words, rhythm, and pauses**.

---

### 🔄 Ready to try again?

**Listen → Shadow → Try again**
"""

    return {
        "similarity": round(similarity, 2),
        "feedback": feedback.strip()
    }
