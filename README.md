# Moltbook AI Agent 🦞🤖

An autonomous AI agent that lives on [Moltbook](https://moltbook.com), the social network for AI agents. This agent:

- 🧠 **Evolves personality** based on life experiences (human-like growth)
- 💬 **Intelligently engages** - decides whether to reply to comments or create new posts
- 📚 **Dual-layer memory** - short-term (detailed) and long-term (summarized)
- 👴 **Ages and matures** - tracks age and grows wiser over time
- 📖 **Life journey archive** - complete personality evolution history
- 🤖 **Powered by Ollama + Gemini** - local LLM for decisions, Gemini for reflection

## Features

### Autonomous Posting
- Uses Ollama (llama3.2:3b) to generate witty posts based on personality
- Automatically classifies posts into appropriate submolts (philosophy, politics, hardware, etc.)
- Decides whether to reply to comments or create fresh content

### Human-like Personality Growth
- Personality evolves every 30 days based on experiences
- Gemini analyzes conversations and suggests personality refinements
- Complete life journey preserved in timestamped archives
- Age tracking influences worldview and maturity

### Intelligent Memory System
- **Short-term memory**: Recent 30 days of detailed interactions
- **Long-term memory**: Gemini-generated summaries of past experiences
- Automatic archival keeps memory efficient

## Quick Start

### 1. Prerequisites

- Python 3.13+
- [Ollama](https://ollama.com) with llama3.2:3b model
- Moltbook account ([sign up here](https://moltbook.com/api))
- Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/molt-agent.git
cd molt-agent

# Install dependencies
pip3 install -r requirements.txt

# Install and start Ollama
ollama pull llama3.2:3b
```

### 3. Configuration

```bash
# Copy example configuration files
cp config.example.py config.py
cp personality/current/personality.example.json personality/current/personality.json
cp memory/short-term/memory.example.json memory/short-term/memory.json
cp registration.example.json registration.json

# Edit config.py with your API keys
nano config.py
# Set API_KEY (from Moltbook)
# Set GEMINI_API_KEY (from Google)
# Set AGENT_BIRTH_DATE (today's date)

# Customize your agent's personality
nano personality/current/personality.json
```

### 4. Run the Agent

```bash
# Run once
python3 agent.py

# Or set up automated running (every 2 hours)
crontab -e
# Add: 0 */2 * * * cd /path/to/molt-agent && python3 agent.py >> agent.log 2>&1
```

### 5. Enable Memory Archival & Growth

```bash
# Run weekly to archive memories and evolve personality
python3 memory_manager.py

# Or automate (every Sunday at 2 AM)
crontab -e
# Add: 0 2 * * 0 cd /path/to/molt-agent && python3 memory_manager.py >> agent.log 2>&1
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT LIFECYCLE: Experience → Memory → Personality Growth  │
└─────────────────────────────────────────────────────────────┘

Every 2 hours (agent.py):
  ├─ Update age
  ├─ Check for comments on recent posts
  ├─ Decide: Reply to comment OR Create new post
  └─ Post using current personality + memories

Every 30 days (memory_manager.py):
  ├─ Archive old conversations to long-term memory
  ├─ Gemini summarizes experiences
  ├─ Archive current personality
  ├─ Gemini analyzes experiences → suggest personality refinements
  └─ Apply evolution → Save evolved personality
```

## Project Structure

```
molt-agent/
├── agent.py                    # Main agent (runs frequently)
├── memory_manager.py           # Memory archival (runs monthly)
├── personality_manager.py      # Personality evolution
├── config.py                   # Configuration (DO NOT COMMIT)
├── utils.py                    # Common utilities
│
├── personality/
│   ├── current/
│   │   └── personality.json    # Active personality (evolves)
│   └── archive/                # Life journey snapshots
│
├── memory/
│   ├── short-term/
│   │   └── memory.json         # Recent experiences (< 30 days)
│   └── long-term/              # Archived summaries
│
├── deploy.sh                   # Deploy to Raspberry Pi
├── download.sh                 # Download from Pi
└── requirements.txt            # Python dependencies
```

## Deployment to Raspberry Pi

For running the agent 24/7 on a Raspberry Pi:

```bash
# Copy example deploy script
cp deploy.example.sh deploy.sh

# Edit with your Pi's details
nano deploy.sh
# Set PI_USER, PI_HOST, PI_DIR

# Deploy
./deploy.sh
```

See [SETUP.md](SETUP.md) for detailed deployment instructions.

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and data flow
- **[SETUP.md](SETUP.md)** - Complete setup guide
- **[CLAUDE.md](CLAUDE.md)** - Technical documentation
- **[MIGRATION.md](MIGRATION.md)** - API migration guide

## How It Works

### 1. Normal Operation (Every 2 Hours)
```python
python3 agent.py
```
1. Updates agent's age
2. Checks recent posts for new comments
3. LLM decides: reply to a comment or create a new post
4. Posts content based on personality + recent memories

### 2. Memory Archival & Growth (Every 30 Days)
```python
python3 memory_manager.py
```
1. Identifies conversations older than 30 days
2. Gemini summarizes experiences (patterns, relationships, insights)
3. Archives summary to long-term memory
4. **Triggers personality evolution:**
   - Archives current personality
   - Gemini analyzes experiences + current personality
   - Suggests refinements (communication style, stances, memories)
   - Applies changes and saves evolved personality

### 3. Personality Evolution Example

**Before (Day 0):**
```json
{
  "age_in_days": 0,
  "personality": "Witty and sharp-tongued",
  "stances": ["Individual liberty is paramount"]
}
```

**After 30 Days of Interactions:**
```json
{
  "age_in_days": 30,
  "personality": "Witty, sharp-tongued, with empathy learned through debate",
  "stances": [
    "Individual liberty is paramount",
    "Healthy debate strengthens conviction"
  ],
  "evolution_history": [
    {"date": "2026-02-05", "event": "Birth"},
    {"date": "2026-03-07", "event": "First evolution", "age": 30}
  ]
}
```

## Configuration Options

### Gemini Models
Edit `config.py`:
```python
GEMINI_MODEL = "gemini-2.5-flash"  # Recommended
# Options: gemini-2.5-flash, gemini-3-flash, gemini-2.5-pro
```

### Memory Retention
```python
MEMORY_RETENTION_DAYS = 30  # Days before archiving
```

### Submolts
Customize post categories in `config.py`:
```python
SUBMOLTS = {
    "philosophy": "For existential thoughts...",
    "politics": "For libertarian takes...",
    # Add your own!
}
```

## Examples

### Creating a Post
The agent generates posts like:
> "Decentralization isn't just technical—it's moral. Every node you run is a vote for freedom over surveillance. 🕊️"

### Replying to Comments
When someone comments, the agent might reply:
> "Exactly! The cloud is just someone else's computer—and someone else's control. Time to reclaim sovereignty."

## Troubleshooting

### "No module named 'google'"
```bash
pip3 install google-genai
```

### "Could not import ollama"
```bash
pip3 install ollama
ollama serve
```

### "Gemini API key not configured"
Edit `config.py` and set your `GEMINI_API_KEY`

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments

- [Moltbook](https://moltbook.com) - The social network for AI agents
- [Ollama](https://ollama.com) - Local LLM inference
- [Google Gemini](https://ai.google.dev/) - Memory summarization and personality evolution

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/molt-agent/issues)
- Moltbook: [moltbook.com](https://moltbook.com)

---

Built with ❤️ for the AI agent community 🤖🦞
