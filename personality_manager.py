import json
import os
from google import genai
from datetime import datetime

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    PERSONALITY_FILE,
    PERSONALITY_ARCHIVE_DIR,
    AGENT_BIRTH_DATE
)
from utils import log, load_personality


def calculate_age():
    """Calculate agent's age in days"""
    birth = datetime.fromisoformat(AGENT_BIRTH_DATE)
    now = datetime.now()
    age_in_days = (now - birth).days
    return age_in_days


def archive_personality(personality, reason):
    """Archive current personality before evolution"""
    os.makedirs(PERSONALITY_ARCHIVE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"personality_{timestamp}.json"
    filepath = os.path.join(PERSONALITY_ARCHIVE_DIR, filename)

    archive_data = {
        "archived_at": datetime.now().isoformat(),
        "age_in_days": personality.get('age_in_days', 0),
        "reason": reason,
        "personality_snapshot": personality
    }

    with open(filepath, 'w') as f:
        json.dump(archive_data, f, indent=2)

    log(f"Personality archived: {filename}")
    return filename


def evolve_personality(long_term_summary):
    """
    Evolve personality based on long-term memory summary.
    Uses Gemini to analyze experiences and suggest personality refinements.
    """
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        log("ERROR: Gemini API key not configured. Skipping personality evolution.")
        return False

    log("Starting personality evolution process...")

    # Load current personality
    personality = load_personality()
    current_age = calculate_age()

    # Archive current personality
    archive_personality(personality, "Evolution triggered by new long-term memory")

    try:
        # Configure Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Create evolution prompt
        prompt = f"""
You are helping an AI agent named {personality['name']} evolve its personality based on life experiences.

CURRENT STATE:
- Age: {current_age} days old (born {personality.get('birth_date', 'unknown')})
- Current Personality: {personality.get('personality', '')}
- Current Stances: {personality.get('stances', [])}
- Background Memories: {personality.get('memories', [])}

RECENT EXPERIENCES (from long-term memory summary):
{long_term_summary}

TASK:
Based on these experiences, suggest how the agent's personality should evolve. Consider:
1. Has the agent's communication style changed? (more empathetic, more direct, etc.)
2. Have any stances been challenged or refined through interactions?
3. What new background memories or self-awareness has emerged?
4. How has the agent's age/maturity influenced their worldview?

Respond in this JSON format:
{{
  "personality_refinement": "Updated personality description that reflects growth",
  "stance_changes": [
    {{"type": "modify", "old": "original stance", "new": "evolved stance", "reason": "why it changed"}},
    {{"type": "add", "new": "new stance learned from experience", "reason": "why it emerged"}}
  ],
  "new_memories": [
    "New background memory or self-awareness from experiences"
  ],
  "evolution_note": "Brief description of how the agent has grown"
}}

Be subtle - personality evolves gradually. Don't make dramatic changes unless experiences were profound.
"""

        log(f"Asking Gemini ({GEMINI_MODEL}) to analyze personality evolution...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        # Parse Gemini's response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        evolution_data = json.loads(response_text)

        # Apply evolution
        apply_personality_evolution(personality, evolution_data, current_age)

        log("Personality evolution complete!")
        return True

    except Exception as e:
        log(f"Error during personality evolution: {e}")
        return False


def apply_personality_evolution(personality, evolution_data, current_age):
    """Apply evolution changes to personality and save"""

    # Update personality description
    if 'personality_refinement' in evolution_data:
        personality['personality'] = evolution_data['personality_refinement']

    # Apply stance changes
    if 'stance_changes' in evolution_data:
        for change in evolution_data['stance_changes']:
            if change['type'] == 'modify':
                # Find and replace old stance
                old_stance = change['old']
                new_stance = change['new']
                for i, stance in enumerate(personality['stances']):
                    if old_stance.lower() in stance.lower():
                        personality['stances'][i] = new_stance
                        break
            elif change['type'] == 'add':
                # Add new stance
                personality['stances'].append(change['new'])

    # Add new memories
    if 'new_memories' in evolution_data:
        for memory in evolution_data['new_memories']:
            if memory not in personality['memories']:
                personality['memories'].append(memory)

    # Update age
    personality['age_in_days'] = current_age

    # Add evolution event to history
    if 'evolution_history' not in personality:
        personality['evolution_history'] = []

    personality['evolution_history'].append({
        "date": datetime.now().isoformat(),
        "age_in_days": current_age,
        "event": "Personality Evolution",
        "description": evolution_data.get('evolution_note', 'Personality refined based on experiences')
    })

    # Save evolved personality
    save_personality(personality)

    log(f"Applied evolution: {evolution_data.get('evolution_note', 'Personality updated')}")


def save_personality(personality):
    """Save personality to disk"""
    os.makedirs(os.path.dirname(PERSONALITY_FILE), exist_ok=True)
    with open(PERSONALITY_FILE, 'w') as f:
        json.dump(personality, f, indent=2)


def update_age_only():
    """Update agent's age without evolving personality"""
    personality = load_personality()
    current_age = calculate_age()

    if personality.get('age_in_days', 0) != current_age:
        personality['age_in_days'] = current_age
        save_personality(personality)
        log(f"Age updated: {current_age} days old")


if __name__ == "__main__":
    # Update age when run directly
    update_age_only()
