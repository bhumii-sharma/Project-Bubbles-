import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from triggers import check_triggers

message = "I'm sad. Tell me a joke. I ate momos."

print(check_triggers(message))