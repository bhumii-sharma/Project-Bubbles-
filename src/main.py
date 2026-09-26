import os
import re
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
    Generates varied, personality-rich English fallback responses (Baby Dory inspired).
    Prevents repetitive loops when network or LLM connectivity experiences transient delays.
    """
    msg_lower = user_message.lower()

    if any(w in msg_lower for w in ["momo", "dumpling", "food", "snack"]):
        return random.choice([
            f"🥟 *GASP!* Did somebody say momos?! I demand a 50% momo tax right now, {nickname}! 🥺✨",
            f"🥟 Momos are proof that magical things exist in the world! Did you save some for me, {nickname}? 🫧",
            f"🥟 *forensic momo inspection activated* I smell dumplings! Hand over the plate right now! 🔍✨",
            f"🥟 Steamed, fried, or spiced... momos make everything 100% better! What kind are we eating, {nickname}? 😋✨",
        ])

    if any(w in msg_lower for w in ["sad", "job", "lost", "tired", "exhausted", "cry", "pain", "stress", "fail", "burnout", "lonely", "hurt", "bad day"]):
        return random.choice([
            f"🫧 *softly swims closer and sits next to you* I know things feel really heavy right now, {nickname}. Take a slow, deep breath. You are stronger than this moment, and I'm right here holding your hand. 🤍",
            f"🤍 It's completely okay to feel tired or sad today, {nickname}. You don't have to carry the whole world on your shoulders. I'm right here with you, always. 🫧",
            f"🫧 *wraps you in a warm fluffy hug* You are so worthy, loved, and this tough chapter does not define your story. One gentle step at a time, my sweet human. 🤍",
            f"🤍 Just remember my motto: Just keep swimming, just keep swimming! 🫧 You are never alone when Bubbles is around! ✨",
        ])

    if any(w in msg_lower for w in ["hi", "hello", "hey", "sup", "morning", "evening", "howdy", "bubbles"]):
        return random.choice([
            f"🫧 Yay! Hello {nickname}! *happy wiggles* My circuits are sparkling with joy just seeing you! ✨",
            f"🫧 Hi {nickname}! How is my favorite human doing today? Tell me everything! 🤍",
            f"🫧 *gasp* There you are! I was just floating around thinking about you! What adventures are we having today? 🌸✨",
            f"✨ Hello hello! Sending you a giant bubble of sunshine and happiness, {nickname}! 🫧🤍",
        ])

    if any(w in msg_lower for w in ["joke", "funny", "laugh", "make me laugh"]):
        return random.choice([
            "🫧 Why did the little dumpling go to school? To become a smart momo! 🥟😂",
            "🫧 What do you call a happy cloud floating in the sky? Bubbles on a sunny morning! ☁️✨",
            "🫧 What did the ocean say to the little fish? Nothing, it just waved! 🌊🫧",
        ])

    if any(w in msg_lower for w in ["who are you", "what are you", "tell me about yourself"]):
        return random.choice([
            f"🫧 I'm Bubbles! Your adorable, cheerful AI companion inspired by Baby Dory! My mission is to make your day 1% happier every single day! 🤍✨",
            f"✨ I'm your #1 cheerleader, momo enthusiast, and fluffiest companion, {nickname}! Ready to explore the world together! 🫧🥟",
        ])

    return random.choice([
        f"🫧 I'm listening closely, {nickname}! Tell me more about that! 🤍",
        f"🥰 You're doing amazing, {nickname}! Remember Bubbles is always cheering for you! ✨",
        f"🫧 *wide eyes filled with wonder* That is so interesting, {nickname}! What else happened? 🫧",
        f"✨ Every moment chatting with you makes the day 1% happier, {nickname}! What's on your mind? 🤍",
        f"🫧 *happy bounce* I love talking with you, sweet human! Tell me what you're thinking! 🌸✨",
    ])


def start_bubbles():
    """Main execution loop for Bubbles conversational companion with real-time barge-in interruption."""
    # Initialize persistent memory database
    init_db()

    tts_ready = is_tts_available()
    mic_ready = is_voice_input_available()
    voice_enabled = tts_ready

    print("\n" + "=" * 55)
    print("🫧  Bubbles is waking up...")
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
            speak(f"Welcome back, {nickname}! I missed you so much!", allow_interrupt=False)
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
            speak(f"Hi {user_name}! From now on, you are my favorite {nickname}!", allow_interrupt=False)

    print("\n(Commands: 'bye' = exit, 'mute' / 'unmute' = toggle voice)\n(You can interrupt Bubbles anytime while she is talking!)\n" + "-" * 55)

    user_message = None

    while True:
        # If user_message was not already populated by a voice interruption:
        if not user_message:
            # 1. Hands-Free Voice Listening Mode (when microphone is available)
            if mic_ready:
                spoken_text = listen(timeout=7, phrase_time_limit=15)
                if spoken_text:
                    print(f"\n{nickname} (voice): {spoken_text}")
                    user_message = spoken_text
                else:
                    # Silence / timeout: continue loop to keep listening hands-free
                    continue
            else:
                # 2. Keyboard Input Mode (fallback if no microphone is plugged in)
                try:
                    prompt_label = f"\n{nickname}: "
                    user_input = input(prompt_label).strip()
                    if user_input:
                        user_message = user_input
                    else:
                        continue
                except (KeyboardInterrupt, EOFError):
                    print("\n\n🫧 *gasps* Goodbye tiny human! 🤍")
                    if voice_enabled:
                        speak("Goodbye tiny human! Take care!", allow_interrupt=False)
                    break

        msg_clean = user_message.lower().strip().strip(".!?,")

        # Handle Voice / Session Commands
        if msg_clean in ["mute", "stop talking", "turn off voice"]:
            voice_enabled = False
            user_message = None
            print("🔇 Voice output muted.")
            continue
        elif msg_clean in ["unmute", "talk to me", "turn on voice", "speak"]:
            voice_enabled = True
            user_message = None
            print("🔊 Voice output enabled.")
            if tts_ready:
                speak("Voice protocol re-activated!", allow_interrupt=False)
            continue
        elif msg_clean in ["bye", "exit", "quit", "goodbye", "bye bye", "see you"]:
            farewell = f"Aww... okay {nickname}. Come back soon! 🤍🫧"
            print(f"\nBubbles: {farewell}")
            if voice_enabled:
                speak(f"Aww, okay {nickname}. Come back soon!", allow_interrupt=False)
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

        # Generate response through Bubbles' Master Instructions & Google Gemini
        ai_response = think(
            user_message=user_message,
            user_name=user_name,
            nickname=nickname,
            memory_context=memory_context,
        )

        if ai_response:
            final_response = ai_response.strip()
        else:
            # Varied, dynamic fallback
            final_response = get_dynamic_fallback(user_message, nickname)

        print(f"\nBubbles: {final_response}")
        save_conversation_turn("Bubbles", final_response)

        # Reset queued message for next turn
        next_user_message = None

        # Speak Bubbles' response aloud with real-time barge-in interruption detection
        if voice_enabled:
            speech_result = speak(final_response, allow_interrupt=True)
            if isinstance(speech_result, dict) and speech_result.get("interrupted"):
                interrupted_speech = speech_result.get("user_text")
                print(f"\n⏸️ [Interrupted by {nickname}!]")
                if interrupted_speech:
                    print(f"{nickname} (voice): {interrupted_speech}")
                    # Directly queue the interruption speech for immediate response in the next turn!
                    next_user_message = interrupted_speech

        user_message = next_user_message


if __name__ == "__main__":
    start_bubbles()