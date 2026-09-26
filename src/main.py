import os
import sys
import random

# Configure UTF-8 encoding for Windows terminal output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Ensure local src imports work reliably
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from brain import think
    from llm_provider import is_available
    from memory import (
        init_db,
        get_profile_value,
        set_profile_value,
        save_memory,
        save_conversation_turn,
        format_memory_context,
    )
    from voice import (
        speak,
        listen,
        is_tts_available,
        is_voice_input_available,
    )
except ImportError:
    from src.brain import think
    from src.llm_provider import is_available
    from src.memory import (
        init_db,
        get_profile_value,
        set_profile_value,
        save_memory,
        save_conversation_turn,
        format_memory_context,
    )
    from src.voice import (
        speak,
        listen,
        is_tts_available,
        is_voice_input_available,
    )


def get_dynamic_fallback(user_message, nickname):
    """
    Generates varied, personality-rich fallback responses when LLM is offline or out of quota.
    Prevents repetitive single-sentence loops.
    """
    msg_lower = user_message.lower()

    if any(w in msg_lower for w in ["momo", "dumpling"]):
        return random.choice([
            f"🥟 *GASP!* Did you say momos?! I demand a 50% momo tax right now, {nickname}! 🥺",
            f"🥟 Momos are proof that good things exist in the universe! Did you save any for me, {nickname}? 🫧",
            f"🥟 *forensic momo inspection activated* I smell dumplings! Hand over the plate! 🔍✨",
        ])

    if any(w in msg_lower for w in ["sad", "job", "lost", "tired", "exhausted", "cry", "pain", "stress", "fail", "burnout"]):
        return random.choice([
            f"🫧 *softly sits next to you* I know things feel heavy right now, {nickname}. Take a deep breath. You are stronger than this moment, and I'm right here with you. 🤍",
            f"🤍 It's completely okay to feel tired or hurt, {nickname}. You don't have to carry everything alone. I'm right beside you through the storm. 🫧",
            f"🫧 *wraps you in a warm fluffy hug* You are worthy, loved, and this hard chapter does not define you. One step at a time, my sweet human. 🤍",
        ])

    if any(w in msg_lower for w in ["hi", "hello", "hey", "sup", "morning", "evening"]):
        return random.choice([
            f"🫧 Yay! Hello {nickname}! My circuits are sparkling just seeing you! ✨",
            f"🫧 Hi {nickname}! How is my favorite human doing today? 🤍",
            f"🫧 *happy wiggles* Hello! What fun or cozy things are we doing today? 🌸",
        ])

    if any(w in msg_lower for w in ["joke", "funny"]):
        return random.choice([
            "🫧 Why did the momo go to school? To become a smart dumpling! 🥟😂",
            "🫧 What do you call a happy cloud? Bubbles on a Tuesday! ☁️✨",
        ])

    return random.choice([
        f"🫧 I'm listening closely, {nickname}! Tell me everything! 🤍",
        f"🥰 You're doing great today, {nickname}! Remember Bubbles is always cheering for you! ✨",
        f"🫧 *nods attentively* I'm right here with you, tiny human! 🤍",
        f"✨ Every day with you is 1% happier, {nickname}! What's on your mind? 🫧",
    ])


def start_bubbles():
    """Main execution loop for Bubbles conversational companion."""
    # Initialize persistent memory database
    init_db()

    tts_ready = is_tts_available()
    mic_ready = is_voice_input_available()
    voice_enabled = tts_ready

    brain_status = "[ONLINE]" if is_available() else "[OFFLINE FALLBACK]"
    tts_status = "[ONLINE - Baby Dory Neural]" if tts_ready else "[DISABLED]"
    mic_status = '[READY - type "mic" to speak]' if mic_ready else "[TEXT ONLY]"

    print("\n" + "=" * 55)
    print("🫧  Bubbles is waking up...")
    print(f"🧠  Brain:        {brain_status}")
    print(f"🔊  Voice Output: {tts_status}")
    print(f"🎤  Voice Input:  {mic_status}")
    print("=" * 55)

    # Check if returning human or first meeting
    stored_name = get_profile_value("user_name")
    stored_nickname = get_profile_value("nickname")

    if stored_name:
        user_name = stored_name
        nickname = stored_nickname or stored_name
        greeting = f"Welcome back, {nickname}! 🫧🤍 I missed you so much!"
        print(f"\nBubbles: {greeting}")
        if voice_enabled:
            speak(f"Welcome back, {nickname}! I missed you so much!")
    else:
        user_name = input("\nWhat's your name? ").strip()
        if not user_name:
            user_name = "Human"

        nickname = f"Pocket Human {user_name}"
        set_profile_value("user_name", user_name)
        set_profile_value("nickname", nickname)
        greeting = f"Hi {user_name}! From now on, you're my favorite {nickname}! 🫧🤍"
        print(f"\nBubbles: {greeting}")
        if voice_enabled:
            speak(f"Hi {user_name}! From now on, you are my favorite {nickname}!")

    print("\n(Commands: 'mic' = speak into mic, 'mute'/'unmute' = toggle voice, 'bye' = exit)\n" + "-" * 55)

    while True:
        try:
            prompt_label = f"\n{nickname}: "
            user_input = input(prompt_label).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n🫧 *gasps* Goodbye tiny human! 🤍")
            if voice_enabled:
                speak("Goodbye tiny human! Take care!")
            break

        if not user_input:
            continue

        # Handle Voice Input Command
        if user_input.lower() in ["mic", "/mic", "listen", "voice", "/voice"]:
            if not mic_ready:
                print("⚠️ Microphone is not available. Please type your message instead.")
                continue
            spoken_text = listen(timeout=5, phrase_time_limit=10)
            if not spoken_text:
                print("🫧 Bubbles: I couldn't hear anything, tiny human. Try again or type it! 🤍")
                continue
            print(f"🗣️ (Heard): {spoken_text}")
            user_message = spoken_text
        elif user_input.lower() == "mute":
            voice_enabled = False
            print("🔇 Voice output muted.")
            continue
        elif user_input.lower() == "unmute":
            voice_enabled = True
            print("🔊 Voice output enabled.")
            if tts_ready:
                speak("Voice protocol re-activated!")
            continue
        else:
            user_message = user_input

        if user_message.lower() in ["bye", "exit", "quit", "goodbye"]:
            farewell = f"Aww... okay {nickname}. Come back soon! 🤍🫧"
            print(f"\nBubbles: {farewell}")
            if voice_enabled:
                speak(f"Aww, okay {nickname}. Come back soon!")
            break

        # Save user message to persistent conversation history
        save_conversation_turn(nickname, user_message)

        # Automatically save key life context / preferences if mentioned
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["lost my job", "fired", "struggling", "depressed", "exhausted", "burnout"]):
            save_memory("struggle", user_message, importance=5)
        elif any(w in msg_lower for w in ["momo", "dumpling"]):
            save_memory("preference", "Loves momos 🥟", importance=3)
        elif any(w in msg_lower for w in ["promoted", "won", "passed", "got the job", "celebrating"]):
            save_memory("celebration", user_message, importance=4)

        # Fetch relevant memories and recent conversation context
        memory_context = format_memory_context()

        # Generate response through Bubbles' Master Instructions & OpenAI/Gemini
        ai_response = think(
            user_message=user_message,
            user_name=user_name,
            nickname=nickname,
            memory_context=memory_context,
        )

        if ai_response:
            final_response = ai_response.strip()
        else:
            # Varied, dynamic offline fallback
            final_response = get_dynamic_fallback(user_message, nickname)

        print(f"\nBubbles: {final_response}")

        # Speak Bubbles' response aloud with sanitized Baby Dory neural voice
        if voice_enabled:
            speak(final_response)

        # Save Bubbles' response to persistent conversation history
        save_conversation_turn("Bubbles", final_response)


if __name__ == "__main__":
    start_bubbles()