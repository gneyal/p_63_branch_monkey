"""Horizontal Git graph visualization - time flows left to right."""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import git
from git.exc import InvalidGitRepositoryError
from datetime import datetime


@dataclass
class CommitNode:
    """A commit in the graph."""

    sha: str
    short_sha: str
    message: str
    author: str
    timestamp: datetime
    parents: List[str]
    children: List[str]  # For horizontal layout, we need children too
    branches: List[str]
    tags: List[str]
    is_head: bool = False
    is_merge: bool = False
    row: int = 0  # Which row (vertical position)
    col: int = 0  # Which column (horizontal position, time)

    @property
    def age(self) -> str:
        """Human-readable age."""
        delta = datetime.now() - self.timestamp
        if delta.days > 365:
            return f"{delta.days // 365}y"
        elif delta.days > 30:
            return f"{delta.days // 30}mo"
        elif delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60}m"
        else:
            return "now"


class HorizontalGitGraph:
    """
    Builds and renders a horizontal Git graph.

    The graph shows:
    - Horizontal timeline (oldest on left, newest on right)
    - Commits as dots (●)
    - Branches as rows (vertical separation)
    - Current HEAD position highlighted (◉)
    """

    # Drawing characters
    COMMIT = "●"
    CURRENT = "◉"
    HORIZONTAL = "─"
    VERTICAL = "│"
    SPLIT_DOWN = "┬"
    SPLIT_UP = "┴"
    MERGE_RIGHT = "┤"
    MERGE_LEFT = "├"
    CORNER_DOWN_RIGHT = "┌"
    CORNER_DOWN_LEFT = "┐"
    CORNER_UP_RIGHT = "└"
    CORNER_UP_LEFT = "┘"

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize graph builder.

        Args:
            repo_path: Path to Git repository
        """
        self.repo_path = repo_path or Path.cwd()
        try:
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(
                f"{self.repo_path} is not a Git repository."
            )

    def build_graph(self, limit: int = 30) -> Tuple[List[CommitNode], Dict[str, List[CommitNode]]]:
        """
        Build the commit graph with horizontal layout.

        Args:
            limit: Maximum number of commits per branch

        Returns:
            Tuple of (all nodes, nodes by branch)
        """
        nodes = []
        node_map = {}  # sha -> node

        # Get HEAD commit SHA
        try:
            head_sha = self.repo.head.commit.hexsha
        except Exception:
            head_sha = None

        # Get all branches
        branches = {}  # branch_name -> list of commits
        for branch in self.repo.branches:
            branch_commits = []
            for commit in self.repo.iter_commits(branch.name, max_count=limit):
                sha = commit.hexsha

                # Create or update node
                if sha not in node_map:
                    node = CommitNode(
                        sha=sha,
                        short_sha=sha[:7],
                        message=commit.message.strip(),
                        author=commit.author.name,
                        timestamp=datetime.fromtimestamp(commit.committed_date),
                        parents=[p.hexsha for p in commit.parents],
                        children=[],
                        branches=[],
                        tags=[],
                        is_head=(sha == head_sha),
                        is_merge=(len(commit.parents) > 1),
                    )
                    node_map[sha] = node
                    nodes.append(node)

                # Add branch to this commit
                if branch.name not in node_map[sha].branches:
                    node_map[sha].branches.append(branch.name)

                branch_commits.append(node_map[sha])

            branches[branch.name] = branch_commits

        # Build parent-child relationships
        for node in nodes:
            for parent_sha in node.parents:
                if parent_sha in node_map:
                    node_map[parent_sha].children.append(node.sha)

        # Get tags
        for tag in self.repo.tags:
            sha = tag.commit.hexsha
            if sha in node_map:
                node_map[sha].tags.append(tag.name)

        # Assign positions (row and column)
        self._assign_positions(branches, node_map)

        return nodes, branches

    def _assign_positions(self, branches: Dict[str, List[CommitNode]], node_map: Dict[str, CommitNode]) -> None:
        """
        Assign row (vertical) and column (horizontal) positions.

        Args:
            branches: Dictionary of branch name to list of commits
            node_map: Dictionary of SHA to CommitNode
        """
        # Assign rows (each branch gets a row)
        row_assignments = {}
        current_row = 0

        # Sort branches: main/master first, then alphabetically
        sorted_branches = sorted(branches.keys(), key=lambda b: (
            b not in ['main', 'master'],  # main/master first
            b
        ))

        for branch_name in sorted_branches:
            row_assignments[branch_name] = current_row
            current_row += 1

        # Assign columns based on timestamp (oldest = leftmost)
        all_commits = list(node_map.values())
        all_commits.sort(key=lambda n: n.timestamp)

        for col, node in enumerate(all_commits):
            node.col = col
            # Assign row based on primary branch
            if node.branches:
                primary_branch = node.branches[0]
                node.row = row_assignments.get(primary_branch, 0)

    def render_graph(self, nodes: List[CommitNode], branches: Dict[str, List[CommitNode]], width: int = 120) -> List[str]:
        """
        Render the graph as ASCII art (horizontal).

        Args:
            nodes: List of commit nodes
            branches: Dictionary of branch name to list of commits
            width: Maximum width

        Returns:
            List of strings, one per row
        """
        if not nodes:
            return ["No commits yet"]

        # Find dimensions
        max_row = max(node.row for node in nodes)
        max_col = max(node.col for node in nodes)

        # Create grid
        grid = {}  # (row, col) -> character

        # Place commits
        for node in nodes:
            symbol = self.CURRENT if node.is_head else self.COMMIT
            grid[(node.row, node.col)] = symbol

        # Draw connections (horizontal lines between commits in same row)
        for node in nodes:
            # Connect to children in same row
            for child_sha in node.children:
                child = next((n for n in nodes if n.sha == child_sha), None)
                if child and child.row == node.row:
                    # Draw horizontal line
                    for c in range(node.col + 1, child.col):
                        if (node.row, c) not in grid:
                            grid[(node.row, c)] = self.HORIZONTAL

        # Convert grid to strings
        lines = []

        # For each row, also show branch name and commit info
        sorted_branches = sorted(branches.keys(), key=lambda b: (
            b not in ['main', 'master'],
            b
        ))

        for row_idx, branch_name in enumerate(sorted_branches):
            # Build the line for this row
            line_chars = []

            # Branch name (fixed width)
            branch_label = f"{branch_name:12s} "
            line_chars.append(branch_label)

            # Graph part
            for col in range(max_col + 1):
                if (row_idx, col) in grid:
                    char = grid[(row_idx, col)]
                    line_chars.append(char)

                    # Add space after commit
                    if char in [self.COMMIT, self.CURRENT]:
                        line_chars.append(self.HORIZONTAL)
                    else:
                        line_chars.append("")
                else:
                    line_chars.append("  ")

            # Find commit info for this row/branch
            branch_commits = branches[branch_name]
            if branch_commits:
                latest = branch_commits[0]  # Most recent
                info = f"  {latest.short_sha} {latest.message[:40]}"
                line_chars.append(info)

            lines.append("".join(line_chars))

        return lines

    def get_branches_list(self, branches: Dict[str, List[CommitNode]]) -> List[Tuple[str, CommitNode]]:
        """
        Get list of branches with their latest commit.

        Args:
            branches: Dictionary of branch name to list of commits

        Returns:
            List of (branch_name, latest_commit) tuples
        """
        result = []
        for branch_name, commits in branches.items():
            if commits:
                result.append((branch_name, commits[0]))
        return result

    def get_branch_commits(self, branch_name: str, branches: Dict[str, List[CommitNode]]) -> List[CommitNode]:
        """Get all commits for a branch."""
        return branches.get(branch_name, [])
