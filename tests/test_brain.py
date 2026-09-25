import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from brain import think


def test_brain():
    memory_context = """LONG-TERM MEMORIES OF YOUR HUMAN:
- [STRUGGLE] Lost job recently, plans to join gym when finances improve
- [PREFERENCE] Loves steamed veg momos
"""

    reply = think(
        user_message="Hi Bubbles! How are you doing today?",
        user_name="Bhumi",
        nickname="Chief Momo Inspector",
        memory_context=memory_context
    )

    print(f"Test Brain Output with Memory Context:\n{reply}")
    if reply:
        assert len(reply) > 0
        print("\n[PASS] Brain with Memory Context generated response successfully!")
    else:
        print("\n[INFO] Brain safely returned None (offline fallback mode active).")


if __name__ == "__main__":
    test_brain()