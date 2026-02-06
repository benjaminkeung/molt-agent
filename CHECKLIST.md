# Pre-Commit Checklist ✓

Before pushing to GitHub, verify:

## 1. Sensitive Files Protected
- [ ] `.gitignore` includes `config.py`
- [ ] `.gitignore` includes `deploy.sh` and `download.sh`
- [ ] `.gitignore` includes `registration.json`
- [ ] `.gitignore` includes actual memory/personality files

## 2. Example Files Created
- [ ] `config.example.py` exists
- [ ] `deploy.example.sh` exists
- [ ] `download.example.sh` exists
- [ ] `registration.example.json` exists
- [ ] `personality.example.json` exists
- [ ] `memory.example.json` exists

## 3. No Secrets in Code
```bash
# Run these commands to check:
grep -r "moltbook_sk_" . --exclude-dir=.git --exclude-dir=tmp
grep -r "AIzaSy" . --exclude-dir=.git --exclude-dir=tmp
grep -r "192.168" . --exclude-dir=.git --exclude-dir=tmp
```
Should only find secrets in `.example` files!

## 4. Documentation Complete
- [ ] README.md exists
- [ ] LICENSE exists
- [ ] CONTRIBUTING.md exists
- [ ] All docs reference example files, not actual config

## 5. Test Before Push
```bash
# Verify gitignore works
git status

# Should NOT see:
# - config.py
# - deploy.sh
# - download.sh
# - registration.json
```

## 6. Ready to Push
```bash
git add .
git commit -m "Initial commit"
git push
```

## If You See Sensitive Files in `git status`:
**STOP!** They're not in `.gitignore`. Add them before committing!
