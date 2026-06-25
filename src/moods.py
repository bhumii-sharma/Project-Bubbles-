import random

MOODS = [
    "Happy",
    "Curious",
    "Excited",
    "Protective",
    "Chaotic"
]

def get_mood():
    return random.choice(MOODS)