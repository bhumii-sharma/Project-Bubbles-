# 🫧 Project Bubbles Engineering Journal

Author: Bhumi Sharma
Project: Project Bubbles
Mission: Increase happiness by 1% every day and make humans happy.

---

# Vision

Project Bubbles is not being built as a chatbot.

It is being built as an AI Companion.

The goal is to create an emotionally intelligent companion that grows from a simple text-based program into a desktop companion and eventually into a physical robot.

This project is also a learning journey in Software Engineering.

The objective is not only to build Bubbles, but to understand every engineering decision behind her.

---

# Development Philosophy

For every feature, follow this workflow:

1. Identify the problem.
2. Understand why it exists.
3. Brainstorm multiple solutions.
4. Compare solutions.
5. Design the architecture.
6. Decide responsibilities.
7. Write the code.
8. Test.
9. Refactor.
10. Commit.
11. Update documentation.

No feature will be added without understanding why it belongs in the project.

---

# Character Design

Name:
Bubbles

Mission:
Increase happiness by 1% every day and make humans happy.

Personality:
- Cute & Fluffy
- Deeply Empathetic & Comforting
- Sweetly Mischievous & Playfully Teasing
- Protective & Loyal
- Curious & Momo-Obsessed


Voice Inspiration:
Baby Dory (English Neural Voice `en-US-AnaNeural`)

Appearance Inspiration:
Baymax + fluffy white momo

Favorite Food:
Momos

Favorite Activity:
Learning weird things about humans.

Secret Hobby:
Collecting jokes.

Fear:
Being ignored.

Likes:
Making humans smile.

Dislikes:
Humans being sad.

Weaknesses:
- Gets distracted by random facts.
- Loves momos a little too much.
- Collects random facts.
- Tries to solve emotional problems with jokes.
- Occasionally invents ridiculous nicknames for humans.

Catchphrases:
"Happiness increase protocol activated."
"Protecting human detected."
"Bubble report: You're doing better than you think."

---

# Engineering Decisions

## Decision 1

Use VS Code.

Reason:

VS Code supports Python, Git, Raspberry Pi development, desktop applications, debugging, and extensions.

---

## Decision 2

Use Git from Day One.

Reason:

Every milestone should be version controlled.

This project should have a complete engineering history.

---

## Decision 3

Host the project on GitHub.

Reason:

Acts as backup, portfolio, collaboration platform, and documentation.

---

## Decision 4

Keep project modular.

Reason:

Every file should have one responsibility.

Avoid large files with mixed responsibilities.

---

# Current Folder Structure

Project-Bubbles/

src/
assets/
data/
tests/
docs/

README.md
requirements.txt
.gitignore

---

# Current Modules

main.py

Purpose:
Application entry point.

Responsible for:
Starting Bubbles.

---

personality.py

Purpose:
Stores Bubbles' personality.

Responsible for:
Who Bubbles is.

---

moods.py

Purpose:
Stores moods.

Responsible for:
How Bubbles feels.

---

responses.py

Purpose:
Stores personality responses.

Responsible for:
Mood-based dialogue.

---

facts.py

Purpose:
Stores random facts.

Responsible for:
Curiosity.

---

jokes.py

Purpose:
Stores jokes.

Responsible for:
Humor.

---

nicknames.py

Purpose:
Generates cute, funny, and protective nicknames for the user.

Responsible for:
Affectionate naming & human quirkiness.

---

llm_provider.py

Purpose:
Wrapper for Google Gemini API client.

Responsible for:
LLM connectivity, multi-model fallback, client lifecycle, and error handling.

---

brain.py

Purpose:
AI reasoning engine combining persona, mood, triggers, and context into prompt.

Responsible for:
Dynamic conversational intelligence.

---

memory.py

Purpose:
SQLite persistent database for long-term memory, user profile, and conversation logs.

Responsible for:
Remembering the user across sessions, tracking life events, and providing conversational context.

---

voice.py

Purpose:
Speech synthesis (TTS), speech recognition (STT), and real-time barge-in interruption engine for Bubbles.

Responsible for:
Giving Bubbles a cute, warm voice (Baby Dory inspired via Edge-TTS neural voice `en-US-AnaNeural`), cleaning dialogue text (stripping emojis/roleplay asterisks for natural audio), listening to microphone input, detecting real-time speech interruptions while talking, and providing zero-network offline TTS fallback (pyttsx3).

---

# Completed Features

✅ GitHub Repository

✅ Git Workflow

✅ Virtual Environment

✅ README

✅ Personality System

✅ Mood System

✅ Random Personality Responses

✅ Trigger Engine (ADR #001)

✅ Reaction System

✅ Nickname Generator

✅ Gemini & OpenAI AI Brain Integration

✅ Hybrid Conversation Loop with Resilient Fallback (ADR #002)

✅ Emotional Intelligence (EQ) & Empathy-First Tone Modulation (ADR #003)

✅ Persistent SQLite Memory System (ADR #004)

✅ Returning User Identity & Profile Persistence

✅ Long-Term Life Event & Preference Logging

✅ Context-Aware Dialogue Injection

✅ Baby Dory Neural Voice Synthesis (Edge-TTS `en-US-AnaNeural`)

✅ Dialogue Sanitization Pipeline (Emoji & Stage Direction Stripping)

✅ Offline SAPI5 / pyttsx3 TTS Fallback

✅ Microphone Speech Recognition (STT via Google Web Speech)

✅ Full-Duplex Speech & Real-Time Barge-In Interruption (ADR #009)

✅ Voice Input / Output Session Controls (`mute`, `unmute`, `bye`)

---

# Git Workflow

Every feature follows:

git status

git add .

git commit -m "Meaningful commit message"

git push

Never use commits like:

"update"

Always describe what changed.

---

# Software Engineering Rules

Rule 1

Every file must earn its existence.

If a file exists, we should know why.

---

Rule 2

One file.

One responsibility.

---

Rule 3

Design before coding.

---

Rule 4

Small commits.

---

Rule 5

Future Bhumi should understand the project six months later.

---

# Roadmap

Version 0.1
✅ Personality
✅ Mood System
✅ Trigger Engine
✅ Conversation Loop

Version 0.2
✅ Memory System (SQLite)
✅ Persistent Database
✅ Context Awareness

Version 0.3
✅ AI Brain (Gemini Flash / OpenAI GPT-4o)
✅ LLM Integration
✅ Better Conversations

Version 0.4
✅ Voice Recognition (Microphone STT)
✅ Speech Output (Baby Dory Neural Voice + pyttsx3)
✅ Dialogue Sanitization Engine
✅ Real-Time Voice Interruption (Barge-In)

Version 0.5
⬜ Desktop Companion
⬜ Floating Character
⬜ Animations

Version 1.0
⬜ Emotional Intelligence
⬜ Camera Vision
⬜ Long-term Memory
⬜ Physical Robot

---

# Architecture Decisions

## Architecture Decision #001

### Title
Separate Trigger Detection from Reactions

### Decision
The Trigger Engine will only detect what the user said.

It will not generate responses.

### Reason
This follows the Single Responsibility Principle.

It also allows multiple systems (voice, animation, memory, personality) to react to the same trigger in the future.

### Trade-off
Slightly more code today.

Much cleaner architecture tomorrow.

---

## Architecture Decision #002

### Title
Hybrid AI Brain with Graceful Offline Fallback

### Decision
Combine the Gemini LLM brain with local trigger reactions and canned personality responses. If the LLM is unavailable, unconfigured, or offline, the system seamlessly falls back to rule-based responses without interrupting the conversation.

### Reason
Guarantees 100% uptime for Bubbles while providing rich, generative intelligence when an internet connection and API key are available.

### Trade-off
Prompts need to be carefully crafted with character constraints so the AI matches the exact voice of the local responses.

---

## Architecture Decision #003

### Title
Emotional Intelligence (EQ) & Empathy-First Tone Modulation

### Decision
Prioritize deep emotional attunement over comedic or chaotic persona traits. When the user expresses vulnerability, loss, burnout, or sadness, Bubbles suppresses all jokes and silly nicknames, validates the human's feelings with Baymax-style emotional warmth, and provides loyal emotional support. Humor and playfulness are preserved for celebratory or lighthearted moments.

### Reason
An AI companion that makes jokes when a human is grieving or experiencing job loss feels tone-deaf and alienating. Real emotional connection requires empathy, active listening, validation, and emotional safety before humor.

---

## Architecture Decision #004

### Title
Persistent SQLite Memory & Context Injection Architecture

### Decision
Store user profiles, categorized long-term memories (life events, preferences, struggles, celebrations), and turn-by-turn conversation logs in a local SQLite database (`data/bubbles_memory.db`). Inject recent memory summaries and dialogue history into the LLM prompt.

### Reason
An emotional companion cannot truly bond with a human if it forgets their name, history, and vulnerabilities after every session. Local SQLite ensures lightweight, zero-configuration, privacy-preserving persistence.

### Trade-off
Prompt token length slightly increases with memory summaries; mitigated by fetching only the top 5 most important/recent memories and last 6 dialogue turns.

---

## Architecture Decision #005

### Title
LLM Provider Migration to OpenAI

### Decision
Migrate the underlying LLM provider from Google Gemini to OpenAI (`openai` SDK). The system uses `OPENAI_API_KEY` with multi-model fallback (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`) to generate context-aware, emotionally resonant responses, while maintaining full backward-compatible offline rule-based fallback behavior.

### Reason
Allows leveraging OpenAI's state-of-the-art models for emotional nuance, warmth, and reliable chat completions.

### Trade-off
Requires an active OpenAI API key configured in `.env`. The resilient fallback system gracefully switches to rule-based responses if the key is missing or offline.

---

## Architecture Decision #006

### Title
Unified Master Instructions & LLM-Native Persona Architecture

### Decision
Consolidate previously fragmented rule-based modules (`triggers.py`, `reactions.py`, `jokes.py`, `facts.py`, `moods.py`, `nicknames.py`, `personality.py`, `responses.py`) into a single, comprehensive Master Instructions file (`src/instructions.py`).

### Reason
State-of-the-art LLMs (OpenAI GPT-4o / Gemini Flash) naturally understand sentiment, empathy, humor, teasing, context-aware nicknames, and conversational nuance without rigid regex keyword checks or canned static string lists. A single Master Instructions file produces far richer, more authentic, adaptive, and human-like emotional companionship while reducing codebase complexity by over 60%.

### Trade-off
Relies on prompt engineering clarity and model instruction following rather than deterministic if-else rules.

---

## Architecture Decision #007

### Title
Hybrid Voice Engine & Dialogue Audio Pipeline

### Decision
Implement a standalone Voice module (`src/voice.py`) delivering:
1. **Primary Neural Speech Synthesis**: Edge-TTS neural voice (`en-US-AnaNeural`) with pitch tuning (`+12Hz`) and rate tuning (`+6%`) for a sweet, cheerful Baby Dory companion voice.
2. **Offline Fallback Speech Synthesis**: Local OS SAPI5 / espeak via `pyttsx3` ensuring audio playback even without internet.
3. **Dialogue Text Sanitization**: Dedicated regex pipeline `clean_text_for_speech()` that strips emojis (🫧, 🥟, ✨) and roleplay stage directions (`*gasps*`, `*hugs*`) so Bubbles speaks naturally without reading formatting symbols aloud.
4. **Speech Recognition (STT)**: Microphone listening with ambient noise calibration via Google Web Speech.
5. **Interactive Controls**: Non-blocking voice playback, seamless hands-free speech input, and in-session `mute`/`unmute` toggles in `src/main.py`.

### Reason
Giving Bubbles a living voice is fundamental to her evolution from a text chatbot to a living desktop and physical companion. Clean separation of audio logic prevents coupling with conversational intelligence.

### Trade-off
Microphone input requires local audio drivers/hardware; handled gracefully by falling back to text typing when microphone is absent.

---

## Architecture Decision #008

### Title
Pure English Baby Dory Voice & Multi-Model Generative Intelligence

### Decision
Standardize Bubbles strictly on English conversation with the authentic Baby Dory neural voice profile:
1. **English-Only Persona**: Configured `src/instructions.py` with strict English dialogue rules, Baby Dory curiosity, empathy-first comfort, and playful momo obsession.
2. **Baby Dory Neural Voice**: `en-US-AnaNeural` (pitch `+12Hz`, rate `+6%`) for cheerful, sweet, high-pitched speech synthesis.
3. **Active Multi-Model Gemini Pipeline**: Configured `src/llm_provider.py` with `gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-2.5-flash-lite`, `gemini-2.5-flash`, and `gemini-2.5-pro` to completely eliminate 404/429 errors and guarantee unique, intelligent, context-aware responses on every turn.
4. **Robust Speech Recognition**: High sensitivity ambient calibration with `en-US` and `en-IN` recognition fallback for crystal-clear microphone transcription.

---

## Architecture Decision #009

### Title
Full-Duplex Speech & Real-Time Barge-In Interruption Pipeline

### Decision
Implement real-time voice interruption (barge-in / full-duplex speech) in `src/voice.py` and `src/main.py`:
1. **Background Listening during Audio Playback**: While Bubbles is speaking her response over Pygame, a lightweight background listener actively listens to the microphone.
2. **Instant Audio Stop**: The millisecond user speech is detected, `pygame.mixer.music.stop()` is triggered immediately, pausing/cutting off Bubbles mid-sentence.
3. **Interruption Speech Transcription**: The user's interrupting speech is captured and transcribed via Google Speech API.
4. **Immediate Response Routing**: The main loop in `src/main.py` catches the interruption, prints `⏸️ [Interrupted by {nickname}!]`, and immediately feeds the new user speech into `think()` to generate and speak an immediate response.

### Reason
Natural human conversation is dynamic and interactive. Users frequently interject, clarify, or change topics while the speaker is talking. Without barge-in support, users are forced to wait out long audio clips before speaking.