"""Experiment system - safe branching without the complexity."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import git
from git.exc import GitCommandError, InvalidGitRepositoryError


@dataclass
class Experiment:
    """An experiment - a safe place to try things out."""

    name: str
    description: str
    created: datetime
    is_active: bool = False
    base_branch: str = "main"
    commits_ahead: int = 0
    commits_behind: int = 0
    has_changes: bool = False

    @property
    def age(self) -> str:
        """Human-readable age of experiment."""
        delta = datetime.now() - self.created
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"

    @property
    def status(self) -> str:
        """Human-readable status."""
        if self.is_active:
            return "🔬 Active"
        elif self.has_changes:
            return "✏️  Modified"
        elif self.commits_ahead > 0:
            return f"↑ {self.commits_ahead} ahead"
        else:
            return "✓ Clean"


class ExperimentManager:
    """Manages experiments (branches) in your Git repository."""

    EXPERIMENT_PREFIX = "experiment/"

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize experiment manager.

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

    def create(
        self, name: str, description: str = "", base_branch: Optional[str] = None
    ) -> Experiment:
        """
        Create a new experiment.

        Args:
            name: Name of the experiment (will be prefixed with 'experiment/')
            description: What you're trying to do in this experiment
            base_branch: Branch to start from. If None, uses current branch.

        Returns:
            Created experiment

        Raises:
            GitCommandError: If experiment already exists or creation fails
        """
        # Sanitize name
        clean_name = name.lower().replace(" ", "-")
        branch_name = f"{self.EXPERIMENT_PREFIX}{clean_name}"

        # Check if already exists
        if branch_name in [b.name for b in self.repo.branches]:
            raise GitCommandError(
                "git branch",
                f"Experiment '{name}' already exists. Choose a different name.",
            )

        # Get base branch
        if base_branch is None:
            base_branch = self.repo.active_branch.name
        else:
            if base_branch not in [b.name for b in self.repo.branches]:
                raise GitCommandError(
                    "git branch", f"Base branch '{base_branch}' not found."
                )

        # Create branch
        try:
            new_branch = self.repo.create_head(branch_name, base_branch)
            new_branch.checkout()

            # Store description in branch config
            if description:
                self.repo.config_writer().set_value(
                    f'branch "{branch_name}"', "description", description
                ).release()

            return Experiment(
                name=clean_name,
                description=description,
                created=datetime.now(),
                is_active=True,
                base_branch=base_branch,
            )
        except Exception as e:
            raise GitCommandError("git branch", f"Failed to create experiment: {e}")

    def switch(self, experiment: Experiment, save_changes: bool = True) -> None:
        """
        Switch to an experiment.

        Args:
            experiment: Experiment to switch to
            save_changes: If True, saves current changes before switching

        Raises:
            GitCommandError: If switch fails
        """
        branch_name = f"{self.EXPERIMENT_PREFIX}{experiment.name}"

        # Check if branch exists
        if branch_name not in [b.name for b in self.repo.branches]:
            raise GitCommandError(
                "git checkout", f"Experiment '{experiment.name}' not found."
            )

        # Save changes if requested
        if save_changes and self.repo.is_dirty():
            self.repo.git.stash("push", "-m", f"Auto-save before switching to {experiment.name}")

        # Switch branch
        try:
            self.repo.git.checkout(branch_name)
        except Exception as e:
            raise GitCommandError("git checkout", f"Failed to switch: {e}")

    def list_experiments(self) -> List[Experiment]:
        """
        List all experiments.

        Returns:
            List of experiments
        """
        experiments = []
        active_branch = self.repo.active_branch.name

        for branch in self.repo.branches:
            # Only include experiment branches
            if not branch.name.startswith(self.EXPERIMENT_PREFIX):
                continue

            # Extract experiment name
            exp_name = branch.name[len(self.EXPERIMENT_PREFIX) :]

            # Get description from config
            try:
                description = (
                    self.repo.config_reader()
                    .get_value(f'branch "{branch.name}"', "description", default="")
                )
            except Exception:
                description = ""

            # Get creation time from first commit in branch
            try:
                # This is approximate - gets the commit time
                created = datetime.fromtimestamp(branch.commit.committed_date)
            except Exception:
                created = datetime.now()

            # Check if active
            is_active = branch.name == active_branch

            # Get commits ahead/behind compared to base
            commits_ahead = 0
            commits_behind = 0
            base_branch = "main"

            try:
                # Try to find base branch from config or default to main
                base_branch = (
                    self.repo.config_reader()
                    .get_value(f'branch "{branch.name}"', "base", default="main")
                )

                # Count commits ahead/behind
                if base_branch in [b.name for b in self.repo.branches]:
                    ahead_behind = self.repo.git.rev_list(
                        "--left-right", "--count", f"{base_branch}...{branch.name}"
                    ).split()
                    if len(ahead_behind) == 2:
                        commits_behind = int(ahead_behind[0])
                        commits_ahead = int(ahead_behind[1])
            except Exception:
                pass

            # Check for uncommitted changes (only if active)
            has_changes = is_active and self.repo.is_dirty()

            experiments.append(
                Experiment(
                    name=exp_name,
                    description=description,
                    created=created,
                    is_active=is_active,
                    base_branch=base_branch,
                    commits_ahead=commits_ahead,
                    commits_behind=commits_behind,
                    has_changes=has_changes,
                )
            )

        # Sort by created time, newest first
        experiments.sort(key=lambda e: e.created, reverse=True)

        return experiments

    def get_active_experiment(self) -> Optional[Experiment]:
        """Get currently active experiment, if any."""
        experiments = self.list_experiments()
        for exp in experiments:
            if exp.is_active:
                return exp
        return None

    def merge(self, experiment: Experiment, delete_after: bool = True) -> None:
        """
        Merge experiment back to its base branch.

        Args:
            experiment: Experiment to merge
            delete_after: If True, deletes the experiment branch after merging

        Raises:
            GitCommandError: If merge fails
        """
        branch_name = f"{self.EXPERIMENT_PREFIX}{experiment.name}"

        # Switch to base branch
        try:
            self.repo.git.checkout(experiment.base_branch)
        except Exception as e:
            raise GitCommandError(
                "git checkout", f"Failed to switch to base branch: {e}"
            )

        # Merge experiment
        try:
            self.repo.git.merge(branch_name, "--no-ff", "-m",
                              f"Merge experiment: {experiment.name}")
        except Exception as e:
            # Abort merge on failure
            try:
                self.repo.git.merge("--abort")
            except Exception:
                pass
            raise GitCommandError(
                "git merge",
                f"Failed to merge. You may have conflicts. {e}"
            )

        # Delete branch if requested
        if delete_after:
            try:
                self.repo.delete_head(branch_name, force=True)
            except Exception as e:
                # Don't fail if we can't delete
                print(f"Warning: Could not delete experiment branch: {e}")

    def delete(self, experiment: Experiment, force: bool = False) -> None:
        """
        Delete an experiment.

        Args:
            experiment: Experiment to delete
            force: If True, deletes even if not merged

        Raises:
            GitCommandError: If deletion fails
        """
        branch_name = f"{self.EXPERIMENT_PREFIX}{experiment.name}"

        # Can't delete active branch
        if experiment.is_active:
            raise GitCommandError(
                "git branch",
                f"Cannot delete active experiment. Switch to another branch first.",
            )

        # Delete branch
        try:
            self.repo.delete_head(branch_name, force=force)
        except Exception as e:
            raise GitCommandError("git branch", f"Failed to delete experiment: {e}")

    def rename(self, experiment: Experiment, new_name: str) -> Experiment:
        """
        Rename an experiment.

        Args:
            experiment: Experiment to rename
            new_name: New name for the experiment

        Returns:
            Updated experiment

        Raises:
            GitCommandError: If rename fails
        """
        old_branch_name = f"{self.EXPERIMENT_PREFIX}{experiment.name}"
        clean_name = new_name.lower().replace(" ", "-")
        new_branch_name = f"{self.EXPERIMENT_PREFIX}{clean_name}"

        # Check if new name already exists
        if new_branch_name in [b.name for b in self.repo.branches]:
            raise GitCommandError(
                "git branch",
                f"Experiment '{new_name}' already exists. Choose a different name.",
            )

        # Rename branch
        try:
            branch = self.repo.heads[old_branch_name]
            branch.rename(new_branch_name)

            # Update experiment object
            experiment.name = clean_name

            return experiment
        except Exception as e:
            raise GitCommandError("git branch", f"Failed to rename experiment: {e}")
