# 📝 Mistakes & Lessons Learned

A running engineering log of mistakes made, why they happened, and how they were solved.

---

### Mistake #001: Tone-Deaf Jokes During User Distress
- **Symptom**: When the user shared painful real-life hardship (*"I just lost my job..."*), Bubbles responded with chaotic quips (*"Whoa, hold up there, sparkly!"*).
- **Root Cause**: The prompt over-indexed on "chaotic" traits and "solving emotional problems with jokes" without establishing emotional attunement or sadness triggers for life events (job loss, layoffs, burnout).
- **Fix**: Redesigned Bubbles with **Empathy-First Architecture (ADR #003)**. Emotional distress triggers now suppress jokes, validate pain sincerely, and provide Baymax-style warmth before any humor.

---

### Mistake #002: Windows Console `cp1252` Encoding Crash
- **Symptom**: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'`.
- **Root Cause**: Windows default terminal encoding does not support UTF-8 emoji output without reconfiguration.
- **Fix**: Added `sys.stdout.reconfigure(encoding="utf-8")` to `main.py` and test suites.

---

### Mistake #003: Tight Coupling and Module Import Paths
- **Symptom**: Direct script execution (`python tests/test_brain.py`) failed to find `src` modules without explicit path configuration.
- **Fix**: Standardized `sys.path.insert(0, ...)` across all entry points and test scripts so they run cleanly from any working directory.

---

### Mistake #004: Hardcoded Top-Level Assertions Crashing Pytest Collection
- **Symptom**: `pytest` crashed at collection phase with `AssertionError: assert None is not None` when running test files with module-level execution.
- **Root Cause**: Test files were originally written as standalone linear scripts executing assertions at top-level import time without `def test_*():` function wrappers or offline tolerance.
- **Fix**: Wrapped all test suites inside standard pytest `def test_*():` functions and added graceful handling for offline fallback mode.

---

### Mistake #005: Fragmented Rule-Based Architecture Overcomplicating LLM Workflows
- **Symptom**: 8+ fragmented rule files (`triggers.py`, `reactions.py`, `jokes.py`, `nicknames.py`, `moods.py`, `responses.py`, `facts.py`) created maintenance clutter and brittle keyword matching.
- **Root Cause**: Legacy pre-LLM heuristic patterns were retained after integrating GPT-4o, creating redundant layers of if-else checks that restricted the LLM's natural conversational abilities.
- **Fix**: Consolidated all persona, empathy, teasing, momo protocols, and nickname guidance into a single Master Instructions file (`src/instructions.py`) (ADR #006).

---

### Mistake #006: Function-Level Dynamic Imports Causing Linter & IDE Resolution Issues
- **Symptom**: Editor linters reported `cannot resolve import 'openai'` and runtime errors occurred when switching between virtual and global Python environments.
- **Root Cause**: Importing packages dynamically inside helper functions (`get_client()`) caused IDE static analyzers to miss symbols, and dependencies were not synchronized across interpreters.
- **Fix**: Structured imports at the module top-level with safe `try...except ImportError` guards (`_OPENAI_INSTALLED`), dual-path module import fallbacks (`from brain` vs `from src.brain`), and synchronized dependencies.

---

### Mistake #007: Unvalidated Placeholder API Keys Triggering False Availability
- **Symptom**: `is_available()` reported `True` when `.env` contained default placeholder values like `your_openai_api_key_here`, leading to unhandled 401 API exceptions.
- **Root Cause**: Checked only for string presence rather than validating against known template placeholders.
- **Fix**: Added explicit filtering in `get_client()` to reject placeholder tokens and cleanly route to offline fallback mode.

---

### Mistake #008: Retrying Exhausted Quota Across Models Causing High Latency & Repetitive Fallbacks
- **Symptom**: Responses suffered 10-15s delay and Bubbles repeated the exact same static sentence on every turn.
- **Root Cause**: When the user's OpenAI account had 0 credits (`credit_balance_exhausted` 429), `generate_response()` sequentially retried all 3 fallback models (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`) over the network instead of failing fast, and `main.py` had only a single hardcoded fallback message.
- **Fix**: Implemented fast-fail on `RateLimitError` (`insufficient_quota`) and `AuthenticationError` to eliminate latency, added user-visible diagnostic alerts with billing URL, and implemented dynamic context-aware fallback generation (`get_dynamic_fallback()`) in `main.py`.

---

### Mistake #009: Backslash Escape Inside F-String Expression in Python < 3.12
- **Symptom**: `SyntaxError: f-string expression part cannot include a backslash` when launching `main.py` on Python 3.10.
- **Root Cause**: In Python versions earlier than 3.12, backslashes (`\"`) are strictly forbidden inside f-string interpolation braces `{...}`.
- **Fix**: Precomputed conditional status string variables before f-string printing.

---

### Mistake #010: Retired Model Names in Gemini Fallback Pipeline Causing Canned Fallbacks
- **Symptom**: Repetitive canned fallback replies when user talked to Bubbles in terminal.
- **Root Cause**: `GEMINI_MODELS` list contained `gemini-1.5-flash` which was retired/not found (404) and `gemini-2.5-flash` which reached rate limit quotas (429). When both failed, `generate_response()` returned `None`, triggering repetitive static offline fallback lines in `main.py`.
- **Fix**: Updated `GEMINI_MODELS` to use current active high-throughput models (`gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemini-2.5-pro`). Verified dynamic sub-second generative intelligence on every turn.

---

### Mistake #011: Unvalidated Audio Triggers During Playback Causing Hyper-Sensitive Self-Interruption
- **Symptom**: Bubbles stopped talking mid-sentence whenever the user took a breath, shifted in their seat, or when laptop speakers played Bubbles' own voice.
- **Root Cause**:
  1. `energy_threshold` was set too low (`180`), capturing breathing, ambient room noise, and speaker bleed.
  2. The interruption callback immediately halted audio playback (`pygame.mixer.music.stop()`) on *raw sound detection* before verifying if actual human words were spoken.
- **Fix**:
  1. Implemented **Word-Verified Interruption**: Speech recognition now transcribes the audio chunk first; playback is ONLY stopped if valid, recognizable speech words (`len(transcript) >= 2`) are detected. Coughs, breathing, and ambient noise are ignored.
  2. Balanced `energy_threshold = 380` (normal listening) and `550` (during playback) with `phrase_threshold = 0.35s` to filter out non-verbal audio.
