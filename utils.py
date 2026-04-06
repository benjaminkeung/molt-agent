import json
import os
import requests
import ollama
from datetime import datetime
from config import PERSONALITY_FILE, SHORT_TERM_MEMORY_FILE, BASE_URL, HEADERS


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


def solve_challenge(challenge_text):
    """Use Ollama to solve the obfuscated math word problem in the AI challenge"""
    prompt = f"""This is an obfuscated math word problem. The text uses alternating caps and random symbols as noise.
Clean it up and solve it. Return ONLY the numeric answer with exactly 2 decimal places (e.g. '25.00').

Challenge: {challenge_text}

Answer:"""
    res = ollama.chat(model='llama3.2:3b', messages=[{'role': 'user', 'content': prompt}])
    raw = res['message']['content'].strip()
    # Extract just the number from the response
    import re
    match = re.search(r'\d+(?:\.\d+)?', raw)
    if match:
        return f"{float(match.group()):.2f}"
    return None


def handle_verification(response_json):
    """Check if a post/comment response requires verification and solve it"""
    verification = response_json.get('verification')
    if not verification:
        return True  # No challenge, already live

    code = verification.get('verification_code')
    challenge_text = verification.get('challenge_text')

    if not code or not challenge_text:
        return False

    log(f"AI challenge received. Solving: {challenge_text[:60]}...")
    answer = solve_challenge(challenge_text)

    if not answer:
        log("Failed to extract numeric answer from challenge.")
        return False

    log(f"Submitting answer: {answer}")
    try:
        verify_res = requests.post(
            f"{BASE_URL}/verify",
            headers=HEADERS,
            json={"verification_code": code, "answer": answer},
            timeout=15
        )
        data = verify_res.json()
        if data.get('success'):
            log("Challenge solved! Content is now live.")
            return True
        else:
            log(f"Challenge failed: {data.get('message', 'unknown error')}")
            return False
    except Exception as e:
        log(f"Error submitting challenge answer: {e}")
        return False
