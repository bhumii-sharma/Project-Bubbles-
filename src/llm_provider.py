import os
import sys
from dotenv import load_dotenv

# Configure UTF-8 encoding for Windows terminal output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Load .env file
load_dotenv()

# Google Gemini Support (Free & Fast)
try:
    from google import genai
    _GENAI_INSTALLED = True
except ImportError:
    _GENAI_INSTALLED = False
    genai = None

# OpenAI Support
try:
    from openai import OpenAI, RateLimitError, AuthenticationError
    _OPENAI_INSTALLED = True
except ImportError:
    _OPENAI_INSTALLED = False
    OpenAI = None
    RateLimitError = Exception
    AuthenticationError = Exception

_gemini_client = None
_openai_client = None

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash"
]

OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo"
]


def get_gemini_client():
    """Lazily initializes Google Gemini client with Free tier API Key."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    if not _GENAI_INSTALLED or genai is None:
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    api_key = api_key.strip().strip("'").strip('"')
    if not api_key:
        return None

    try:
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except Exception:
        return None


def get_openai_client():
    """Lazily initializes OpenAI client if funded API Key is provided."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    if not _OPENAI_INSTALLED or OpenAI is None:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    api_key = api_key.strip().strip("'").strip('"')
    if not api_key or "your_openai_api_key_here" in api_key:
        return None

    try:
        _openai_client = OpenAI(api_key=api_key)
        return _openai_client
    except Exception:
        return None


def is_available():
    """Returns True if at least one LLM provider is available."""
    return get_gemini_client() is not None or get_openai_client() is not None


def _extract_gemini_text(response):
    """Safely extracts text content from Google Gemini response objects."""
    if not response:
        return None
    try:
        if getattr(response, "text", None):
            return response.text
        if hasattr(response, "candidates") and response.candidates:
            cand = response.candidates[0]
            if hasattr(cand, "content") and cand.content and hasattr(cand.content, "parts"):
                parts_text = [p.text for p in cand.content.parts if hasattr(p, "text") and p.text]
                if parts_text:
                    return "\n".join(parts_text)
    except Exception:
        pass
    return None


def generate_response(prompt, system_prompt=None, temperature=0.7):
    """
    Generates an intelligent response using Google Gemini (Free & Fast),
    with multi-model fallback and optional OpenAI support.
    """
    # 1. Primary: Google Gemini (100% Free & Lightning Fast)
    gemini = get_gemini_client()
    if gemini:
        full_content = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        for model in GEMINI_MODELS:
            try:
                res = gemini.models.generate_content(
                    model=model,
                    contents=full_content,
                )
                text = _extract_gemini_text(res)
                if text:
                    return text
            except Exception:
                continue

    # 2. Secondary: OpenAI (if configured and funded)
    openai_client = get_openai_client()
    if openai_client:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for model in OPENAI_MODELS:
            try:
                res = openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    timeout=8.0,
                )
                if res and res.choices and res.choices[0].message.content:
                    return res.choices[0].message.content
            except (RateLimitError, AuthenticationError):
                break
            except Exception:
                continue

    return None