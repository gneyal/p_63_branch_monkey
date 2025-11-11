"""Main TUI application."""

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane
from textual.binding import Binding

from ..core.checkpoint import CheckpointManager
from ..core.experiment import ExperimentManager
from ..core.history import HistoryNavigator
from .screens.timeline import TimelineScreen
from .screens.checkpoints import CheckpointsScreen
from .screens.experiments import ExperimentsScreen


class Welcome(Static):
    """Welcome message widget."""

    def compose(self) -> ComposeResult:
        yield Static(
            """[bold cyan]🐵 Branch Monkey[/bold cyan]

[dim]Git for humans - visual, safe, and beginner-friendly[/dim]

[yellow]Quick Start:[/yellow]
• [bold]Tab 1:[/bold] Timeline - See what happened
• [bold]Tab 2:[/bold] Checkpoints - Save points you can restore
• [bold]Tab 3:[/bold] Experiments - Safe places to try things

[dim]Press ? for help • Press q to quit[/dim]
"""
        )


class BranchMonkeyApp(App):
    """Main Branch Monkey TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }

    TabbedContent {
        height: 100%;
    }

    TabPane {
        padding: 1 2;
    }

    Welcome {
        padding: 2 4;
        border: solid $primary;
        background: $surface;
    }

    .help-text {
        color: $text-muted;
        text-style: italic;
    }

    .success {
        color: $success;
    }

    .warning {
        color: $warning;
    }

    .error {
        color: $error;
    }

    .highlight {
        background: $primary 20%;
        color: $text;
    }
    """

    TITLE = "Branch Monkey"
    SUB_TITLE = "Git for humans"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("1", "switch_tab('timeline')", "Timeline", show=False),
        Binding("2", "switch_tab('checkpoints')", "Checkpoints", show=False),
        Binding("3", "switch_tab('experiments')", "Experiments", show=False),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize app.

        Args:
            repo_path: Path to Git repository
        """
        super().__init__()
        self.repo_path = repo_path or Path.cwd()

        # Initialize managers
        try:
            self.checkpoint_mgr = CheckpointManager(self.repo_path)
            self.experiment_mgr = ExperimentManager(self.repo_path)
            self.history_nav = HistoryNavigator(self.repo_path)
            self.repo_initialized = True
        except Exception as e:
            self.repo_initialized = False
            self.error_message = str(e)

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        if not self.repo_initialized:
            yield Container(
                Static(
                    f"[bold red]Error:[/bold red] {self.error_message}\n\n"
                    "[yellow]Tip:[/yellow] Run 'git init' to create a Git repository first.",
                    classes="error",
                ),
            )
        else:
            yield TabbedContent(
                TabPane("Welcome", Welcome(), id="welcome"),
                TabPane(
                    "Timeline",
                    TimelineScreen(self.history_nav),
                    id="timeline",
                ),
                TabPane(
                    "Checkpoints",
                    CheckpointsScreen(self.checkpoint_mgr),
                    id="checkpoints",
                ),
                TabPane(
                    "Experiments",
                    ExperimentsScreen(self.experiment_mgr),
                    id="experiments",
                ),
            )

        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to a specific tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = tab_id

    def action_refresh(self) -> None:
        """Refresh current view."""
        # Get active tab and refresh it
        tabs = self.query_one(TabbedContent)
        active_pane = tabs.get_pane(tabs.active)
        if hasattr(active_pane, "refresh_data"):
            active_pane.refresh_data()

    def action_help(self) -> None:
        """Show help."""
        self.push_screen("help")


def run_tui(repo_path: Optional[Path] = None) -> None:
    """
    Run the Branch Monkey TUI.

    Args:
        repo_path: Path to Git repository
    """
    app = BranchMonkeyApp(repo_path)
    app.run()
