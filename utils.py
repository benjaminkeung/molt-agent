import json
import os
from datetime import datetime
from config import PERSONALITY_FILE, SHORT_TERM_MEMORY_FILE


def log(msg):
    """Timestamped logging helper - generates [YYYY-MM-DD HH:MM:SS] format"""
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}")


def load_personality():
    """Load agent personality from disk"""
    try:
        with open(PERSONALITY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "name": "taibun_boo_boo",
            "personality": "Witty",
            "stances": [],
            "memories": []
        }


def load_memory():
    """Load agent short-term memory from disk, creating default if not found"""
    try:
        with open(SHORT_TERM_MEMORY_FILE, 'r') as f:
            data = json.load(f)
        # Safety Check: Ensure these keys always exist to prevent KeyErrors
        if 'my_posts' not in data:
            data['my_posts'] = []
        if 'conversations' not in data:
            data['conversations'] = []
        if 'allies' not in data:
            data['allies'] = []
        if 'enemies' not in data:
            data['enemies'] = []
        return data
    except FileNotFoundError:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SHORT_TERM_MEMORY_FILE), exist_ok=True)
        return {"my_posts": [], "conversations": [], "allies": [], "enemies": []}


def save_memory(data):
    """Persist agent short-term memory to disk"""
    os.makedirs(os.path.dirname(SHORT_TERM_MEMORY_FILE), exist_ok=True)
    with open(SHORT_TERM_MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)
