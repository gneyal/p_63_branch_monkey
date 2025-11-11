"""History navigation - visual timeline and diff viewing."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import git
from git.exc import GitCommandError, InvalidGitRepositoryError


@dataclass
class FileChange:
    """A change to a single file."""

    path: str
    change_type: str  # 'added', 'modified', 'deleted', 'renamed'
    insertions: int = 0
    deletions: int = 0
    old_path: Optional[str] = None  # For renamed files

    @property
    def icon(self) -> str:
        """Get icon for change type."""
        icons = {
            "added": "✨",
            "modified": "📝",
            "deleted": "🗑️ ",
            "renamed": "📋",
        }
        return icons.get(self.change_type, "❓")

    @property
    def summary(self) -> str:
        """Get human-readable summary."""
        if self.change_type == "renamed":
            return f"{self.old_path} → {self.path}"
        elif self.insertions > 0 or self.deletions > 0:
            parts = []
            if self.insertions > 0:
                parts.append(f"+{self.insertions}")
            if self.deletions > 0:
                parts.append(f"-{self.deletions}")
            return f"{self.path} ({', '.join(parts)})"
        else:
            return self.path


@dataclass
class HistoryEntry:
    """An entry in the project history."""

    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: List[FileChange]
    branch: Optional[str] = None
    tags: List[str] = None
    is_merge: bool = False

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def short_sha(self) -> str:
        """Get short version of SHA."""
        return self.sha[:7]

    @property
    def age(self) -> str:
        """Human-readable age."""
        delta = datetime.now() - self.timestamp
        if delta.days > 365:
            years = delta.days // 365
            return f"{years}y"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months}mo"
        elif delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours}h"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes}m"
        else:
            return "now"

    @property
    def summary_stats(self) -> str:
        """Summary of changes."""
        total_files = len(self.files_changed)
        total_insertions = sum(f.insertions for f in self.files_changed)
        total_deletions = sum(f.deletions for f in self.files_changed)

        parts = [f"{total_files} file{'s' if total_files != 1 else ''}"]
        if total_insertions > 0:
            parts.append(f"+{total_insertions}")
        if total_deletions > 0:
            parts.append(f"-{total_deletions}")

        return ", ".join(parts)


class HistoryNavigator:
    """Navigate and visualize project history."""

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize history navigator.

        Args:
            repo_path: Path to Git repository. If None, uses current directory.

        Raises:
            InvalidGitRepositoryError: If path is not a Git repository.
        """
        self.repo_path = repo_path or Path.cwd()
        try:
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(
                f"{self.repo_path} is not a Git repository. "
                "Run 'git init' first to use Branch Monkey."
            )

    def get_history(
        self,
        limit: int = 50,
        branch: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> List[HistoryEntry]:
        """
        Get project history.

        Args:
            limit: Maximum number of entries to return
            branch: Specific branch to show history for. If None, uses current branch.
            file_path: If provided, only shows history for this file

        Returns:
            List of history entries, newest first
        """
        entries = []

        # Build arguments for iter_commits
        kwargs = {"max_count": limit}
        if branch:
            kwargs["rev"] = branch
        if file_path:
            kwargs["paths"] = file_path

        # Iterate commits
        for commit in self.repo.iter_commits(**kwargs):
            # Get file changes
            file_changes = self._get_file_changes(commit)

            # Determine if merge commit
            is_merge = len(commit.parents) > 1

            # Get tags for this commit
            tags = [tag.name for tag in self.repo.tags if tag.commit == commit]

            # Get branch (for current HEAD)
            branch_name = None
            try:
                if commit == self.repo.head.commit:
                    branch_name = self.repo.active_branch.name
            except Exception:
                pass

            entries.append(
                HistoryEntry(
                    sha=commit.hexsha,
                    message=commit.message.strip(),
                    author=commit.author.name,
                    timestamp=datetime.fromtimestamp(commit.committed_date),
                    files_changed=file_changes,
                    branch=branch_name,
                    tags=tags,
                    is_merge=is_merge,
                )
            )

        return entries

    def get_branches_timeline(self) -> Dict[str, List[HistoryEntry]]:
        """
        Get history organized by branches.

        Returns:
            Dictionary mapping branch names to their histories
        """
        timeline = {}

        for branch in self.repo.branches:
            # Get history for this branch (limit to recent commits)
            history = self.get_history(limit=20, branch=branch.name)
            timeline[branch.name] = history

        return timeline

    def get_diff(self, entry: HistoryEntry, file_path: Optional[str] = None) -> str:
        """
        Get diff for a history entry.

        Args:
            entry: History entry to get diff for
            file_path: If provided, only shows diff for this file

        Returns:
            Diff as string
        """
        try:
            commit = self.repo.commit(entry.sha)

            # If no parent, this is first commit
            if not commit.parents:
                if file_path:
                    return self.repo.git.show(f"{entry.sha}:{file_path}")
                else:
                    return self.repo.git.show(entry.sha)

            # Get diff with parent
            parent = commit.parents[0]

            if file_path:
                return self.repo.git.diff(parent.hexsha, entry.sha, "--", file_path)
            else:
                return self.repo.git.diff(parent.hexsha, entry.sha)

        except Exception as e:
            raise GitCommandError("git diff", f"Failed to get diff: {e}")

    def search_history(
        self, query: str, search_in: str = "message", limit: int = 50
    ) -> List[HistoryEntry]:
        """
        Search project history.

        Args:
            query: Search query
            search_in: What to search in ('message', 'author', 'content')
            limit: Maximum number of results

        Returns:
            Matching history entries
        """
        if search_in == "message":
            # Search in commit messages
            entries = self.get_history(limit=limit)
            return [e for e in entries if query.lower() in e.message.lower()]

        elif search_in == "author":
            # Search by author
            entries = self.get_history(limit=limit)
            return [e for e in entries if query.lower() in e.author.lower()]

        elif search_in == "content":
            # Search in commit content (pickaxe)
            try:
                commits = list(
                    self.repo.iter_commits(max_count=limit, all=True, G=query)
                )
                entries = []
                for commit in commits:
                    file_changes = self._get_file_changes(commit)
                    entries.append(
                        HistoryEntry(
                            sha=commit.hexsha,
                            message=commit.message.strip(),
                            author=commit.author.name,
                            timestamp=datetime.fromtimestamp(commit.committed_date),
                            files_changed=file_changes,
                            is_merge=len(commit.parents) > 1,
                        )
                    )
                return entries
            except Exception:
                return []

        return []

    def get_file_history(self, file_path: str, limit: int = 20) -> List[HistoryEntry]:
        """
        Get history for a specific file.

        Args:
            file_path: Path to file (relative to repo root)
            limit: Maximum number of entries

        Returns:
            History entries that modified this file
        """
        return self.get_history(limit=limit, file_path=file_path)

    def compare_commits(
        self, sha1: str, sha2: str
    ) -> Tuple[List[FileChange], str]:
        """
        Compare two commits.

        Args:
            sha1: First commit SHA
            sha2: Second commit SHA

        Returns:
            Tuple of (file changes, full diff)
        """
        try:
            # Get diff
            diff_text = self.repo.git.diff(sha1, sha2)

            # Get file changes
            commit1 = self.repo.commit(sha1)
            commit2 = self.repo.commit(sha2)

            # Get diff stats
            diff_index = commit1.diff(commit2)

            file_changes = []
            for diff_item in diff_index:
                change_type = "modified"
                old_path = None

                if diff_item.new_file:
                    change_type = "added"
                elif diff_item.deleted_file:
                    change_type = "deleted"
                elif diff_item.renamed_file:
                    change_type = "renamed"
                    old_path = diff_item.rename_from

                # Try to get line counts (may not always be available)
                insertions = 0
                deletions = 0
                if hasattr(diff_item, "diff"):
                    diff_str = diff_item.diff.decode("utf-8", errors="ignore")
                    for line in diff_str.split("\n"):
                        if line.startswith("+") and not line.startswith("+++"):
                            insertions += 1
                        elif line.startswith("-") and not line.startswith("---"):
                            deletions += 1

                file_changes.append(
                    FileChange(
                        path=diff_item.b_path or diff_item.a_path,
                        change_type=change_type,
                        insertions=insertions,
                        deletions=deletions,
                        old_path=old_path,
                    )
                )

            return file_changes, diff_text

        except Exception as e:
            raise GitCommandError("git diff", f"Failed to compare commits: {e}")

    def _get_file_changes(self, commit: git.Commit) -> List[FileChange]:
        """Get file changes for a commit."""
        file_changes = []

        # If no parent, this is the first commit
        if not commit.parents:
            # Show all files as added
            for item in commit.tree.traverse():
                if item.type == "blob":  # It's a file
                    file_changes.append(
                        FileChange(
                            path=item.path,
                            change_type="added",
                        )
                    )
            return file_changes

        # Get diff with parent
        parent = commit.parents[0]
        diffs = parent.diff(commit)

        for diff_item in diffs:
            change_type = "modified"
            old_path = None

            if diff_item.new_file:
                change_type = "added"
            elif diff_item.deleted_file:
                change_type = "deleted"
            elif diff_item.renamed_file:
                change_type = "renamed"
                old_path = diff_item.rename_from

            # Try to count lines (may not always work)
            insertions = 0
            deletions = 0
            try:
                if hasattr(diff_item, "diff") and diff_item.diff:
                    diff_str = diff_item.diff.decode("utf-8", errors="ignore")
                    for line in diff_str.split("\n"):
                        if line.startswith("+") and not line.startswith("+++"):
                            insertions += 1
                        elif line.startswith("-") and not line.startswith("---"):
                            deletions += 1
            except Exception:
                pass

            file_changes.append(
                FileChange(
                    path=diff_item.b_path or diff_item.a_path,
                    change_type=change_type,
                    insertions=insertions,
                    deletions=deletions,
                    old_path=old_path,
                )
            )

        return file_changes
