"""Horizontal graph screen - branches as rows, time flows left to right."""

from typing import Optional, List, Tuple
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal, Vertical
from textual.widgets import Static, Label, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen
from rich.text import Text
from rich.panel import Panel

from ...core.graph_horizontal import HorizontalGitGraph, CommitNode


class HorizontalGraphView(Static):
    """Display horizontal Git graph."""

    selected_branch_index = reactive(0)
    selected_commit_index = reactive(0)

    def __init__(self, graph_lines: List[str], branches_list: List[Tuple[str, CommitNode]]):
        super().__init__()
        self.graph_lines = graph_lines
        self.branches_list = branches_list

    def compose(self) -> ComposeResult:
        """Compose the graph view."""
        # Show graph
        graph_text = "\n".join(self.graph_lines)
        yield Static(graph_text, id="graph_display", classes="graph_content")

        # Show selected branch info
        yield Static("", id="selection_info", classes="info_panel")

    def on_mount(self) -> None:
        """Initial render."""
        self.update_selection_display()

    def watch_selected_branch_index(self, old: int, new: int) -> None:
        """React to branch selection changes."""
        self.update_selection_display()

    def watch_selected_commit_index(self, old: int, new: int) -> None:
        """React to commit selection changes."""
        self.update_selection_display()

    def update_selection_display(self) -> None:
        """Update the selection info display."""
        if not self.branches_list:
            return

        # Get current branch and commit
        if 0 <= self.selected_branch_index < len(self.branches_list):
            branch_name, latest_commit = self.branches_list[self.selected_branch_index]

            info_widget = self.query_one("#selection_info", Static)

            info_text = Text()
            info_text.append("\n")
            info_text.append(f"Branch: ", style="bold")
            info_text.append(f"{branch_name}", style="cyan")
            info_text.append(f" ({latest_commit.short_sha})\n", style="dim")
            info_text.append(f"{latest_commit.message[:60]}\n", style="")
            info_text.append(f"Author: {latest_commit.author} • {latest_commit.age}", style="dim")

            info_widget.update(info_text)

    def get_selected_branch(self) -> Optional[Tuple[str, CommitNode]]:
        """Get currently selected branch."""
        if 0 <= self.selected_branch_index < len(self.branches_list):
            return self.branches_list[self.selected_branch_index]
        return None

    def move_to_next_branch(self) -> None:
        """Move to next branch (Tab)."""
        if self.branches_list:
            self.selected_branch_index = (self.selected_branch_index + 1) % len(self.branches_list)

    def move_to_prev_branch(self) -> None:
        """Move to previous branch (Shift+Tab)."""
        if self.branches_list:
            self.selected_branch_index = (self.selected_branch_index - 1) % len(self.branches_list)


class HorizontalGraphScreen(Static):
    """Main horizontal graph screen."""

    BINDINGS = [
        Binding("up,k", "prev_branch", "↑ Branch", show=True),
        Binding("down,j", "next_branch", "↓ Branch", show=True),
        Binding("enter", "checkout", "Checkout", show=True),
        Binding("n", "new_checkpoint", "Save", show=True),
        Binding("e", "new_experiment", "Experiment", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def __init__(self, repo_path=None):
        super().__init__()
        self.graph = HorizontalGitGraph(repo_path)
        self.nodes = []
        self.branches = {}
        self.graph_view = None

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Static(
            "[bold cyan]🐵 Branch Monkey - Git Graph (Horizontal)[/bold cyan]\n"
            "[dim]↑/↓: Switch branches • ←/→: Switch tabs • Enter: Checkout[/dim]\n",
            id="header",
        )

        yield Container(id="graph_container")

        yield Static(
            "\n[dim]↑/↓: Switch branches • Enter: Checkout • n: Save • e: Experiment • r: Refresh[/dim]",
            id="help",
        )

    def on_mount(self) -> None:
        """When screen is mounted, build and display graph."""
        self.refresh_graph()

    def refresh_graph(self) -> None:
        """Rebuild and redisplay the graph."""
        try:
            # Build graph
            self.nodes, self.branches = self.graph.build_graph(limit=30)

            # Render graph
            graph_lines = self.graph.render_graph(self.nodes, self.branches)

            # Get branches list
            branches_list = self.graph.get_branches_list(self.branches)

            # Create graph view
            container = self.query_one("#graph_container", Container)
            container.remove_children()

            self.graph_view = HorizontalGraphView(graph_lines, branches_list)
            container.mount(self.graph_view)

            # Select current branch (HEAD)
            for i, (branch_name, commit) in enumerate(branches_list):
                if commit.is_head:
                    self.graph_view.selected_branch_index = i
                    break

        except Exception as e:
            self.notify(f"Error loading graph: {e}", severity="error")

    def action_next_branch(self) -> None:
        """Move to next branch (Tab)."""
        if self.graph_view:
            self.graph_view.move_to_next_branch()
            self.notify("Switched to next branch", severity="information")

    def action_prev_branch(self) -> None:
        """Move to previous branch (Shift+Tab)."""
        if self.graph_view:
            self.graph_view.move_to_prev_branch()
            self.notify("Switched to previous branch", severity="information")

    def action_move_left(self) -> None:
        """Move left in timeline (older commits)."""
        # TODO: Implement commit navigation within branch
        self.notify("Navigate to older commits - TODO", severity="information")

    def action_move_right(self) -> None:
        """Move right in timeline (newer commits)."""
        # TODO: Implement commit navigation within branch
        self.notify("Navigate to newer commits - TODO", severity="information")

    def action_checkout(self) -> None:
        """Checkout selected branch."""
        if not self.graph_view:
            return

        selection = self.graph_view.get_selected_branch()
        if not selection:
            self.notify("No branch selected", severity="warning")
            return

        branch_name, commit = selection

        # Confirm
        msg = (
            f"Checkout branch: {branch_name}\n"
            f"Latest commit: {commit.short_sha}\n"
            f"{commit.message[:60]}"
        )

        def handle_confirm(result):
            if result:
                confirmed, branch_name = result
                if confirmed:
                    try:
                        self.graph.repo.git.checkout(branch_name)
                        self.notify(
                            f"Checked out: {branch_name}", severity="success"
                        )
                        self.refresh_graph()
                    except Exception as e:
                        self.notify(f"Error: {e}", severity="error")

        self.app.push_screen(
            ConfirmCheckoutScreen(msg, branch_name), handle_confirm
        )

    def action_new_checkpoint(self) -> None:
        """Create new checkpoint."""
        self.notify("Save checkpoint - integrated with other screens", severity="information")

    def action_new_experiment(self) -> None:
        """Create new experiment."""
        self.notify("Create experiment - integrated with other screens", severity="information")

    def action_refresh(self) -> None:
        """Refresh the graph."""
        self.refresh_graph()
        self.notify("Graph refreshed", severity="success")


class ConfirmCheckoutScreen(ModalScreen):
    """Confirmation dialog for checkout."""

    def __init__(self, message: str, branch_name: str):
        super().__init__()
        self.message = message
        self.branch_name = branch_name

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog."""
        yield Container(
            Static(self.message, classes="confirm_message"),
            Horizontal(
                Button("Checkout", variant="primary", id="yes"),
                Button("Cancel", variant="default", id="cancel"),
                classes="button_row",
            ),
            id="confirm_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes":
            self.dismiss((True, self.branch_name))
        else:
            self.dismiss(None)
