#!/usr/bin/env python
"""Demo script showing the current graph visualization."""

from branch_monkey.core.graph import GitGraph

# Build graph
graph = GitGraph()
nodes = graph.build_graph(limit=15, all_branches=True)

print("=" * 80)
print("BRANCH MONKEY - GIT GRAPH VISUALIZATION")
print("=" * 80)
print()
print(f"Found {len(nodes)} commits")
print()

# Show branch information
branches = set()
for node in nodes:
    branches.update(node.branches)

if branches:
    print(f"Branches: {', '.join(branches)}")
    print()

# Render graph
lines = graph.render_graph(nodes, width=100)

print("VISUAL TREE:")
print("-" * 80)
for line in lines[:30]:  # Show first 30 lines
    print(line.text)

if len(lines) > 30:
    print(f"... and {len(lines) - 30} more lines")

print()
print("=" * 80)
print("LEGEND:")
print("  ◉  = Current HEAD (where you are)")
print("  ●  = Commit")
print("  │  = Branch line")
print("  [sha] = Commit SHA")
print("  (branch) = Branch name")
print("=" * 80)
