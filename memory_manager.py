import json
import os
from google import genai
from datetime import datetime, timedelta

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SHORT_TERM_MEMORY_FILE,
    LONG_TERM_MEMORY_DIR,
    MEMORY_RETENTION_DAYS
)
from utils import log, load_memory, save_memory, load_personality
from personality_manager import evolve_personality


def archive_old_memories():
    """
    Check short-term memory for data older than MEMORY_RETENTION_DAYS.
    Summarize old data using Gemini and move to long-term memory.
    """
    log("Starting memory archival process...")

    memory = load_memory()
    personality = load_personality()

    cutoff_date = datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)

    # Separate old and recent data
    old_posts = []
    recent_posts = []
    old_conversations = []
    recent_conversations = []

    # Process posts (if they have timestamps in future, for now keep all recent)
    # Note: my_posts are just IDs, we'll keep them all for now
    recent_posts = memory.get('my_posts', [])

    # Process conversations by date
    for convo in memory.get('conversations', []):
        try:
            convo_date = datetime.fromisoformat(convo['date'].replace('Z', '+00:00'))
            if convo_date < cutoff_date:
                old_conversations.append(convo)
            else:
                recent_conversations.append(convo)
        except (ValueError, KeyError):
            # If date parsing fails, keep in recent
            recent_conversations.append(convo)

    if not old_conversations:
        log("No old memories to archive.")
        return

    log(f"Found {len(old_conversations)} old conversations to archive...")

    # Summarize using Gemini
    summary = summarize_with_gemini(personality, old_conversations)

    if summary:
        # Save summary to long-term memory
        save_long_term_summary(summary, old_conversations)

        # Update short-term memory (remove old data)
        memory['my_posts'] = recent_posts
        memory['conversations'] = recent_conversations
        save_memory(memory)

        log(f"Archived {len(old_conversations)} conversations to long-term memory.")

        # Evolve personality based on the new long-term memory
        log("Now evolving personality based on experiences...")
        evolve_personality(summary)
    else:
        log("Failed to generate summary. Old memories not archived.")


def summarize_with_gemini(personality, conversations):
    """Use Gemini to summarize old conversations"""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        log("ERROR: Gemini API key not configured. Please set GEMINI_API_KEY in config.py")
        return None

    try:
        # Configure Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Format conversations for summarization
        convo_text = "\n".join([
            f"- {c['from']} said: \"{c['text']}\" (on post {c.get('post_id', 'unknown')})"
            for c in conversations
        ])

        prompt = f"""
You are summarizing old interactions for {personality['name']}, an AI agent on Moltbook.

Personality: {personality.get('personality', 'Witty')}
Stances: {personality.get('stances', [])}

Here are the conversations from the past month:
{convo_text}

Please provide a concise summary covering:
1. Key interactions and who they were with
2. Main topics discussed
3. Any emerging patterns (allies, enemies, recurring themes)
4. Insights about the agent's social dynamics

Keep the summary under 500 words.
"""

        log(f"Asking Gemini ({GEMINI_MODEL}) to summarize old memories...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        return response.text

    except Exception as e:
        log(f"Error calling Gemini API: {e}")
        return None


def save_long_term_summary(summary, conversations):
    """Save summarized memory to long-term storage"""
    os.makedirs(LONG_TERM_MEMORY_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_{timestamp}.json"
    filepath = os.path.join(LONG_TERM_MEMORY_DIR, filename)

    archive_data = {
        "archived_at": datetime.now().isoformat(),
        "conversation_count": len(conversations),
        "date_range": {
            "oldest": min(c['date'] for c in conversations),
            "newest": max(c['date'] for c in conversations)
        },
        "summary": summary,
        "raw_conversations": conversations
    }

    with open(filepath, 'w') as f:
        json.dump(archive_data, f, indent=2)

    log(f"Long-term memory saved to: {filename}")


def load_long_term_context():
    """Load all long-term memory summaries for context"""
    if not os.path.exists(LONG_TERM_MEMORY_DIR):
        return []

    summaries = []
    for filename in sorted(os.listdir(LONG_TERM_MEMORY_DIR)):
        if filename.endswith('.json'):
            filepath = os.path.join(LONG_TERM_MEMORY_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    summaries.append({
                        "archived_at": data.get('archived_at'),
                        "summary": data.get('summary')
                    })
            except Exception as e:
                log(f"Error loading {filename}: {e}")

    return summaries


if __name__ == "__main__":
    # Run memory archival when executed directly
    archive_old_memories()
