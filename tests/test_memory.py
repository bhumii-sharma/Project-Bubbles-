import os
import sys
import tempfile

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from memory import (
    init_db,
    set_profile_value,
    get_profile_value,
    save_memory,
    get_recent_memories,
    save_conversation_turn,
    get_recent_conversation,
    format_memory_context,
)

def test_sqlite_memory():
    print("=" * 60)
    print("TESTING PERSISTENT SQLITE MEMORY SYSTEM")
    print("=" * 60)

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        test_db_path = tf.name

    try:
        # 1. Test init
        init_db(test_db_path)
        print("1. Database initialized.")

        # 2. Test profile storage
        set_profile_value("user_name", "Bhumi", db_path=test_db_path)
        set_profile_value("nickname", "Chief Momo Inspector", db_path=test_db_path)
        assert get_profile_value("user_name", db_path=test_db_path) == "Bhumi"
        assert get_profile_value("nickname", db_path=test_db_path) == "Chief Momo Inspector"
        print("2. Profile storage verified.")

        # 3. Test long-term memory
        save_memory("struggle", "Lost job recently, plans to join gym when finances improve", importance=5, db_path=test_db_path)
        save_memory("preference", "Loves steamed veg momos", importance=4, db_path=test_db_path)
        memories = get_recent_memories(limit=5, db_path=test_db_path)
        assert len(memories) == 2
        assert "Lost job" in memories[0]["content"] or "Lost job" in memories[1]["content"]
        print("3. Long-term memory saving/retrieval verified.")

        # 4. Test conversation history
        save_conversation_turn("Bhumi", "Hi Bubbles!", mood="Happy", db_path=test_db_path)
        save_conversation_turn("Bubbles", "Hi Bhumi! I'm happy to see you!", mood="Happy", db_path=test_db_path)
        chats = get_recent_conversation(limit=5, db_path=test_db_path)
        assert len(chats) == 2
        assert chats[0]["sender"] == "Bhumi"
        assert chats[1]["sender"] == "Bubbles"
        print("4. Conversation history verified.")

        # 5. Test context formatting
        context = format_memory_context(db_path=test_db_path)
        print("\nFormatted Context Output:\n" + "-" * 40 + "\n" + context + "\n" + "-" * 40)
        assert "LONG-TERM MEMORIES" in context
        assert "RECENT CONVERSATION HISTORY" in context
        print("\n[PASS] All SQLite memory tests passed successfully!")

    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)


if __name__ == "__main__":
    test_sqlite_memory()
