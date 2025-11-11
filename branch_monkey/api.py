"""Public API for Claude Code and programmatic usage."""

from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import asdict, fields

from .core.checkpoint import CheckpointManager, Checkpoint
from .core.experiment import ExperimentManager, Experiment
from .core.history import HistoryNavigator, HistoryEntry


def to_dict(obj: Any) -> Dict:
    """
    Convert dataclass to dict, including properties.

    Args:
        obj: Dataclass instance

    Returns:
        Dictionary with all fields and properties
    """
    # Start with basic fields
    result = asdict(obj)

    # Add properties
    for attr_name in dir(obj):
        # Skip private attributes and methods
        if attr_name.startswith('_'):
            continue

        attr = getattr(type(obj), attr_name, None)

        # Check if it's a property
        if isinstance(attr, property):
            try:
                result[attr_name] = getattr(obj, attr_name)
            except Exception:
                pass  # Skip properties that raise errors

    return result


class BranchMonkey:
    """
    Main API for Branch Monkey.

    This class provides a simple, human-friendly interface to Git operations.
    Perfect for integration with Claude Code or other tools.

    Example:
        >>> monkey = BranchMonkey()
        >>> monkey.save("Added new feature")
        >>> monkey.try_something("refactor", "Trying new architecture")
        >>> monkey.undo()
    """

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize Branch Monkey.

        Args:
            repo_path: Path to Git repository. If None, uses current directory.
        """
        self.repo_path = repo_path or Path.cwd()
        self.checkpoints = CheckpointManager(self.repo_path)
        self.experiments = ExperimentManager(self.repo_path)
        self.history = HistoryNavigator(self.repo_path)

    # === Checkpoint API ===

    def save(self, message: str, include_untracked: bool = True) -> Dict:
        """
        Save current work as a checkpoint.

        This is like hitting "Save" in a video game. You can always come back to this point.

        Args:
            message: Description of what you're saving
            include_untracked: Whether to include new files (default: True)

        Returns:
            Dictionary with checkpoint info

        Example:
            >>> monkey.save("Before trying refactor")
        """
        checkpoint = self.checkpoints.create(message, include_untracked)
        return to_dict(checkpoint)

    def quick_save(self, message: str = "Quick save") -> Dict:
        """
        Quickly save current work (temporary).

        This creates a temporary save point. Great for "let me just save this real quick".

        Args:
            message: Description (default: "Quick save")

        Returns:
            Dictionary with checkpoint info

        Example:
            >>> monkey.quick_save("Before pulling changes")
        """
        checkpoint = self.checkpoints.create_temporary(message)
        return to_dict(checkpoint)

    def undo(self, keep_changes: bool = True) -> None:
        """
        Go back to the previous checkpoint.

        Args:
            keep_changes: If True, keeps your current changes (default: True for safety)

        Example:
            >>> monkey.undo()  # Go back, but keep my current work
        """
        checkpoints = self.checkpoints.list_checkpoints(limit=5)
        if len(checkpoints) < 2:
            raise ValueError("Nothing to undo to")

        # Go to previous checkpoint (index 1, since 0 is current)
        self.checkpoints.restore(checkpoints[1], keep_changes=keep_changes)

    def restore(self, checkpoint_id: str, keep_changes: bool = True) -> None:
        """
        Restore to a specific checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore (short SHA or full)
            keep_changes: Whether to keep current changes (default: True for safety)

        Example:
            >>> monkey.restore("a1b2c3d")
        """
        checkpoints = self.checkpoints.list_checkpoints(limit=100)

        # Find checkpoint by ID
        checkpoint = None
        for cp in checkpoints:
            if cp.id.startswith(checkpoint_id) or cp.short_id == checkpoint_id:
                checkpoint = cp
                break

        if not checkpoint:
            raise ValueError(f"Checkpoint '{checkpoint_id}' not found")

        self.checkpoints.restore(checkpoint, keep_changes=keep_changes)

    def list_saves(self, limit: int = 20) -> List[Dict]:
        """
        List recent checkpoints.

        Args:
            limit: Maximum number to return (default: 20)

        Returns:
            List of checkpoint dictionaries

        Example:
            >>> saves = monkey.list_saves()
            >>> for save in saves:
            ...     print(f"{save['short_id']}: {save['message']}")
        """
        checkpoints = self.checkpoints.list_checkpoints(limit)
        return [to_dict(cp) for cp in checkpoints]

    def has_changes(self) -> bool:
        """
        Check if there are unsaved changes.

        Returns:
            True if there are changes, False otherwise

        Example:
            >>> if monkey.has_changes():
            ...     monkey.save("Before switching")
        """
        return self.checkpoints.has_changes()

    # === Experiment API ===

    def try_something(
        self, name: str, description: str = "", base: Optional[str] = None
    ) -> Dict:
        """
        Start a new experiment.

        This creates a safe place to try new things without affecting your main work.

        Args:
            name: Name for the experiment (e.g., "new-feature")
            description: What you're trying (optional)
            base: Branch to start from (default: current branch)

        Returns:
            Dictionary with experiment info

        Example:
            >>> monkey.try_something("refactor", "Trying new architecture")
        """
        experiment = self.experiments.create(name, description, base)
        return to_dict(experiment)

    def switch_to(self, experiment_name: str) -> None:
        """
        Switch to an experiment.

        Args:
            experiment_name: Name of experiment to switch to

        Example:
            >>> monkey.switch_to("refactor")
        """
        experiments = self.experiments.list_experiments()

        # Find experiment
        experiment = None
        for exp in experiments:
            if exp.name == experiment_name:
                experiment = exp
                break

        if not experiment:
            raise ValueError(f"Experiment '{experiment_name}' not found")

        self.experiments.switch(experiment, save_changes=True)

    def keep_experiment(self, experiment_name: Optional[str] = None) -> None:
        """
        Keep an experiment by merging it back.

        This merges the experiment into its base branch.

        Args:
            experiment_name: Name of experiment (default: current experiment)

        Example:
            >>> monkey.keep_experiment()  # Keep current experiment
        """
        if experiment_name:
            experiments = self.experiments.list_experiments()
            experiment = None
            for exp in experiments:
                if exp.name == experiment_name:
                    experiment = exp
                    break
            if not experiment:
                raise ValueError(f"Experiment '{experiment_name}' not found")
        else:
            experiment = self.experiments.get_active_experiment()
            if not experiment:
                raise ValueError("No active experiment")

        self.experiments.merge(experiment, delete_after=True)

    def discard_experiment(
        self, experiment_name: Optional[str] = None, force: bool = True
    ) -> None:
        """
        Discard an experiment.

        Args:
            experiment_name: Name of experiment (default: current experiment)
            force: Delete even if not merged (default: True)

        Example:
            >>> monkey.discard_experiment("refactor")
        """
        if experiment_name:
            experiments = self.experiments.list_experiments()
            experiment = None
            for exp in experiments:
                if exp.name == experiment_name:
                    experiment = exp
                    break
            if not experiment:
                raise ValueError(f"Experiment '{experiment_name}' not found")
        else:
            experiment = self.experiments.get_active_experiment()
            if not experiment:
                raise ValueError("No active experiment")

        self.experiments.delete(experiment, force=force)

    def list_experiments(self) -> List[Dict]:
        """
        List all experiments.

        Returns:
            List of experiment dictionaries

        Example:
            >>> experiments = monkey.list_experiments()
            >>> for exp in experiments:
            ...     print(f"{exp['name']}: {exp['description']}")
        """
        experiments = self.experiments.list_experiments()
        return [to_dict(exp) for exp in experiments]

    def current_experiment(self) -> Optional[Dict]:
        """
        Get current experiment, if any.

        Returns:
            Current experiment dictionary or None

        Example:
            >>> exp = monkey.current_experiment()
            >>> if exp:
            ...     print(f"Currently in: {exp['name']}")
        """
        experiment = self.experiments.get_active_experiment()
        return to_dict(experiment) if experiment else None

    # === History API ===

    def what_happened(self, limit: int = 10) -> List[Dict]:
        """
        See what happened recently.

        Args:
            limit: How many entries to show (default: 10)

        Returns:
            List of history entry dictionaries

        Example:
            >>> history = monkey.what_happened()
            >>> for entry in history:
            ...     print(f"{entry['short_sha']}: {entry['message']}")
        """
        entries = self.history.get_history(limit)
        return [to_dict(entry) for entry in entries]

    def search(self, query: str, search_in: str = "message") -> List[Dict]:
        """
        Search project history.

        Args:
            query: What to search for
            search_in: Where to search ('message', 'author', or 'content')

        Returns:
            List of matching history entries

        Example:
            >>> results = monkey.search("bug fix")
            >>> results = monkey.search("Alice", search_in="author")
        """
        entries = self.history.search_history(query, search_in)
        return [to_dict(entry) for entry in entries]

    def show_changes(self, checkpoint_id: str) -> str:
        """
        Show what changed in a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID (short SHA or full)

        Returns:
            Diff as string

        Example:
            >>> diff = monkey.show_changes("a1b2c3d")
            >>> print(diff)
        """
        # Get the entry
        entries = self.history.get_history(limit=100)
        entry = None
        for e in entries:
            if e.sha.startswith(checkpoint_id) or e.short_sha == checkpoint_id:
                entry = e
                break

        if not entry:
            raise ValueError(f"Checkpoint '{checkpoint_id}' not found")

        return self.history.get_diff(entry)

    def compare(self, id1: str, id2: str) -> Dict:
        """
        Compare two checkpoints.

        Args:
            id1: First checkpoint ID
            id2: Second checkpoint ID

        Returns:
            Dictionary with 'files' and 'diff'

        Example:
            >>> comparison = monkey.compare("a1b2c3d", "e4f5g6h")
            >>> print(f"Changed {len(comparison['files'])} files")
        """
        file_changes, diff = self.history.compare_commits(id1, id2)
        return {
            "files": [to_dict(fc) for fc in file_changes],
            "diff": diff,
        }


# Convenience functions for quick access


def save(message: str, repo_path: Optional[Path] = None) -> Dict:
    """Quick save function."""
    monkey = BranchMonkey(repo_path)
    return monkey.save(message)


def undo(repo_path: Optional[Path] = None) -> None:
    """Quick undo function."""
    monkey = BranchMonkey(repo_path)
    monkey.undo()


def try_something(
    name: str, description: str = "", repo_path: Optional[Path] = None
) -> Dict:
    """Quick experiment creation."""
    monkey = BranchMonkey(repo_path)
    return monkey.try_something(name, description)
