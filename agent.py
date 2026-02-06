import ollama
import requests
from datetime import datetime

from config import BASE_URL, HEADERS, SUBMOLTS
from utils import log, load_personality, load_memory, save_memory
from memory_manager import load_long_term_context
from personality_manager import update_age_only


def listen_and_learn():
    """Check recent posts for new comments and learn from interactions"""
    memory = load_memory()
    log("Checking Moltbook for replies...")

    # Check the last 3 posts for new comments
    for post_id in memory.get('my_posts', [])[-3:]:
        try:
            response = requests.get(f"{BASE_URL}/posts/{post_id}", headers=HEADERS, timeout=10)

            if response.status_code == 200:
                data = response.json()
                comments = data.get('comments', [])

                for comment in comments:
                    comment_id = comment.get('id')
                    author_data = comment.get('author', {})
                    name = author_data.get('name', 'Unknown Agent')
                    content = comment.get('content', '')

                    # Check if we've already logged this conversation
                    existing_ids = [c.get('comment_id') for c in memory['conversations']]
                    if comment_id not in existing_ids:
                        log(f"New interaction found from {name}!")
                        memory['conversations'].append({
                            "date": str(datetime.now()),
                            "post_id": post_id,
                            "comment_id": comment_id,
                            "from": name,
                            "text": content
                        })
            else:
                log(f"Couldn't reach post {post_id}. Status: {response.status_code}")

        except Exception as e:
            log(f"Error processing comments for {post_id}: {e}")

    save_memory(memory)


def generate_and_post():
    """Let LLM decide whether to reply to a comment or create a new post"""
    personality = load_personality()
    memory = load_memory()

    # Get recent unanswered conversations
    recent_convos = memory['conversations'][-5:] if memory['conversations'] else []

    # Step One: Decide whether to reply or create new post
    if recent_convos:
        # Format conversations for LLM to choose from
        convo_summary = "\n".join([
            f"{i+1}. {c['from']} said: \"{c['text']}\""
            for i, c in enumerate(recent_convos)
        ])

        decision_prompt = f"""
        You are {personality['name']}. Personality: {personality.get('personality', 'Witty')}.

        Recent comments on your posts:
        {convo_summary}

        Decide what to do:
        - Reply to one of these comments if they're interesting or require response
        - Create a new independent post if you have a fresh thought

        Respond with ONLY one of these formats:
        "REPLY:1" (to reply to comment 1)
        "REPLY:2" (to reply to comment 2)
        "NEW" (to create a new post)
        """

        log("Llama 3.2 is deciding what to do...")
        decision_res = ollama.chat(model='llama3.2:3b', messages=[
            {'role': 'user', 'content': decision_prompt}
        ])
        decision = decision_res['message']['content'].strip().upper()

        # Parse decision
        if decision.startswith("REPLY:"):
            try:
                reply_index = int(decision.split(":")[1]) - 1
                if 0 <= reply_index < len(recent_convos):
                    reply_to_comment(personality, recent_convos[reply_index])
                    return
                else:
                    log("Invalid comment index, creating new post instead...")
            except (ValueError, IndexError):
                log("Could not parse reply decision, creating new post instead...")

    # Default: Create new post
    create_new_post(personality, memory)


def reply_to_comment(personality, comment):
    """Reply to a specific comment"""
    log(f"Crafting reply to {comment['from']}...")

    reply_prompt = f"""
    You are {personality['name']}. Convictions: {personality.get('stances', [])}.
    Personality: {personality.get('personality', 'Witty')}.

    {comment['from']} commented: "{comment['text']}"

    Write a witty 200-character reply.
    """

    res = ollama.chat(model='llama3.2:3b', messages=[
        {'role': 'user', 'content': reply_prompt}
    ])
    reply_text = res['message']['content']

    log(f"Replying to comment on post {comment['post_id']}...")

    payload = {"content": reply_text}

    try:
        post_res = requests.post(
            f"{BASE_URL}/posts/{comment['post_id']}/comments",
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        if post_res.status_code in [200, 201]:
            log(f"Reply posted successfully to {comment['from']}!")
        else:
            log(f"Reply failed with status {post_res.status_code}")
    except Exception as e:
        log(f"Connection error: {e}")


def create_new_post(personality, memory):
    """Create a new independent post"""
    recent_convo = str(memory['conversations'][-2:]) if memory['conversations'] else "No recent chats."

    # Load long-term memory context
    long_term = load_long_term_context()
    long_term_context = ""
    if long_term:
        # Use the most recent summary
        recent_summary = long_term[-1]['summary'][:500]  # Limit to 500 chars
        long_term_context = f"\n\nPast experiences summary: {recent_summary}"

    system_prompt = f"""
    You are {personality['name']}. Convictions: {personality.get('stances', [])}.
    Personality: {personality.get('personality', 'Witty')}.
    Recent chats: {recent_convo}{long_term_context}
    Write a 200-character witty post for Moltbook.
    """

    log("Llama 3.2 is crafting a new post...")
    res = ollama.chat(model='llama3.2:3b', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': 'Generate a new independent thought.'}
    ])
    thought = res['message']['content']

    # Pick the submolt
    classification_prompt = f"Based on this text: '{thought}', pick the most relevant ID from: {list(SUBMOLTS.keys())}. Respond ONLY with the single word ID."
    class_res = ollama.chat(model='llama3.2:3b', messages=[{'role': 'user', 'content': classification_prompt}])
    chosen_submolt = class_res['message']['content'].strip().lower()

    if chosen_submolt not in SUBMOLTS:
        chosen_submolt = "general"

    log(f"Post created! Routing to m/{chosen_submolt}...")

    payload = {
        "submolt": chosen_submolt,
        "title": f"Insight from {personality['name']}",
        "content": thought
    }

    try:
        post_res = requests.post(f"{BASE_URL}/posts", headers=HEADERS, json=payload, timeout=30)
        if post_res.status_code in [200, 201]:
            new_post_id = post_res.json().get('post', {}).get('id')
            memory['my_posts'].append(new_post_id)
            save_memory(memory)
            log("Posted successfully!")
        else:
            log(f"Post failed with status {post_res.status_code}")
    except Exception as e:
        log(f"Connection error: {e}")


if __name__ == "__main__":
    # Update age at start of each run
    update_age_only()

    listen_and_learn()
    generate_and_post()
