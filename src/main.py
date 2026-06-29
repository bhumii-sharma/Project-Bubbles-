from triggers import check_triggers
from moods import get_mood
from responses import RESPONSES
import random

print("🫧 Bubbles is waking up...")

mood = get_mood()
print(f"\nCurrent Mood: {mood}")

user_name = input("\nWhat's your name? ")
print(f"\nHi {user_name}! 🫧")

user_message = input("\nYou: ")

triggers = check_triggers(user_message)

# Temporary trigger reactions
if "momo" in triggers:
    print("🥟 MOMOS DETECTED!! GIVE ME MOMOS!!")

if "sad" in triggers:
    print("🤍 Protective mode activated. Come here, tiny human.")

if "joke" in triggers:
    print("😂 Joke request detected!")

if "fact" in triggers:
    print("📚 Interesting fact request detected!")

message = random.choice(RESPONSES[mood])
print(f"\n{message}")