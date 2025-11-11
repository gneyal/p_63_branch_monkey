# Branch Monkey - Quick Start Guide

## Daily Usage

### Scenario 1: Before Starting New Work

**Visual Way:**
```bash
monkey          # Launch TUI
# Look at graph, see where you are
# Press 'n' to create checkpoint
# Type: "Before adding login feature"
```

**Command Line Way:**
```bash
monkey save "Before adding login feature"
```

### Scenario 2: Try Something Without Risk

**Visual Way:**
```bash
monkey          # Launch TUI
# Navigate to commit where you want to branch from
# Press 'e' for new experiment
# Name it: "try-new-approach"
# Work on your changes...
```

**Command Line Way:**
```bash
monkey try-it try-new-approach -d "Testing new architecture"
# Work on your changes...
monkey save "Implemented new approach"

# Like it?
monkey keep

# Don't like it?
git checkout main
monkey discard try-new-approach
```

### Scenario 3: See What Happened

**Visual Way:**
```bash
monkey          # Launch TUI
# Use ↑/↓ to browse commits
# See the vertical timeline
# Press Enter on any commit to go there
```

**Command Line Way:**
```bash
monkey history          # See recent changes
monkey search "bug"     # Find specific commits
monkey status           # See current state
```

### Scenario 4: Go Back in Time

**Visual Way:**
```bash
monkey          # Launch TUI
# Navigate to the commit you want
# Press Enter to jump there
# Now you're at that point in history!
```

**Command Line Way:**
```bash
monkey checkpoints      # List all save points
monkey restore a1b2c3d  # Go to that checkpoint
monkey undo             # Go back one step
```

## The Graph - Your Main View

When you run `monkey`, you see:

```
◉    [current] (main) Your latest work
│
●    Previous commit
│
●    Another commit
│
  ●  (experiment/feature) Branch splits here
  │
●    Earlier work
```

**What the symbols mean:**
- `◉` = You are here (HEAD)
- `●` = A commit (save point)
- `│` = Branch line (vertical timeline)
- Branches appear in different columns (horizontal)

## Common Workflows

### 1. Regular Development

```bash
# Start of day
monkey status

# Make changes...
# Save checkpoint
monkey save "Added user validation"

# More changes...
# Save again
monkey save "Fixed validation bug"

# End of day - see what you did
monkey history
```

### 2. Experimental Work

```bash
# Want to try something risky?
monkey try-it refactor-api -d "Trying to simplify the API"

# Work on it...
monkey save "Refactored endpoints"

# Like it?
monkey keep

# OR don't like it?
git checkout main
monkey discard refactor-api
# Your main code is untouched!
```

### 3. Finding Old Work

```bash
# Visual exploration
monkey
# Browse with arrows, see everything

# Or search
monkey search "login"
monkey search "Alice" -w author

# Jump to specific point
monkey checkpoints
monkey restore 7a3b9f2
```

### 4. Team Collaboration

```bash
# Before pulling others' changes
monkey save "My work before pull"

# Pull from team
git pull

# If things break
monkey undo  # Go back to your working state

# Fix conflicts, then
monkey save "Merged team changes"
```

## Keyboard Shortcuts in TUI

### Navigation
- `↑` / `k` - Up
- `↓` / `j` - Down
- `Tab` - Next tab
- `1` / `2` / `3` / `4` - Jump to tab

### Actions
- `Enter` - Go to commit
- `n` - New checkpoint
- `e` - New experiment
- `r` - Refresh
- `q` - Quit
- `?` - Help

## CLI Command Reference

### Checkpoints (Save Points)
```bash
monkey save "message"           # Create checkpoint
monkey quick                    # Quick temporary save
monkey undo                     # Go back one
monkey restore <sha>            # Go to specific point
monkey checkpoints              # List all
```

### Experiments (Branches)
```bash
monkey try-it <name>            # Start experiment
monkey experiments              # List all
monkey switch <name>            # Switch to experiment
monkey keep                     # Merge and keep
monkey discard <name>           # Delete experiment
```

### History & Info
```bash
monkey history                  # See recent commits
monkey search "query"           # Find commits
monkey status                   # Current state
monkey diff <sha>               # Show changes
```

### Visual Mode
```bash
monkey                          # Launch TUI
monkey tui                      # Same thing
```

## Tips & Tricks

### 1. Save Often
```bash
# Before any major change
monkey save "Before refactoring auth"
```

### 2. Use Experiments for Risky Changes
```bash
# Don't commit to main until you're sure
monkey try-it new-feature
# Play around safely
```

### 3. Quick Saves Before Pulls
```bash
# Always save before pulling
monkey quick
git pull
```

### 4. Search is Your Friend
```bash
# Can't remember when you fixed something?
monkey search "bug fix"
monkey search "yesterday" -w message
```

### 5. Visual Mode for Exploration
```bash
# When you need to understand the project history
monkey
# Browse visually, see the tree structure
```

## Integration with Git

Branch Monkey is just a friendly interface to Git. Everything it does is standard Git:

- **Checkpoints** = Git commits
- **Experiments** = Git branches (prefixed with `experiment/`)
- **Quick saves** = Git stash
- **Timeline** = Git log

You can still use regular Git commands. Branch Monkey just makes it easier!

## For Claude Code Users

Use Branch Monkey in your Claude workflow:

```python
from branch_monkey import BranchMonkey

monkey = BranchMonkey()

# Before Claude makes changes
if monkey.has_changes():
    monkey.save("Before Claude session")

# Let Claude work...

# After Claude's changes
monkey.save("After Claude refactoring")

# Easy to compare or revert if needed
```

## Next Steps

1. **Try it now**: `monkey` - Launch the TUI and explore
2. **Make a save point**: `monkey save "First checkpoint"`
3. **Create an experiment**: `monkey try-it test-feature`
4. **Browse history**: Use arrows in TUI to see your project timeline

## Need Help?

- In TUI: Press `?` for help
- CLI: `monkey --help`
- Specific command: `monkey save --help`

## Philosophy

Branch Monkey makes Git simple:
- **No fear** - You can always go back
- **Visual** - See what's happening
- **Simple** - Checkpoints and experiments, not commits and branches
- **Safe** - Hard to lose work

Just remember: **Save often, experiment freely!** 🐵
