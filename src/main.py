from triggers import check_triggers
from reactions import get_reaction
from moods import get_mood
from responses import RESPONSES
import random

print("🫧 Bubbles is waking up...")

mood = get_mood()
print(f"\nCurrent Mood: {mood}")

user_name = input("\nWhat's your name? ")
print(f"\nHi {user_name}! 🫧")

while True:

    user_message = input(f"\n{user_name}: ")

    if user_message.lower() in ["bye", "exit", "quit"]:
        print("\n🫧 Aww... okay tiny human. Come back soon! 🤍")
        break

    triggers = check_triggers(user_message)

    if triggers:
        for trigger in triggers:
            print(f"\nBubbles: {get_reaction(trigger)}")
    else:
        message = random.choice(RESPONSES[mood])
        print(f"\nBubbles: {message}")