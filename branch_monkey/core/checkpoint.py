"""Checkpoint system - simple save/restore abstraction over Git commits and stashes."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import git
from git.exc import GitCommandError, InvalidGitRepositoryError


@dataclass
class Checkpoint:
    """A save point in your code's history."""

    id: str  # Commit SHA or stash ref
    message: str
    timestamp: datetime
    author: str
    is_temporary: bool = False  # True for stashes, False for commits
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0

    @property
    def short_id(self) -> str:
        """Get short version of checkpoint ID."""
        return self.id[:7] if len(self.id) > 7 else self.id

    @property
    def age(self) -> str:
        """Human-readable age of checkpoint."""
        delta = datetime.now() - self.timestamp
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"


class CheckpointManager:
    """Manages checkpoints (save points) in your Git repository."""

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize checkpoint manager.

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

    def create(self, message: str, include_untracked: bool = False) -> Checkpoint:
        """
        Create a new checkpoint (commit).

        Args:
            message: Description of what you're saving
            include_untracked: Whether to include new files

        Returns:
            Created checkpoint

        Raises:
            GitCommandError: If there are no changes to save
        """
        # Check if there are changes
        if not self.has_changes():
            raise GitCommandError(
                "git commit", "No changes to save. Modify some files first!"
            )

        # Stage all changes
        if include_untracked:
            self.repo.git.add(A=True)
        else:
            self.repo.git.add(u=True)

        # Create commit
        commit = self.repo.index.commit(message)

        return self._commit_to_checkpoint(commit)

    def create_temporary(self, message: str = "Quick save") -> Checkpoint:
        """
        Create a temporary checkpoint (stash).

        This saves your current work without creating a permanent checkpoint.
        Useful for quickly trying something without committing.

        Args:
            message: Description of what you're saving

        Returns:
            Created temporary checkpoint
        """
        if not self.has_changes():
            raise GitCommandError(
                "git stash", "No changes to save. Modify some files first!"
            )

        # Create stash
        self.repo.git.stash("push", "-m", message, "--include-untracked")

        # Get the stash we just created
        stash_list = self.repo.git.stash("list").split("\n")
        if not stash_list or not stash_list[0]:
            raise GitCommandError("git stash", "Failed to create temporary checkpoint")

        # Parse stash entry
        stash_ref = stash_list[0].split(":")[0]  # e.g., "stash@{0}"

        return Checkpoint(
            id=stash_ref,
            message=message,
            timestamp=datetime.now(),
            author=self._get_current_user(),
            is_temporary=True,
        )

    def restore(self, checkpoint: Checkpoint, keep_changes: bool = False) -> None:
        """
        Restore to a checkpoint.

        Args:
            checkpoint: Checkpoint to restore to
            keep_changes: If True, keeps current changes. If False, discards them.

        Raises:
            GitCommandError: If restore fails
        """
        if checkpoint.is_temporary:
            # Restore from stash
            self.repo.git.stash("apply", checkpoint.id)
        else:
            # Restore from commit
            if keep_changes:
                # Soft reset - keeps changes staged
                self.repo.git.reset("--soft", checkpoint.id)
            else:
                # Hard reset - discards changes
                if self.has_changes():
                    # Stash current changes as backup
                    self.create_temporary("Auto-backup before restore")

                self.repo.git.reset("--hard", checkpoint.id)

    def list_checkpoints(self, limit: int = 20) -> List[Checkpoint]:
        """
        List recent checkpoints.

        Args:
            limit: Maximum number of checkpoints to return

        Returns:
            List of checkpoints, newest first
        """
        checkpoints = []

        # Add commits
        for commit in self.repo.iter_commits(max_count=limit):
            checkpoints.append(self._commit_to_checkpoint(commit))

        return checkpoints

    def list_temporary(self) -> List[Checkpoint]:
        """
        List temporary checkpoints (stashes).

        Returns:
            List of temporary checkpoints
        """
        checkpoints = []

        try:
            stash_list = self.repo.git.stash("list").split("\n")
        except GitCommandError:
            return []

        for entry in stash_list:
            if not entry:
                continue

            # Parse: "stash@{0}: On main: Quick save"
            parts = entry.split(": ", 2)
            if len(parts) < 3:
                continue

            stash_ref = parts[0]
            message = parts[2]

            # Try to get timestamp from stash commit
            try:
                stash_commit = self.repo.commit(stash_ref)
                timestamp = datetime.fromtimestamp(stash_commit.committed_date)
                author = stash_commit.author.name
            except Exception:
                timestamp = datetime.now()
                author = self._get_current_user()

            checkpoints.append(
                Checkpoint(
                    id=stash_ref,
                    message=message,
                    timestamp=timestamp,
                    author=author,
                    is_temporary=True,
                )
            )

        return checkpoints

    def has_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        return (
            self.repo.is_dirty()
            or len(self.repo.untracked_files) > 0
        )

    def get_current_checkpoint(self) -> Optional[Checkpoint]:
        """Get the current checkpoint (HEAD commit)."""
        try:
            commit = self.repo.head.commit
            return self._commit_to_checkpoint(commit)
        except Exception:
            return None

    def _commit_to_checkpoint(self, commit: git.Commit) -> Checkpoint:
        """Convert Git commit to Checkpoint."""
        # Get stats
        stats = commit.stats.total
        files_changed = stats.get("files", 0)
        insertions = stats.get("insertions", 0)
        deletions = stats.get("deletions", 0)

        return Checkpoint(
            id=commit.hexsha,
            message=commit.message.strip(),
            timestamp=datetime.fromtimestamp(commit.committed_date),
            author=commit.author.name,
            is_temporary=False,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        )

    def _get_current_user(self) -> str:
        """Get current Git user name."""
        try:
            return self.repo.config_reader().get_value("user", "name", default="Unknown")
        except Exception:
            return "Unknown"
