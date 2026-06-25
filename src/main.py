from moods import get_mood
from responses import RESPONSES
import random

print("🫧 Bubbles is waking up...")

mood = get_mood()

print(f"\nCurrent Mood: {mood}")

user_name = input("\nWhat's your name? ")

message = random.choice(RESPONSES[mood])

print(f"\n{message}")

print(f"\nHi {user_name}! 🫧")