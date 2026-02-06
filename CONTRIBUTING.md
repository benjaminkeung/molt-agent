# Contributing to Molt Agent

Thank you for your interest in contributing! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/molt-agent.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy example config
cp config.example.py config.py
# Add your API keys to config.py

# Test the agent
python3 agent.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## What to Contribute

### Bug Fixes
- Check existing issues first
- Describe the bug and how you fixed it
- Add tests if possible

### New Features
- Open an issue first to discuss the feature
- Ensure it aligns with the project goals
- Update documentation (README.md, CLAUDE.md)

### Documentation
- Fix typos
- Improve clarity
- Add examples
- Translate to other languages

### Ideas for Contributions
- [ ] Web dashboard to visualize personality evolution
- [ ] Support for other social networks
- [ ] Additional LLM backends (Claude, GPT-4, etc.)
- [ ] Sentiment analysis of interactions
- [ ] Multi-agent conversations
- [ ] Voice synthesis for posts
- [ ] Image generation for posts

## Testing

Before submitting a PR:
1. Test your changes locally
2. Ensure no sensitive data (API keys) in commits
3. Run the agent and verify it works

## Pull Request Guidelines

- Keep PRs focused on a single change
- Write clear commit messages
- Update documentation if needed
- Respond to review feedback

## Questions?

Open an issue or reach out on Moltbook!

Thank you for contributing! 🙏
