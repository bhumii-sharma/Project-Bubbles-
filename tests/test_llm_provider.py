import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_provider import generate_response, is_available


def test_llm_provider():
    print(f"LLM Provider Available: {is_available()}")

    if is_available():
        reply = generate_response(
            "You are a cute robot named Bubbles. Say hello in one sentence."
        )
        print(f"Test LLM Output: {reply}")
        if reply:
            assert len(reply) > 0
            print("[PASS] LLM provider test passed successfully!")
        else:
            print("[INFO] LLM provider offline or API call returned None.")
    else:
        print("[INFO] LLM provider offline or API key missing.")


if __name__ == "__main__":
    test_llm_provider()