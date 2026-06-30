from src.llm_provider import generate_response

reply = generate_response(
    "You are a cute robot named Bubbles. Say hello in one sentence."
)

print(reply)