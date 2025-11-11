# Branch Monkey - Visual Git Graph

## Current Implementation

I've rebuilt Branch Monkey with **visualization as the main feature**. Here's what we have now:

### Visual Git Graph

The graph shows:
- **Vertical timeline** - newest commits at top
- **Commits as dots** - ● for regular commits, ◉ for current HEAD
- **Branches in separate columns** - branches appear horizontally separated
- **Arrow key navigation** - move up/down through commits
- **Interactive actions** - press Enter to jump to any commit

### Example Output

```
◉    [ed83679] (main) Added visual Git graph...
│
●    [b56e35e] Complete Branch Monkey v0.1.0...
│
●    [66a558b] Added test file
│
  ●  [7781230] (experiment/test-feature) Fixed API...
  │
●    [a27d270] Initial commit
```

### How to Use

#### Command Line
```bash
# See the graph
python demo_graph.py

# Or use the CLI
monkey history
```

#### Interactive TUI
```bash
# Launch the TUI (graph is now the first tab)
monkey

# Then:
# - Use ↑/↓ or j/k to navigate
# - Press Enter to jump to a commit
# - Press 'n' for new checkpoint
# - Press 'e' for new experiment
# - Press 'r' to refresh
# - Press 'q' to quit
```

#### Python API
```python
from branch_monkey.core.graph import GitGraph

# Build graph
graph = GitGraph()
nodes = graph.build_graph(limit=20, all_branches=True)

# Render as ASCII
lines = graph.render_graph(nodes)
for line in lines:
    print(line.text)

# Navigate
for node in nodes:
    print(f"{node.short_sha}: {node.message}")
    print(f"  Branches: {node.branches}")
    print(f"  Column: {node.column}")
```

## What's Working

✅ **Core Features:**
- Visual Git graph with ASCII art
- Commits shown as dots vertically
- Branches shown in separate columns (horizontal positioning)
- Current HEAD highlighted
- Arrow key navigation in TUI
- Jump to any commit
- All metadata (branches, tags, author, age)

✅ **Integration:**
- Works as standalone tool (`monkey`)
- Python API for Claude Code
- CLI commands still work
- Graph is the main/first tab in TUI

## What Could Be Enhanced

The current visualization works and shows the tree structure, but could be improved:

### 1. Better Branch Splits
Currently branches appear in different columns, but the "split point" where a branch diverges isn't visually connected with horizontal lines. Could add:
```
●    [main commit]
├─── [branch splits here]
│ ●  [branch commit]
│ │
● │  [main continues]
```

### 2. Merge Visualization
Show merge commits with lines coming back together:
```
● │  [main]
│ ●  [branch]
●─┘  [merge commit]
```

### 3. More Colors
Currently using basic text. Could add:
- Different colors per branch
- Highlight patterns
- Color-coded commit types

### 4. Compact Mode
Option to show less detail per commit for a more compact tree

## Architecture

```
branch_monkey/
├── core/
│   ├── graph.py          # NEW: Git graph builder and renderer
│   ├── checkpoint.py     # Checkpoint system
│   ├── experiment.py     # Experiment system
│   └── history.py        # History navigation
├── tui/
│   ├── app.py            # Main TUI app (updated with graph)
│   └── screens/
│       ├── graph.py      # NEW: Main graph screen with navigation
│       ├── timeline.py   # Old timeline view
│       ├── checkpoints.py
│       └── experiments.py
├── api.py                # Python API
└── cli.py                # CLI commands
```

## Key Classes

### GitGraph
- `build_graph()` - Builds commit node tree
- `render_graph()` - Renders as ASCII art
- Handles branch column assignment

### CommitNode
- Represents a single commit
- Contains SHA, message, author, timestamp
- Tracks branches, tags, parents
- Knows its column position

### GraphScreen
- Main TUI screen
- Shows rendered graph
- Handles arrow key navigation
- Allows interactive actions

## Testing

```bash
# Test the graph rendering
python demo_graph.py

# Test the TUI (should open graph as first tab)
monkey

# Test CLI still works
monkey history
monkey status
monkey checkpoints
```

## Next Steps (If Desired)

1. **Enhanced branch visualization** - Add horizontal lines at split/merge points
2. **Better color coding** - Per-branch colors, merge highlights
3. **Zoom levels** - Compact vs detailed views
4. **Search/filter in graph** - Find commits while viewing tree
5. **Side panel** - Show commit details next to graph

The foundation is solid - the graph builds correctly, renders, and is interactive. The enhancements would be polish on top of this working system!
