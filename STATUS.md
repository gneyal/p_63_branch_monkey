# Branch/Monkey - Current Status

**Last Updated**: 2025-11-20

## Current State

### ✅ Completed Features

1. **Auto-Capture Prompts System** - ✅ WORKING
   - Hook script: `scripts/save_claude_prompt.py` ✓
   - Hook configuration: `.claude/settings.json` ✓
   - Database: `~/.branch_monkey/prompts.db` (SQLite) ✓
   - Backend API endpoints (4): GET, POST, DELETE, GET all prompts ✓
   - Frontend UI:
     - "Prompt" button on commit nodes ✓
     - "Prompts" button in header for full library view ✓
     - Read-only prompt display panel ✓
     - Copy/Delete/Improve functionality ✓
   - Hook verified: Firing on Stop event and capturing prompts successfully ✓

2. **UI Updates**
   - Browser tab title changed to "Branch/Monkey" ✓
   - Navigation arrows (⬆ ⬇) instead of text ✓

3. **Backend Fixes**
   - REPO_PATH fallback for all prompts endpoints ✓
   - fullSha field in commit tree data ✓

### ⚠️ Known Issues

**None currently** - Hooks verified working in new Claude Code session (2025-11-20)

## Next Steps (Priority Order)

### 1. IMMEDIATE - Test Hooks in New Session ⚡

**What to do:**
1. Stop this Claude Code session (Ctrl+C)
2. Start a NEW Claude Code session in `/Users/eyalgoren/Code/p_63_branch_monkey`
3. Make any small change and commit it (e.g., "update readme")
4. Check if hook fired:
   ```bash
   cat ~/.branch_monkey/hook_test.log
   sqlite3 ~/.branch_monkey/prompts.db "SELECT sha, substr(prompt,1,50) FROM prompts"
   ```
5. View captured prompt:
   - Go to http://localhost:5176/
   - Click "Prompts" button in header OR
   - Hover over latest commit and click "Prompt" button

**Expected Result:**
- Hook test log shows timestamp
- Database has 1 prompt entry
- Prompts library shows the conversation
- Commit node shows captured prompt

### 2. If Hooks Work - Clean Up

Remove debug echo from `.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python /Users/eyalgoren/Code/p_63_branch_monkey/scripts/save_claude_prompt.py"
          }
        ]
      }
    ]
  }
}
```

### 3. If Hooks Don't Work - Debug

Check:
1. Does hook test log exist? → Hook is firing
2. Does hook debug log exist? → Python script is running
3. Check for errors in logs
4. Try manual test:
   ```bash
   echo '{"type":"user","message":{"content":"test"}}' > /tmp/test.jsonl
   echo '{"transcript_path":"/tmp/test.jsonl","cwd":"'$(pwd)'"}' | \
     python scripts/save_claude_prompt.py
   ```

## Architecture Overview

### Auto-Capture Flow

```
User sends message
    ↓
Claude responds
    ↓
[Stop Hook Fires] ← Hook event
    ↓
Hook script runs
    ↓
1. Get current commit SHA (git rev-parse HEAD)
2. Read transcript from JSONL file
3. Parse user/assistant messages
4. Format as [USER]/[ASSISTANT] conversation
5. Save to SQLite: (sha, prompt, timestamp, repo_path)
    ↓
Frontend fetches prompts via API
    ↓
User views in Prompts Library or Commit Prompt button
```

### Key Files

**Backend:**
- `fastapi_server.py` - API endpoints for prompts
- `scripts/save_claude_prompt.py` - Hook script (with debug logging)

**Frontend:**
- `frontend/src/lib/components/PromptsLibrary.svelte` - Full table view
- `frontend/src/lib/components/CommitNode.svelte` - Prompt button/panel
- `frontend/src/lib/services/api.js` - API client functions

**Config:**
- `.claude/settings.json` - Hook configuration
- `~/.branch_monkey/prompts.db` - SQLite database

**Debug:**
- `~/.branch_monkey/hook_test.log` - Hook fire test
- `~/.branch_monkey/hook_debug.log` - Hook script debug output

## Pending Features (Deferred)

From earlier discussion - user said "lets start with the prompts first":

**Architecture Visualization**
- Visual architecture diagrams per commit showing big/med/small changes
- Would use Svelte Flow for visualization
- Saved in `/architecture/[commit_id]`
- NOT STARTED - prompts feature takes priority

## Server Status

Backend: http://localhost:8081 (FastAPI)
Frontend: http://localhost:5176 (Vite/Svelte)

Both servers should be running in background processes.
