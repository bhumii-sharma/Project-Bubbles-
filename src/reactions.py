import random

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
    """Return a random reaction for a trigger."""
    if trigger in REACTIONS:
        return random.choice(REACTIONS[trigger])

    return "🫧 *confused bubble noises*"