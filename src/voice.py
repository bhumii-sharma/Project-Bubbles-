import os
import re
import sys
import time
import asyncio
import tempfile
import threading

# Configure UTF-8 encoding for Windows terminal output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional Edge-TTS for ultra-natural, cute neural voice (Baby Dory inspired)
try:
    import edge_tts
    _EDGE_TTS_AVAILABLE = True
except ImportError:
    _EDGE_TTS_AVAILABLE = False
    edge_tts = None

# Optional Pygame for audio playback
try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False
    pygame = None

# Optional pyttsx3 for 100% offline fallback TTS
try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False
    pyttsx3 = None

# Optional SpeechRecognition for voice input (STT)
try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False
    sr = None


# Default Voice Settings (Baby Dory inspired: cute, warm, expressive child/female voice)
DEFAULT_VOICE = os.getenv("BUBBLES_VOICE", "en-US-AnaNeural")
DEFAULT_PITCH = os.getenv("BUBBLES_PITCH", "+8Hz")
DEFAULT_RATE = os.getenv("BUBBLES_RATE", "+5%")

# Pygame mixer initialization lock
_mixer_lock = threading.Lock()
_mixer_initialized = False


def _init_mixer():
    """Safely initializes pygame audio mixer."""
    global _mixer_initialized
    if not _PYGAME_AVAILABLE:
        return False
    with _mixer_lock:
        if not _mixer_initialized:
            try:
                pygame.mixer.init()
                _mixer_initialized = True
            except Exception:
                return False
        return True


def clean_text_for_speech(text: str) -> str:
    """
    Sanitizes dialogue text before feeding into Text-To-Speech engine:
    1. Preserves text inside bold/italics while removing markdown syntax (**, __, #, >, `)
    2. Removes roleplay actions inside single asterisks (*gasps*, *softly hugs you*)
    3. Removes emojis (🫧, 🥟, ✨, 🤍, 🥰, etc.)
    4. Normalizes whitespace and punctuation
    """
    if not text:
        return ""

    # 1. Remove markdown headers and formatting markers (**bold** -> bold, `code` -> code)
    cleaned = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)  # **bold** -> bold
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)      # __bold__ -> bold
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)        # `code` -> code

    # 2. Remove roleplay action directions inside single asterisks (*gasps*, *happy wiggles*)
    cleaned = re.sub(r"\*[^*]+?\*", "", cleaned)

    # 3. Remove leftover markdown symbols and URLs
    cleaned = re.sub(r"[\#\_\`\>\[\]]", "", cleaned)
    cleaned = re.sub(r"http\S+|www\.\S+", "", cleaned)

    # 4. Remove emojis using comprehensive unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010ffff"  # Supplemental symbols & pictographs
        "\U00002600-\U000027bf"  # Misc symbols & Dingbats
        "\U00002300-\U000023ff"  # Misc technical
        "\U00002b50-\U00002b55"  # Stars
        "\U0000fe00-\U0000fe0f"  # Variation selectors
        "]+",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", cleaned)

    # 5. Clean up redundant spaces and punctuation
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"([!?.,])\1+", r"\1", cleaned)  # Replace !!! with !
    cleaned = cleaned.strip()

    return cleaned


async def _generate_edge_tts_audio(text: str, output_path: str, voice: str = DEFAULT_VOICE, pitch: str = DEFAULT_PITCH, rate: str = DEFAULT_RATE):
    """Asynchronously generates neural audio file via Edge-TTS."""
    communicate = edge_tts.Communicate(text, voice=voice, pitch=pitch, rate=rate)
    await communicate.save(output_path)


def _play_audio_file(file_path: str, block: bool = True):
    """Plays an audio file using Pygame Mixer and releases file lock upon completion."""
    if not _init_mixer():
        return False

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        if block:
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            # Stop and unload to release Windows file lock
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        return True
    except Exception:
        return False


def _speak_offline_fallback(text: str):
    """Offline speech fallback using native OS SAPI5 / espeak via pyttsx3."""
    if not _PYTTSX3_AVAILABLE or pyttsx3 is None:
        return False

    try:
        engine = pyttsx3.init()
        # Set speed & volume
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        # Try to select female voice if available
        voices = engine.getProperty("voices")
        for v in voices:
            if "zira" in v.name.lower() or "female" in v.name.lower() or "david" not in v.name.lower():
                engine.setProperty("voice", v.id)
                break

        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False


def speak(text: str, voice: str = DEFAULT_VOICE, block: bool = True) -> bool:
    """
    Speaks the given text using high-quality neural TTS (Edge-TTS)
    with seamless offline fallback (pyttsx3).
    Automatically sanitizes text (removes emojis and roleplay asterisks).
    """
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        return False

    # 1. Primary: Edge-TTS Neural Voice (Baby Dory inspired)
    if _EDGE_TTS_AVAILABLE and _PYGAME_AVAILABLE:
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_file = f.name

            # Generate audio
            asyncio.run(_generate_edge_tts_audio(cleaned_text, temp_file, voice=voice))

            # Play audio
            success = _play_audio_file(temp_file, block=block)
            return success
        except Exception:
            # Fall back to offline TTS on network failure or edge-tts exception
            pass
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    # 2. Resilient Offline Fallback: pyttsx3
    return _speak_offline_fallback(cleaned_text)


def listen(timeout: int = 5, phrase_time_limit: int = 10, language: str = "en-US") -> str | None:
    """
    Captures audio from the microphone and converts speech to text.
    Returns the recognized string, or None if no speech was detected/unintelligible.
    """
    if not _SR_AVAILABLE or sr is None:
        print("\n⚠️ SpeechRecognition is not available.")
        return None

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening... (speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        print("🔄 Processing speech...")
        transcript = recognizer.recognize_google(audio, language=language)
        return transcript.strip()
    except sr.WaitTimeoutError:
        print("⏳ No speech detected within timeout.")
        return None
    except sr.UnknownValueError:
        print("❓ Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Speech Recognition service error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Microphone error: {e}")
        return None


def is_voice_input_available() -> bool:
    """Checks if speech recognition and microphone hardware are accessible."""
    if not _SR_AVAILABLE or sr is None:
        return False
    try:
        with sr.Microphone():
            return True
    except Exception:
        return False


def is_tts_available() -> bool:
    """Checks if either Edge-TTS or pyttsx3 is available."""
    return (_EDGE_TTS_AVAILABLE and _PYGAME_AVAILABLE) or _PYTTSX3_AVAILABLE
