# pebble — Claude Instructions

## SESSION START — NON-NEGOTIABLE, BEFORE ANY OTHER ACTION

1. **Read `WORKLOG.md`** in this directory.
   - If it does not exist, create it using the template at the bottom of this file.
   - If it exists, check for any entries marked "Uncommitted." Handle those before writing new code.

2. **Commit the current working state** before making any changes:
   ```
   git add -A
   git commit -m "save state before session"
   ```
   Even if nothing feels ready. Uncommitted work gets overwritten and is gone forever.

3. **Write a WORKLOG entry before you stop** — committed or not. Other sessions depend on knowing what you left behind.

**Banned git commands — stop and ask Gabby first:**
- `git checkout -f` — permanently wipes uncommitted files
- `git reset --hard` — same, no undo
- `git push --force` — overwrites history

**WORKLOG entry template:**
```
## YYYY-MM-DD — [session name]
**Working on:**
**Files changed:**
**Committed:** YES — [hash] / NO
**Uncommitted:**
**Notes for next session:**
```

---

## Project
See brain file (if present in `brains/`) for full context before starting feature work.

## Deploy
Never push to `main` or deploy without asking Gabby first.

