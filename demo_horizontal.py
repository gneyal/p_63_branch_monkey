#!/usr/bin/env python
"""Demo horizontal graph visualization."""

from branch_monkey.core.graph_horizontal import HorizontalGitGraph

# Build graph
graph = HorizontalGitGraph()
nodes, branches = graph.build_graph(limit=20)

print("=" * 100)
print("BRANCH MONKEY - HORIZONTAL GIT GRAPH")
print("=" * 100)
print()
print(f"Found {len(nodes)} commits across {len(branches)} branches")
print()

# Show branches
print(f"Branches: {', '.join(branches.keys())}")
print()

# Render horizontal graph
lines = graph.render_graph(nodes, branches)

print("VISUAL TREE (Horizontal - Time flows left → right):")
print("-" * 100)
for line in lines:
    print(line)

print()
print("=" * 100)
print("LEGEND:")
print("  ◉  = Current HEAD (where you are)")
print("  ●  = Commit")
print("  ─  = Timeline connection")
print("  Time flows LEFT (old) → RIGHT (new)")
print("=" * 100)
print()
print("CONTROLS IN TUI:")
print("  Tab       - Jump to next branch")
print("  Enter     - Checkout selected branch")
print("  ←/→       - Navigate commits")
print("  n         - New checkpoint")
print("  e         - New experiment")
print("=" * 100)
