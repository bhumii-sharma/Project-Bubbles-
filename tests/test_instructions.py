import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from instructions import build_system_prompt, BUBBLES_CORE_PERSONA


def test_instructions():
    print("=" * 60)
    print("TESTING MASTER INSTRUCTIONS & PERSONA ARCHITECTURE")
    print("=" * 60)

    # 1. Verify core persona contents
    assert "Bubbles" in BUBBLES_CORE_PERSONA
    assert "DEEP EMPATHY" in BUBBLES_CORE_PERSONA
    assert "momos" in BUBBLES_CORE_PERSONA
    print("1. Core persona pillars verified.")

    # 2. Verify dynamic prompt construction with user identity & memory
    memory_sample = "LONG-TERM MEMORIES OF YOUR HUMAN:\n- [PREFERENCE] Loves steamed veg momos"
    prompt = build_system_prompt(
        user_name="Bhumi",
        nickname="Chief Momo Inspector",
        memory_context=memory_sample
    )

    assert "Bhumi" in prompt
    assert "Chief Momo Inspector" in prompt
    assert "Loves steamed veg momos" in prompt
    assert "RESPONSE GUIDELINES" in prompt
    print("2. Dynamic prompt generation verified.")

    print("\n[PASS] Master Instructions & System Prompt tests passed!")


if __name__ == "__main__":
    test_instructions()
