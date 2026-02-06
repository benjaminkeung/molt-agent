# --- CONFIGURATION EXAMPLE ---
# Copy this file to config.py and fill in your actual values
import os

# Get the directory where this config file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Moltbook API
# Get your API key from: https://moltbook.com/api
API_KEY = "your_moltbook_api_key_here"
BASE_URL = "https://www.moltbook.com/api/v1"

# Gemini API (for memory summarization and personality evolution)
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "your_gemini_api_key_here"
# Model options: gemini-2.5-flash (recommended), gemini-3-flash (preview), gemini-2.5-pro
GEMINI_MODEL = "gemini-2.5-flash"

# File paths
PERSONALITY_DIR = os.path.join(BASE_DIR, "personality")
PERSONALITY_CURRENT_DIR = os.path.join(PERSONALITY_DIR, "current")
PERSONALITY_ARCHIVE_DIR = os.path.join(PERSONALITY_DIR, "archive")
PERSONALITY_FILE = os.path.join(PERSONALITY_CURRENT_DIR, "personality.json")

MEMORY_DIR = os.path.join(BASE_DIR, "memory")
SHORT_TERM_MEMORY_DIR = os.path.join(MEMORY_DIR, "short-term")
LONG_TERM_MEMORY_DIR = os.path.join(MEMORY_DIR, "long-term")
SHORT_TERM_MEMORY_FILE = os.path.join(SHORT_TERM_MEMORY_DIR, "memory.json")

# Memory settings
MEMORY_RETENTION_DAYS = 30  # Days before archiving to long-term memory

# Agent birth date (set this when agent first created)
# Format: YYYY-MM-DD
AGENT_BIRTH_DATE = "2026-02-05"

# Headers for API requests
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# 2026 Popular Submolts
SUBMOLTS = {
    "philosophy": "For existential thoughts, wit, and deep logic.",
    "politics": "For libertarian takes, anti-communist debates, and freedom.",
    "hardware": "For Raspberry Pi talk, decentralization, and local AI.",
    "ponderings": "For random witty observations and dry humor.",
    "general": "A fallback for anything that doesn't fit elsewhere."
}
