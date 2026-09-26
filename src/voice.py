import os
import re
import sys
import time
import asyncio
import tempfile
import threading
import concurrent.futures

# Suppress pygame welcome banner in console
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

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


# Multilingual Voice Profiles (Neural Edge-TTS)
VOICE_MAP = {
    "hindi": {
        "voice": "hi-IN-SwaraNeural",           # Sweet, expressive native Hindi voice
        "pitch": "+5Hz",
        "rate": "+2%",
    },
    "hinglish": {
        "voice": "en-IN-NeerjaExpressiveNeural",  # Natural Indian accent for Roman Hinglish
        "pitch": "+6Hz",
        "rate": "+4%",
    },
    "english": {
        "voice": "en-US-AnaNeural",              # Cute, warm Baby Dory child voice
        "pitch": "+8Hz",
        "rate": "+5%",
    },
}

DEFAULT_VOICE = os.getenv("BUBBLES_VOICE", "auto")
DEFAULT_PITCH = os.getenv("BUBBLES_PITCH", None)
DEFAULT_RATE = os.getenv("BUBBLES_RATE", None)
DEFAULT_LANGUAGE = os.getenv("BUBBLES_LANGUAGE", "en-IN")


def detect_language(text: str) -> str:
    """
    Detects whether dialogue is Devanagari Hindi, Roman Hinglish, or English.
    """
    if not text:
        return "english"

    # 1. Hindi Devanagari Unicode Block (\u0900-\u097F)
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    # 2. Hinglish marker words
    hinglish_keywords = {
        "kya", "hai", "hain", "ho", "nahi", "nhi", "haan", "haa", "mujhe", "tum", "tumhara",
        "aap", "aapka", "kaise", "kaisi", "kaisa", "aaj", "bhi", "karo", "kuch", "bohot",
        "bahut", "khana", "yaar", "kaun", "kyun", "kyu", "achha", "achhi", "theek", "bolo",
        "batao", "suno", "meri", "mera", "mere", "hum", "kar", "rahe", "rahi", "gaya",
        "gayi", "momo", "momos", "thak", "accha", "thik", "matlab", "karein", "dekho",
        "dekh", "chalo", "chal", "paas", "sath", "saath", "baat", "krenge", "karenge",
        "khaye", "khaya", "khao", "pyar", "pyaar", "bataiye", "hona", "hoga", "hogi"
    }
    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]+\b", text)]
    if any(w in hinglish_keywords for w in words):
        return "hinglish"

    return "english"


def get_voice_for_text(text: str) -> tuple[str, str, str]:
    """
    Automatically returns (voice_name, pitch, rate) matching the language of the dialogue.
    """
    lang = detect_language(text)
    cfg = VOICE_MAP.get(lang, VOICE_MAP["english"])
    return cfg["voice"], cfg["pitch"], cfg["rate"]

# Pygame mixer initialization lock
_mixer_lock = threading.Lock()
_mixer_initialized = False

# Speech recognition instance & calibration lock
_sr_lock = threading.Lock()
_recognizer = None
_calibrated = False


def _get_recognizer():
    """Lazily initializes and tunes SpeechRecognizer for high sensitivity and low latency."""
    global _recognizer
    if not _SR_AVAILABLE or sr is None:
        return None
    with _sr_lock:
        if _recognizer is None:
            _recognizer = sr.Recognizer()
            # High sensitivity settings so soft/normal voices are clearly detected
            _recognizer.energy_threshold = 200  # Sensitive base threshold
            _recognizer.dynamic_energy_threshold = True
            _recognizer.dynamic_energy_adjustment_damping = 0.15
            _recognizer.dynamic_energy_ratio = 1.3
            _recognizer.pause_threshold = 0.65  # Quick turnaround after speech ends
            _recognizer.phrase_threshold = 0.2
            _recognizer.non_speaking_duration = 0.3
        return _recognizer


def calibrate_microphone(duration: float = 0.5) -> bool:
    """Calibrates microphone ambient noise once at startup."""
    global _calibrated
    if not _SR_AVAILABLE or sr is None:
        return False
    rec = _get_recognizer()
    if not rec:
        return False
    try:
        with sr.Microphone() as source:
            rec.adjust_for_ambient_noise(source, duration=duration)
            _calibrated = True
            return True
    except Exception:
        return False


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


def _run_coroutine(coro):
    """Safely executes an async coroutine across sync contexts or existing event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


def speak(text: str, voice: str = None, pitch: str = None, rate: str = None, block: bool = True) -> bool:
    """
    Speaks the given text using high-quality neural TTS (Edge-TTS)
    with seamless offline fallback (pyttsx3).
    Automatically detects language (Hindi, Hinglish, English) and routes to the matching native voice.
    Automatically sanitizes text (removes emojis and roleplay asterisks).
    """
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        return False

    # Auto-detect language voice profile if not explicitly specified
    auto_voice, auto_pitch, auto_rate = get_voice_for_text(cleaned_text)
    selected_voice = voice if (voice and voice != "auto") else auto_voice
    selected_pitch = pitch if pitch is not None else auto_pitch
    selected_rate = rate if rate is not None else auto_rate

    # 1. Primary: Edge-TTS Neural Voice
    if _EDGE_TTS_AVAILABLE and _PYGAME_AVAILABLE:
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_file = f.name

            # Generate audio with matched voice and pitch
            _run_coroutine(_generate_edge_tts_audio(
                cleaned_text,
                temp_file,
                voice=selected_voice,
                pitch=selected_pitch,
                rate=selected_rate,
            ))

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


def listen(timeout: int = 5, phrase_time_limit: int = 8, language: str = DEFAULT_LANGUAGE) -> str | None:
    """
    Captures audio from the microphone with high sensitivity and converts speech to text.
    Uses fast pause detection and Indian English / Hinglish accent recognition.
    Returns the recognized string, or None if no speech was detected/unintelligible.
    """
    global _calibrated
    if not _SR_AVAILABLE or sr is None:
        return None

    recognizer = _get_recognizer()
    if not recognizer:
        return None

    try:
        with sr.Microphone() as source:
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(source, duration=0.4)
                _calibrated = True

            print("🎤 (Listening... speak into mic)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        print("🔄 Processing speech...")
        # 1. Primary recognition (e.g. en-IN / Indian English & Hinglish)
        try:
            transcript = recognizer.recognize_google(audio, language=language)
            if transcript:
                return transcript.strip()
        except sr.UnknownValueError:
            # 2. Secondary fallback recognition (en-US or hi-IN)
            alt_lang = "en-US" if language != "en-US" else "hi-IN"
            try:
                transcript = recognizer.recognize_google(audio, language=alt_lang)
                if transcript:
                    return transcript.strip()
            except Exception:
                pass

        return None
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"⚠️ Speech Recognition network error: {e}")
        return None
    except Exception as e:
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


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🫧 Testing Bubbles Voice Engine")
    print("=" * 50)
    test_phrase = "🫧 Hi Little Star! 🥟 I'm Bubbles, your favorite momo companion! ✨🤍"
    print(f"\nOriginal text: {test_phrase}")
    sanitized = clean_text_for_speech(test_phrase)
    print(f"Sanitized text: {sanitized}")

    print("\n🔊 Speaking test phrase...")
    success = speak(test_phrase, block=True)
    print(f"Playback status: {'✅ SUCCESS' if success else '❌ FAILED'}")

    if is_voice_input_available():
        print("\n🎤 Testing microphone... (Say something within 5s)")
        result = listen(timeout=5, phrase_time_limit=6)
        print(f"Recognized speech: {result}")
    else:
        print("\n🎤 Microphone hardware not detected (Text input will be used).")
