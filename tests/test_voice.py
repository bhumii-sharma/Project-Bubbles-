import os
import sys
import pytest

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from voice import (
    clean_text_for_speech,
    is_tts_available,
    speak,
    DEFAULT_VOICE,
)


def test_clean_text_removes_emojis():
    """Verify that cute emojis are stripped for clean TTS speech synthesis."""
    raw = "🫧 Hi Little Star! 🥟 Did you bring momos? ✨🤍🥰"
    cleaned = clean_text_for_speech(raw)
    assert "🫧" not in cleaned
    assert "🥟" not in cleaned
    assert "✨" not in cleaned
    assert "🤍" not in cleaned
    assert "🥰" not in cleaned
    assert "Hi Little Star! Did you bring momos?" in cleaned


def test_clean_text_removes_roleplay_asterisks():
    """Verify that stage directions and asterisks (*gasps*, *hugs*) are stripped."""
    raw = "🥟 *GASP!* Did you say momos?! *forensic inspection activated* Hand them over!"
    cleaned = clean_text_for_speech(raw)
    assert "*GASP!*" not in cleaned
    assert "*forensic inspection activated*" not in cleaned
    assert "Did you say momos?! Hand them over!" in cleaned


def test_clean_text_removes_markdown():
    """Verify markdown bold, headers, and code ticks are removed."""
    raw = "## **Important Bubble Announcement**: You are `amazing`!"
    cleaned = clean_text_for_speech(raw)
    assert "#" not in cleaned
    assert "*" not in cleaned
    assert "`" not in cleaned
    assert "Important Bubble Announcement: You are amazing!" in cleaned


def test_clean_text_empty_and_whitespace():
    """Verify that None, empty string, or pure emoji input returns empty string safely."""
    assert clean_text_for_speech("") == ""
    assert clean_text_for_speech(None) == ""
    assert clean_text_for_speech("🫧🥟🤍✨") == ""


def test_tts_availability():
    """Verify TTS system is detected as available."""
    assert is_tts_available() is True


def test_speak_clean_execution():
    """Verify speak function runs with sanitized text without crashing."""
    # Simple short sentence
    result = speak("Hello tiny human! Testing voice protocol.", block=False)
    # Result should be a boolean (True on success, False if no audio device / offline)
    assert isinstance(result, bool)


def test_default_voice_configured():
    """Verify default voice is configured."""
    assert DEFAULT_VOICE in ["auto", "en-US-AnaNeural"]


def test_detect_language_hindi():
    """Verify Hindi Devanagari script is detected accurately."""
    from voice import detect_language, get_voice_for_text
    lang = detect_language("नमस्ते, आप कैसी हो Bubbles?")
    assert lang == "hindi"
    voice, _, _ = get_voice_for_text("नमस्ते")
    assert "hi-IN" in voice or "Swara" in voice


def test_detect_language_hinglish():
    """Verify Roman script Hinglish words are detected accurately."""
    from voice import detect_language, get_voice_for_text
    lang = detect_language("kaise ho aap? aaj bohot thak gayi hoon, momo khana hai")
    assert lang == "hinglish"
    voice, _, _ = get_voice_for_text("kaise ho aap")
    assert "en-IN" in voice or "Neerja" in voice


def test_detect_language_english():
    """Verify English text is routed to standard English voice."""
    from voice import detect_language, get_voice_for_text
    lang = detect_language("Hello Little Star, I hope you are having an amazing day!")
    assert lang == "english"
    voice, _, _ = get_voice_for_text("Hello Little Star")
    assert "en-US" in voice or "Ana" in voice
