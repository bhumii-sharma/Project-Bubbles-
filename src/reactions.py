import random
from jokes import get_random_joke
from facts import get_random_fact

REACTIONS = {
    "momo": [
        "🥟 MOMOS?! WHERE?!",
        "🥟 Human! Sharing is caring...",
        "🥟 My happiness just increased by 1000%!",
        "🥟 Did someone say momos? I'm listening.",
        "🥟 Emergency! We need momos immediately!"
    ],

    "sad": [
        "🤍 Come here, tiny human. I'm here.",
        "🤍 You don't have to carry everything alone.",
        "🤍 It's okay to have bad days.",
        "🤍 Sending you the world's biggest Baymax hug.",
        "🤍 We'll get through this together."
    ],

    "joke": [
        "😂 Joke incoming...",
        "😂 Activating comedy mode!",
        "😂 Okay, don't blame me if it's terrible."
    ],

    "fact": [
        "📚 Fun fact loading...",
        "📚 Oooo! I know a good one.",
        "📚 Random knowledge incoming!"
    ]
}


def get_reaction(trigger):

    if trigger == "joke":
        intros = [
            "😂 Okay, here's one!",
            "😂 Tiny human, prepare yourself...",
            "😂 I found a joke!"
        ]
        return f"{random.choice(intros)}\n{get_random_joke()}"

    if trigger == "fact":
        intros = [
            "📚 Oooo! Here's something interesting!",
            "📚 Random fact incoming!",
            "📚 Tiny human, did you know?"
        ]
        return f"{random.choice(intros)}\n{get_random_fact()}"

    return random.choice(REACTIONS.get(trigger, ["🫧 *confused bubble noises*"]))