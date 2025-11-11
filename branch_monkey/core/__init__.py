"""Core Git abstraction modules."""

from .checkpoint import CheckpointManager, Checkpoint
from .experiment import ExperimentManager, Experiment
from .history import HistoryNavigator, HistoryEntry

__all__ = [
    "CheckpointManager",
    "Checkpoint",
    "ExperimentManager",
    "Experiment",
    "HistoryNavigator",
    "HistoryEntry",
]
