# 🐵 Branch Monkey

**Git for humans - visual, safe, and beginner-friendly**

Branch Monkey makes Git accessible to everyone, from complete beginners to senior developers who want a faster workflow. No more cryptic commands, lost work, or fear of experimenting.

## 🎯 Why Branch Monkey?

Most people struggle with Git because:
- **It's complex**: Branches, commits, HEAD, detached states...
- **It's scary**: One wrong command and your work is gone
- **It's not visual**: Hard to see what's happening

Branch Monkey solves this by:
- ✅ **Simple metaphors**: Checkpoints (not commits), Experiments (not branches)
- ✅ **Always safe**: Can't lose work, easy undo
- ✅ **Visual**: Interactive TUI shows exactly what's happening
- ✅ **Both CLI and TUI**: Use commands OR visual interface

## 🚀 Quick Start

### Installation

```bash
# Install with pip
pip install branch-monkey

# Or install from source
git clone https://github.com/yourusername/branch-monkey
cd branch-monkey
pip install -e .
```

### First Steps

```bash
# Launch interactive interface (recommended for beginners)
monkey

# Or use commands directly
monkey save "My first checkpoint"
monkey try new-feature
monkey history
```

## 📖 Core Concepts

### 1. Checkpoints - Save Points

Think of checkpoints like save points in a video game. You can always go back.

```bash
# Save your work
monkey save "Before trying refactor"

# Made a mistake? Go back
monkey undo

# Or restore to any checkpoint
monkey restore a1b2c3d
```

**In Python/Claude Code:**
```python
from branch_monkey import BranchMonkey

monkey = BranchMonkey()
monkey.save("Before trying refactor")
monkey.undo()
```

### 2. Experiments - Safe Places to Try Things

Experiments are safe sandboxes where you can try new things without affecting your main work.

```bash
# Start an experiment
monkey try refactor -d "Trying new architecture"

# Work on it...
monkey save "Refactored auth system"

# Like it? Keep it
monkey keep

# Don't like it? Discard it
monkey discard
```

**In Python/Claude Code:**
```python
monkey.try_something("refactor", "Trying new architecture")
monkey.save("Refactored auth system")
monkey.keep_experiment()
```

### 3. Timeline - See What Happened

```bash
# See recent history
monkey history

# Search for something
monkey search "bug fix"

# See what changed
monkey diff a1b2c3d
```

## 🎨 Interactive TUI

The Terminal User Interface (TUI) provides a visual, interactive experience:

```bash
monkey  # Launch TUI
```

**Features:**
- 📜 **Timeline**: Visual history of all changes
- 💾 **Checkpoints**: Manage save points
- 🔬 **Experiments**: Create, switch, merge experiments
- ⌨️  **Keyboard shortcuts**: Navigate with arrow keys, enter, etc.

**Navigation:**
- `Tab`: Switch between sections
- `↑/↓` or `j/k`: Navigate lists
- `Enter`: Select/View details
- `n`: New checkpoint/experiment
- `r`: Restore/Refresh
- `q`: Quit
- `?`: Help

## 💻 Command Line Interface

### Checkpoints

```bash
# Create checkpoint
monkey save "Added login feature"

# Quick save (temporary)
monkey quick

# List checkpoints
monkey checkpoints

# Restore to checkpoint
monkey restore a1b2c3d

# Undo to previous
monkey undo
```

### Experiments

```bash
# Create experiment
monkey try new-ui -d "Redesigning dashboard"

# Switch between experiments
monkey switch new-ui
monkey switch main

# List experiments
monkey experiments

# Keep experiment (merge)
monkey keep

# Discard experiment
monkey discard new-ui
```

### History & Search

```bash
# View history
monkey history -n 20

# Search commits
monkey search "bug fix"
monkey search "Alice" -w author

# Show diff
monkey diff a1b2c3d

# Status
monkey status
```

## 🤖 Claude Code Integration

### MCP Server (Recommended)

Branch Monkey includes an MCP (Model Context Protocol) server that integrates directly with Claude Code, giving you access to all Branch Monkey commands via `/monkey` tools.

**Installation:**

```bash
# Install with MCP support
pip install branch-monkey[mcp]

# Or if installing from source
pip install -e ".[mcp]"
```

**Configure Claude Code:**

Add to your `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "branch-monkey": {
      "command": "monkey-mcp",
      "env": {
        "MONKEY_REPO_PATH": "/path/to/your/repo"
      }
    }
  }
}
```

Or without a specific repo path (uses current working directory):

```json
{
  "mcpServers": {
    "branch-monkey": {
      "command": "python",
      "args": ["-m", "branch_monkey.mcp_server"]
    }
  }
}
```

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `monkey_ui` | Start the Branch Monkey web UI |
| `monkey_status` | Get current repo status |
| `monkey_save` | Create a checkpoint |
| `monkey_undo` | Restore to previous checkpoint |
| `monkey_experiment_start` | Start a new experiment |
| `monkey_experiment_keep` | Merge current experiment |
| `monkey_experiment_discard` | Discard current experiment |
| `monkey_context_prompt` | Get AI prompt for context generation |
| `monkey_context_save` | Save AI-generated context summary |
| `monkey_context_latest` | Get latest context summary |
| `monkey_history` | Show recent commit history |

### Python API

Branch Monkey is designed to work seamlessly with Claude Code:

```python
from branch_monkey import BranchMonkey

# Initialize
monkey = BranchMonkey()

# Save before making changes
if monkey.has_changes():
    monkey.save("Before Claude's changes")

# Try something new
monkey.try_something("claude-refactor", "Refactoring suggested by Claude")

# Make changes...

# Save progress
monkey.save("Completed refactor")

# Keep or discard
monkey.keep_experiment()  # If successful
# or
monkey.discard_experiment()  # If not
```

### Example Claude Code Workflow

1. **Before major changes**:
   ```python
   monkey.save("Before adding new feature")
   ```

2. **Safe experimentation**:
   ```python
   monkey.try_something("try-new-approach", "Testing alternative solution")
   ```

3. **Review history**:
   ```python
   history = monkey.what_happened(limit=10)
   for entry in history:
       print(f"{entry['short_sha']}: {entry['message']}")
   ```

4. **Easy rollback**:
   ```python
   monkey.undo()  # Go back one step
   ```

## 🎓 Use Cases

### For Beginners

**Problem**: "I don't understand branches"

**Solution**: Use experiments
```bash
monkey try learning-feature
# Play around...
monkey discard  # No harm done!
```

### For Intermediate Users

**Problem**: "I want to try something but don't want to lose my work"

**Solution**: Create a checkpoint first
```bash
monkey save "Current working state"
monkey try experimental-approach
# Try things...
monkey undo  # Safe to go back
```

### For Senior Developers

**Problem**: "Git CLI is slow for quick iterations"

**Solution**: Fast workflow
```bash
monkey save "checkpoint"
# Make changes
monkey undo
# Repeat quickly
```

### For Claude Code Users

**Problem**: "Hard to track Claude's changes"

**Solution**: Checkpoint before and after
```python
monkey.save("Before Claude session")
# Let Claude make changes
monkey.save("After Claude refactor")
# Easy to compare or revert
```

## 🏗️ Architecture

```
branch-monkey/
├── branch_monkey/
│   ├── core/           # Git abstractions
│   │   ├── checkpoint.py   # Save points
│   │   ├── experiment.py   # Safe branches
│   │   └── history.py      # Timeline
│   ├── tui/            # Terminal UI
│   │   ├── app.py          # Main app
│   │   └── screens/        # Different views
│   ├── api.py          # Python API
│   └── cli.py          # Command line
```

## 🔧 Advanced Usage

### Programmatic API

```python
from branch_monkey import BranchMonkey

monkey = BranchMonkey()

# Checkpoints
checkpoint = monkey.save("Important milestone")
monkey.restore(checkpoint['short_id'])

# Experiments
exp = monkey.try_something("refactor", "Testing new approach")
monkey.switch_to("main")
monkey.switch_to("refactor")
monkey.keep_experiment("refactor")

# History
history = monkey.what_happened(limit=20)
results = monkey.search("bug fix")
diff = monkey.show_changes("a1b2c3d")

# Status
has_changes = monkey.has_changes()
current = monkey.current_experiment()
```

### Custom Repository Path

```python
from pathlib import Path

monkey = BranchMonkey(repo_path=Path("/path/to/repo"))
```

## 🐛 Error Handling

Branch Monkey prioritizes safety:

- **Can't lose work**: Changes are always saved before switching
- **Clear errors**: Human-readable error messages
- **Safe defaults**: `--keep` is default for restore operations

```python
try:
    monkey.save("checkpoint")
except Exception as e:
    print(f"Error: {e}")
    # Error messages are clear and actionable
```

## 🤝 Contributing

Contributions welcome! Branch Monkey is designed to be:
- **Beginner-friendly**: Good first issue labels
- **Well-documented**: Code comments and docstrings
- **Easy to test**: Comprehensive test suite

## 📜 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

Built with:
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git integration
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Typer](https://github.com/tiangolo/typer) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/branch-monkey/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/branch-monkey/discussions)

---

**Remember**: With Branch Monkey, you're always safe to experiment. Go wild! 🐵
