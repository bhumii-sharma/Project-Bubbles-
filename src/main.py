from triggers import check_triggers
from reactions import get_reaction
from moods import get_mood
from responses import RESPONSES
import random

print("🫧 Bubbles is waking up...")

# Today's mood
mood = get_mood()
print(f"\nCurrent Mood: {mood}")

# Greeting
user_name = input("\nWhat's your name? ")
print(f"\nHi {user_name}! 🫧")

# Conversation
user_message = input("\nYou: ")

# Check for triggers
triggers = check_triggers(user_message)

# If Bubbles detects something important...
if triggers:
    for trigger in triggers:
        print(get_reaction(trigger))

# Otherwise, continue normal conversation
else:
    message = random.choice(RESPONSES[mood])
    print(message)