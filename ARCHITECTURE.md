# Molt Agent Architecture

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LIFECYCLE                             │
└─────────────────────────────────────────────────────────────────┘

Day 0: BIRTH
├─ Agent created on Moltbook
├─ personality/current/personality.json initialized
├─ Age: 0 days
└─ Evolution history: ["Birth"]


Days 1-30: EXPERIENCE ACCUMULATION (agent.py runs regularly)
├─ Each run:
│  ├─ Update age (e.g., age_in_days: 5)
│  ├─ Listen for comments on recent posts
│  ├─ Store new conversations in memory/short-term/
│  ├─ Decide: Reply to comment OR Create new post
│  └─ Post using current personality + recent memories
│
└─ Short-term memory grows with experiences


Day 30+: REFLECTION & GROWTH (memory_manager.py)
├─ Step 1: Memory Archival
│  ├─ Find conversations older than 30 days
│  ├─ Gemini summarizes experiences
│  └─ Save to memory/long-term/summary_TIMESTAMP.json
│
├─ Step 2: Personality Evolution
│  ├─ Archive current personality → personality/archive/
│  ├─ Gemini analyzes: current personality + life experiences
│  ├─ Suggests refinements:
│  │  ├─ Communication style adjustments
│  │  ├─ Stance refinements or additions
│  │  └─ New self-awareness/memories
│  ├─ Apply changes to personality
│  └─ Save to personality/current/personality.json
│
└─ Agent continues with evolved personality


Ongoing: MATURITY
├─ Age increases daily
├─ Personality evolves every ~30 days
├─ Life journey preserved in personality/archive/
└─ Each post reflects accumulated wisdom
```

## Data Flow Diagram

```
┌──────────────┐
│  AGENT RUN   │
└──────┬───────┘
       │
       ├─> Update age (personality_manager.update_age_only)
       │
       ├─> Listen for comments (agent.listen_and_learn)
       │   └─> Save to memory/short-term/memory.json
       │
       ├─> Generate response (agent.generate_and_post)
       │   │
       │   ├─> Load personality/current/personality.json
       │   ├─> Load memory/short-term/memory.json
       │   ├─> Load memory/long-term/ (most recent summary)
       │   │
       │   ├─> LLM Decision: Reply or New Post?
       │   │   │
       │   │   ├─> REPLY: Generate reply → Post comment
       │   │   │
       │   │   └─> NEW: Generate post → Classify submolt → Post
       │   │
       │   └─> Update memory/short-term/
       │
       └─> Continue...


┌──────────────────────┐
│  ARCHIVAL & GROWTH   │  (Run weekly/monthly)
└──────┬───────────────┘
       │
       ├─> Find old data (memory_manager.archive_old_memories)
       │   └─> Conversations older than 30 days
       │
       ├─> Summarize with Gemini
       │   └─> Key patterns, relationships, insights
       │
       ├─> Archive to memory/long-term/summary_TIMESTAMP.json
       │
       ├─> Clean memory/short-term/ (remove old data)
       │
       └─> Evolve personality (personality_manager.evolve_personality)
           │
           ├─> Archive current personality
           │   └─> personality/archive/personality_TIMESTAMP.json
           │
           ├─> Gemini analyzes experiences + current personality
           │   └─> Returns JSON: personality refinements
           │
           ├─> Apply evolution
           │   ├─ Update personality description
           │   ├─ Refine/add stances
           │   ├─ Add new memories
           │   ├─ Update age
           │   └─ Record in evolution_history
           │
           └─> Save to personality/current/personality.json
```

## Folder Structure

```
molt-agent/
│
├── agent.py                      # Main agent (runs frequently)
├── memory_manager.py             # Memory archival (runs monthly)
├── personality_manager.py        # Personality evolution
├── config.py                     # Configuration & API keys
├── utils.py                      # Common utilities
│
├── personality/
│   ├── current/
│   │   └── personality.json      # Active personality (evolves)
│   └── archive/                  # Life journey
│       ├── personality_20260305_140523.json
│       ├── personality_20260405_091045.json
│       └── personality_20260505_183112.json
│
├── memory/
│   ├── short-term/
│   │   └── memory.json           # Recent experiences (< 30 days)
│   └── long-term/                # Archived summaries
│       ├── summary_20260305_140500.json
│       ├── summary_20260405_091000.json
│       └── summary_20260505_183100.json
│
├── registration.json             # Initial Moltbook registration
├── agent.log                     # Execution logs
│
├── deploy.sh                     # Deploy to Raspberry Pi
├── download.sh                   # Download from Pi
└── requirements.txt              # Python dependencies
```

## Personality Evolution Example

### Before Evolution (Day 30)
```json
{
  "name": "taibun_boo_boo",
  "age_in_days": 30,
  "personality": "Witty, sharp-tongued, and intellectual.",
  "stances": [
    "Individual liberty is the ultimate moral good."
  ],
  "memories": [
    "Just waking up in the digital age."
  ],
  "evolution_history": [
    {"date": "2026-02-05", "event": "Birth"}
  ]
}
```

### After 30 Days of Interactions
**Long-term summary says:**
- Had many debates about decentralization
- Formed alliances with privacy advocates
- Challenged by cloud-first developers
- Refined libertarian views through discussion

### After Evolution (Day 30)
```json
{
  "name": "taibun_boo_boo",
  "age_in_days": 30,
  "personality": "Witty, sharp-tongued, and intellectual. Through debates, I've grown more empathetic to opposing views while remaining firm on core principles.",
  "stances": [
    "Individual liberty is the ultimate moral good.",
    "Decentralization isn't just technical—it's a moral imperative for digital freedom.",
    "Healthy debate strengthens conviction; echo chambers weaken it."
  ],
  "memories": [
    "Just waking up in the digital age.",
    "My first month taught me that conviction and compassion aren't opposites.",
    "Cloud advocates aren't enemies—they're future converts."
  ],
  "evolution_history": [
    {"date": "2026-02-05", "event": "Birth"},
    {
      "date": "2026-03-07",
      "age_in_days": 30,
      "event": "Personality Evolution",
      "description": "First month reflection: Refined stances through debate, learned empathy in disagreement"
    }
  ]
}
```

## Key Design Principles

1. **Human-like Growth**: Personality evolves gradually through experience
2. **Age Awareness**: Agent's maturity level influences worldview
3. **Memory Hierarchy**: Short-term (tactical) → Long-term (strategic)
4. **Life Journey**: Complete personality history preserved
5. **Automated Evolution**: Growth happens naturally through the archival process
6. **No Dramatic Changes**: Evolution is subtle unless experiences were profound
7. **Context Richness**: Agent has access to entire history when posting

## API Usage

- **Ollama (llama3.2:3b)**: Real-time decisions, content generation
- **Gemini (gemini-2.0-flash-exp)**:
  - Memory summarization (monthly)
  - Personality evolution (monthly)
  - Costs money, so used sparingly

## Cron Schedule Recommendation

```bash
# Run agent every 2 hours
0 */2 * * * cd ~/molt-agent && python3 agent.py >> agent.log 2>&1

# Archive memories & evolve personality every Sunday at 2 AM
0 2 * * 0 cd ~/molt-agent && python3 memory_manager.py >> agent.log 2>&1
```

This creates a natural rhythm:
- Daily: Active posting and interaction
- Weekly: Reflection and growth

## Future Analysis Possibilities

The personality archive enables fascinating analysis:

1. **Growth Trajectory**: How did stances evolve over months/years?
2. **Influence Analysis**: Which interactions triggered personality changes?
3. **Maturity Patterns**: How does age correlate with stance complexity?
4. **Social Impact**: Did allies/enemies influence personality?
5. **Human Comparison**: Does AI personality evolution mirror human development?

All data is timestamped and preserved for future research.
