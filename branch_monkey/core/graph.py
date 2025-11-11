"""Git graph visualization - the main feature of Branch Monkey."""

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
    branches: List[str]
    tags: List[str]
    is_head: bool = False
    is_merge: bool = False
    column: int = 0  # Which column this commit is in (for horizontal positioning)

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


@dataclass
class GraphLine:
    """A line in the rendered graph."""

    text: str
    commit_node: Optional[CommitNode] = None
    is_commit_line: bool = False


class GitGraph:
    """
    Builds and renders a visual Git graph.

    The graph shows:
    - Vertical timeline (newest at top)
    - Commits as dots (●)
    - Branches splitting horizontally
    - Current HEAD position highlighted
    """

    # Box drawing characters
    COMMIT = "●"
    CURRENT = "◉"
    LINE = "│"
    BRANCH_START = "├"
    BRANCH_END = "┤"
    MERGE = "┼"
    HORIZONTAL = "─"
    CORNER_DOWN_RIGHT = "└"
    CORNER_DOWN_LEFT = "┘"
    CORNER_UP_RIGHT = "┌"
    CORNER_UP_LEFT = "┐"
    SPLIT_RIGHT = "├"
    SPLIT_LEFT = "┤"
    CROSS = "┼"

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

    def build_graph(self, limit: int = 50, all_branches: bool = True) -> List[CommitNode]:
        """
        Build the commit graph.

        Args:
            limit: Maximum number of commits
            all_branches: If True, includes all branches. If False, only current branch.

        Returns:
            List of CommitNodes in topological order (newest first)
        """
        nodes = []

        # Get all commits
        kwargs = {"max_count": limit}
        if all_branches:
            kwargs["all"] = True

        # Get HEAD commit SHA
        try:
            head_sha = self.repo.head.commit.hexsha
        except Exception:
            head_sha = None

        # Get branch information
        branch_commits = {}  # sha -> [branch names]
        for branch in self.repo.branches:
            sha = branch.commit.hexsha
            if sha not in branch_commits:
                branch_commits[sha] = []
            branch_commits[sha].append(branch.name)

        # Get tag information
        tag_commits = {}  # sha -> [tag names]
        for tag in self.repo.tags:
            sha = tag.commit.hexsha
            if sha not in tag_commits:
                tag_commits[sha] = []
            tag_commits[sha].append(tag.name)

        # Build nodes
        for commit in self.repo.iter_commits(**kwargs):
            sha = commit.hexsha
            short_sha = sha[:7]

            # Get parent SHAs
            parent_shas = [p.hexsha for p in commit.parents]

            # Get branches and tags
            branches = branch_commits.get(sha, [])
            tags = tag_commits.get(sha, [])

            # Check if HEAD
            is_head = sha == head_sha

            # Check if merge
            is_merge = len(parent_shas) > 1

            node = CommitNode(
                sha=sha,
                short_sha=short_sha,
                message=commit.message.strip(),
                author=commit.author.name,
                timestamp=datetime.fromtimestamp(commit.committed_date),
                parents=parent_shas,
                branches=branches,
                tags=tags,
                is_head=is_head,
                is_merge=is_merge,
            )

            nodes.append(node)

        # Assign columns for visual positioning
        self._assign_columns(nodes)

        return nodes

    def _assign_columns(self, nodes: List[CommitNode]) -> None:
        """
        Assign horizontal column positions to commits.

        This determines where commits appear horizontally when branches split.
        """
        # Build a map of sha -> node for quick lookup
        node_map = {node.sha: node for node in nodes}

        # Track which column each branch is using
        branch_columns: Dict[str, int] = {}
        next_column = 0

        # Process in order (already topologically sorted)
        for node in nodes:
            # If this commit has branches, assign columns
            if node.branches:
                # Use existing column or assign new one
                assigned = False
                for branch in node.branches:
                    if branch in branch_columns:
                        node.column = branch_columns[branch]
                        assigned = True
                        break

                if not assigned:
                    node.column = next_column
                    for branch in node.branches:
                        branch_columns[branch] = next_column
                    next_column += 1
            else:
                # Inherit from parent if possible
                if node.parents:
                    parent_sha = node.parents[0]
                    if parent_sha in node_map:
                        node.column = node_map[parent_sha].column
                    else:
                        node.column = 0
                else:
                    node.column = 0

    def render_graph(
        self,
        nodes: List[CommitNode],
        width: int = 80,
        show_details: bool = True,
    ) -> List[GraphLine]:
        """
        Render the graph as ASCII art.

        Args:
            nodes: List of commit nodes
            width: Maximum width for rendering
            show_details: If True, shows commit message and details

        Returns:
            List of GraphLines to display
        """
        lines = []

        if not nodes:
            return [GraphLine("No commits yet", None, False)]

        # Calculate max column to know total width needed
        max_column = max(node.column for node in nodes) if nodes else 0

        # Render each commit
        for i, node in enumerate(nodes):
            # Build the graph part (left side with dots and lines)
            graph_part = self._build_graph_part(node, nodes, i, max_column)

            # Build the info part (right side with message)
            info_part = self._build_info_part(node, width - len(graph_part) - 2)

            # Combine
            line_text = f"{graph_part}  {info_part}"

            lines.append(GraphLine(line_text, node, True))

            # Add connection lines between commits if needed
            if i < len(nodes) - 1:
                next_node = nodes[i + 1]
                connector_lines = self._build_connector_lines(
                    node, next_node, max_column
                )
                for conn_line in connector_lines:
                    lines.append(GraphLine(conn_line, None, False))

        return lines

    def _build_graph_part(
        self, node: CommitNode, all_nodes: List[CommitNode], index: int, max_column: int
    ) -> str:
        """Build the left graph part showing the tree structure."""
        parts = []

        # Build columns
        for col in range(max_column + 1):
            if col == node.column:
                # This is the commit's column
                if node.is_head:
                    parts.append(self.CURRENT)
                else:
                    parts.append(self.COMMIT)
            else:
                # Check if we need a line here for another branch
                parts.append(" ")

        return " ".join(parts)

    def _build_info_part(self, node: CommitNode, max_width: int) -> str:
        """Build the right info part with commit details."""
        parts = []

        # SHA
        parts.append(f"[{node.short_sha}]")

        # Branches
        if node.branches:
            for branch in node.branches:
                parts.append(f"({branch})")

        # Tags
        if node.tags:
            for tag in node.tags:
                parts.append(f"<{tag}>")

        # Message
        message = node.message.split("\n")[0]  # First line only
        parts.append(message[:60])  # Truncate if too long

        # Author and age
        parts.append(f"- {node.author} {node.age}")

        info = " ".join(parts)

        # Truncate to max width
        if len(info) > max_width:
            info = info[: max_width - 3] + "..."

        return info

    def _build_connector_lines(
        self, current: CommitNode, next_node: CommitNode, max_column: int
    ) -> List[str]:
        """Build connector lines between commits."""
        lines = []

        # Simple vertical line for now
        parts = []
        for col in range(max_column + 1):
            if col == current.column:
                parts.append(self.LINE)
            else:
                parts.append(" ")

        lines.append(" ".join(parts))

        return lines

    def get_node_by_sha(self, nodes: List[CommitNode], sha: str) -> Optional[CommitNode]:
        """Find a node by SHA (full or short)."""
        for node in nodes:
            if node.sha.startswith(sha) or node.short_sha == sha:
                return node
        return None

    def get_node_index(self, nodes: List[CommitNode], node: CommitNode) -> int:
        """Get the index of a node in the list."""
        try:
            return nodes.index(node)
        except ValueError:
            return -1
