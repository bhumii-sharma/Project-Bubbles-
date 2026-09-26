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

# Optional Edge-TTS for ultra-natural, cute neural voice (Baby Dory English)
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


# Baby Dory Signature Voice Profile (Sweet, cheerful, high-pitch English voice)
DEFAULT_VOICE = os.getenv("BUBBLES_VOICE", "en-US-AnaNeural")
DEFAULT_PITCH = os.getenv("BUBBLES_PITCH", "+12Hz")
DEFAULT_RATE = os.getenv("BUBBLES_RATE", "+6%")
DEFAULT_LANGUAGE = os.getenv("BUBBLES_LANGUAGE", "en-IN")

# Pygame mixer initialization lock
_mixer_lock = threading.Lock()
_mixer_initialized = False

# Speech recognition instance & calibration lock
_sr_lock = threading.Lock()
_recognizer = None
_calibrated = False


def _get_recognizer():
    """Lazily initializes and tunes SpeechRecognizer with balanced sensitivity."""
    global _recognizer
    if not _SR_AVAILABLE or sr is None:
        return None
    with _sr_lock:
        if _recognizer is None:
            _recognizer = sr.Recognizer()
            # Balanced energy threshold to ignore breathing, sighing, and ambient background hum
            _recognizer.energy_threshold = 380
            _recognizer.dynamic_energy_threshold = True
            _recognizer.dynamic_energy_adjustment_damping = 0.15
            _recognizer.dynamic_energy_ratio = 1.5
            _recognizer.pause_threshold = 0.8  # Natural conversational pause
            _recognizer.phrase_threshold = 0.3  # Requires intentional speech, ignores quick sniffs/clicks
            _recognizer.non_speaking_duration = 0.4
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


def _speak_offline_fallback(text: str) -> dict:
    """Offline speech fallback using native OS SAPI5 / espeak via pyttsx3."""
    if not _PYTTSX3_AVAILABLE or pyttsx3 is None:
        return {"success": False, "interrupted": False, "user_text": None}

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")
        for v in voices:
            if "zira" in v.name.lower() or "female" in v.name.lower() or "david" not in v.name.lower():
                engine.setProperty("voice", v.id)
                break

        engine.say(text)
        engine.runAndWait()
        return {"success": True, "interrupted": False, "user_text": None}
    except Exception:
        return {"success": False, "interrupted": False, "user_text": None}


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


def speak(text: str, voice: str = None, pitch: str = None, rate: str = None, block: bool = True, allow_interrupt: bool = True) -> dict:
    """
    Speaks the given text using high-quality Baby Dory neural TTS (en-US-AnaNeural)
    with seamless offline fallback (pyttsx3) and verified real-time interruption (barge-in).

    Verified Interruption Guarantee:
    - Audio is ONLY stopped if actual recognized human speech is detected.
    - Breathing, sighs, coughs, and ambient noise are ignored, allowing speech to continue uninterrupted.
    """
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        return {"success": False, "interrupted": False, "user_text": None}

    selected_voice = voice if voice else DEFAULT_VOICE
    selected_pitch = pitch if pitch is not None else DEFAULT_PITCH
    selected_rate = rate if rate is not None else DEFAULT_RATE

    # 1. Primary: Edge-TTS Neural Voice (Baby Dory English)
    if _EDGE_TTS_AVAILABLE and _PYGAME_AVAILABLE:
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_file = f.name

            # Generate audio with Baby Dory voice and pitch
            _run_coroutine(_generate_edge_tts_audio(
                cleaned_text,
                temp_file,
                voice=selected_voice,
                pitch=selected_pitch,
                rate=selected_rate,
            ))

            if not _init_mixer():
                return {"success": False, "interrupted": False, "user_text": None}

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            if not block:
                return {"success": True, "interrupted": False, "user_text": None}

            interrupted_event = threading.Event()
            recognized_holder = {"text": None}

            stop_listener = None

            if allow_interrupt and _SR_AVAILABLE and sr is not None:
                # Dedicated interruption recognizer with higher threshold to prevent speaker feedback & breath triggers
                inter_rec = sr.Recognizer()
                inter_rec.energy_threshold = 550  # Intentional human voice threshold
                inter_rec.dynamic_energy_threshold = False
                inter_rec.phrase_threshold = 0.35  # Requires intentional speech (filters out short breath/rustle)
                inter_rec.pause_threshold = 0.8

                def _on_phrase_detected(recognizer, audio):
                    # 1. First verify if actual human words were spoken (DO NOT cut off on noise/breathing)
                    spoken_text = None
                    for lang in ["en-IN", "en-US", "hi-IN"]:
                        try:
                            transcript = recognizer.recognize_google(audio, language=lang)
                            if transcript and len(transcript.strip()) >= 2:
                                spoken_text = transcript.strip()
                                break
                        except Exception:
                            continue

                    # 2. ONLY cut off playback if valid speech was recognized!
                    if spoken_text:
                        try:
                            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                                pygame.mixer.music.stop()
                        except Exception:
                            pass
                        recognized_holder["text"] = spoken_text
                        interrupted_event.set()

                try:
                    mic = sr.Microphone()
                    stop_listener = inter_rec.listen_in_background(mic, _on_phrase_detected, phrase_time_limit=10)
                except Exception:
                    stop_listener = None

            try:
                # Wait for audio to finish OR until verified interruption occurs
                while pygame.mixer.music.get_busy():
                    if interrupted_event.is_set():
                        break
                    time.sleep(0.04)
            finally:
                if stop_listener:
                    try:
                        stop_listener(wait_for_stop=False)
                    except Exception:
                        pass

            if interrupted_event.is_set():
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                except Exception:
                    pass

                return {
                    "success": True,
                    "interrupted": True,
                    "user_text": recognized_holder["text"]
                }

            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass

            return {
                "success": True,
                "interrupted": False,
                "user_text": None
            }

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


def listen(timeout: int = 7, phrase_time_limit: int = 15, language: str = DEFAULT_LANGUAGE) -> str | None:
    """
    Captures audio from the microphone with balanced sensitivity and converts speech to text.
    Filters out background noise, breathing, and sighing while reliably capturing conversational speech.
    Returns the recognized string, or None if silence/timeout.
    """
    if not _SR_AVAILABLE or sr is None:
        return None

    recognizer = _get_recognizer()
    if not recognizer:
        return None

    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (speak freely)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        print("🔄 Processing speech...")
        
        # 1. Primary recognition (Indian English / en-IN - highly accurate for Indian English speech)
        try:
            transcript = recognizer.recognize_google(audio, language="en-IN")
            if transcript and len(transcript.strip()) >= 2:
                return transcript.strip()
        except sr.UnknownValueError:
            pass

        # 2. Secondary fallback (US English / en-US)
        try:
            transcript = recognizer.recognize_google(audio, language="en-US")
            if transcript and len(transcript.strip()) >= 2:
                return transcript.strip()
        except sr.UnknownValueError:
            pass

        # 3. Tertiary fallback (Hindi / hi-IN)
        try:
            transcript = recognizer.recognize_google(audio, language="hi-IN")
            if transcript and len(transcript.strip()) >= 2:
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
    except Exception:
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
    print("🫧 Testing Bubbles Voice Engine (English Baby Dory with Verified Interruption)")
    print("=" * 50)
    test_phrase = "🫧 Hi Little Star! 🥟 I'm Bubbles, your favorite momo companion! ✨🤍"
    print(f"\nOriginal text: {test_phrase}")
    sanitized = clean_text_for_speech(test_phrase)
    print(f"Sanitized text: {sanitized}")

    print("\n🔊 Speaking test phrase with Baby Dory voice...")
    result = speak(test_phrase, block=True, allow_interrupt=False)
    print(f"Playback status: {'✅ SUCCESS' if result.get('success') else '❌ FAILED'}")

    if is_voice_input_available():
        print("\n🎤 Testing microphone... (Say something in English within 5s)")
        spoken = listen(timeout=5, phrase_time_limit=10)
        print(f"Recognized speech: {spoken}")
    else:
        print("\n🎤 Microphone hardware not detected (Text input will be used).")
