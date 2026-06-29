TRIGGERS = {
    "momo": ["momo", "momos", "dumpling", "dumplings"],
    "sad": ["sad", "upset", "depressed", "crying"],
    "joke": ["joke", "funny", "laugh"],
    "fact": ["fact", "interesting", "tell me something"]
}

def check_triggers(user_message):
    user_message = user_message.lower()
    detected_triggers = []

    for trigger, keywords in TRIGGERS.items():
        for keyword in keywords:
            if keyword in user_message:
                detected_triggers.append(trigger)
                break

    return detected_triggers