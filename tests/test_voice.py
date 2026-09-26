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
    DEFAULT_PITCH,
    DEFAULT_RATE,
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
    result = speak("Hello tiny human! Testing Baby Dory voice protocol.", block=False)
    assert isinstance(result, bool)


def test_default_baby_dory_voice_configured():
    """Verify default Baby Dory neural voice parameters."""
    assert DEFAULT_VOICE == "en-US-AnaNeural"
    assert DEFAULT_PITCH == "+12Hz"
    assert DEFAULT_RATE == "+6%"
