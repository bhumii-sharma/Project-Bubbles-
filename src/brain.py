import os
import sys

# Configure UTF-8 encoding for Windows terminal output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from instructions import build_system_prompt
    from llm_provider import generate_response, is_available
except ImportError:
    from src.instructions import build_system_prompt
    from src.llm_provider import generate_response, is_available


def think(user_message, user_name="Human", nickname=None, memory_context=""):
    """
    Directs the conversation through Bubbles' Master Instructions & OpenAI.
    Passes user identity, memories, and message to the LLM.
    """
    system_prompt = build_system_prompt(
        user_name=user_name,
        nickname=nickname,
        memory_context=memory_context
    )
    return generate_response(user_message, system_prompt=system_prompt)