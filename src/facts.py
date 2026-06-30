import random

FACTS = [
    "Octopuses have three hearts.",
    "Bananas are berries.",
    "Honey never spoils.",
    "Wombats poop cubes.",
    "Sharks are older than trees.",
    "A group of flamingos is called a flamboyance."
]

def get_random_fact():
    return random.choice(FACTS)