"""Main graph screen - visual Git tree with navigation."""

from typing import Optional, List
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widgets import Static, Label, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen
from rich.text import Text
from rich.panel import Panel

from ...core.graph import GitGraph, CommitNode, GraphLine


class GraphView(VerticalScroll):
    """Scrollable graph view."""

    selected_index = reactive(0)

    def __init__(self, graph_lines: List[GraphLine]):
        super().__init__()
        self.graph_lines = graph_lines
        self.commit_indices = []  # Indices of lines that have commits

        # Build index of commit lines
        for i, line in enumerate(graph_lines):
            if line.is_commit_line and line.commit_node:
                self.commit_indices.append(i)

    def compose(self) -> ComposeResult:
        """Compose the graph view."""
        for i, line in enumerate(self.graph_lines):
            if line.is_commit_line and line.commit_node:
                # This is a commit line - make it selectable
                yield CommitLine(line, i, id=f"commit_{i}")
            else:
                # Regular connector line
                yield Static(line.text, classes="connector")

    def watch_selected_index(self, old_value: int, new_value: int) -> None:
        """React to selection changes."""
        # Update highlighting
        if 0 <= old_value < len(self.commit_indices):
            old_line_index = self.commit_indices[old_value]
            old_widget = self.query_one(f"#commit_{old_line_index}")
            old_widget.remove_class("selected")

        if 0 <= new_value < len(self.commit_indices):
            new_line_index = self.commit_indices[new_value]
            new_widget = self.query_one(f"#commit_{new_line_index}")
            new_widget.add_class("selected")
            new_widget.scroll_visible()

    def get_selected_commit(self) -> Optional[CommitNode]:
        """Get currently selected commit."""
        if 0 <= self.selected_index < len(self.commit_indices):
            line_index = self.commit_indices[self.selected_index]
            return self.graph_lines[line_index].commit_node
        return None

    def move_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1

    def move_down(self) -> None:
        """Move selection down."""
        if self.selected_index < len(self.commit_indices) - 1:
            self.selected_index += 1


class CommitLine(Static):
    """A single commit line that can be selected."""

    def __init__(self, graph_line: GraphLine, index: int, **kwargs):
        super().__init__(graph_line.text, **kwargs)
        self.graph_line = graph_line
        self.index = index


class GraphScreen(Static):
    """Main graph screen showing visual Git tree."""

    BINDINGS = [
        Binding("up,k", "cursor_up", "Up", show=False),
        Binding("down,j", "cursor_down", "Down", show=False),
        Binding("enter", "goto_commit", "Go to commit", show=True),
        Binding("n", "new_checkpoint", "New checkpoint", show=True),
        Binding("e", "new_experiment", "New experiment", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def __init__(self, repo_path=None):
        super().__init__()
        self.graph = GitGraph(repo_path)
        self.nodes = []
        self.graph_view = None

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Static(
            "[bold cyan]🐵 Branch Monkey - Git Graph[/bold cyan]\n"
            "[dim]Navigate with ↑/↓ arrows, Enter to jump to commit[/dim]\n",
            id="header",
        )

        # Will be populated in on_mount
        yield Container(id="graph_container")

        yield Static(
            "\n[dim]↑/↓: Navigate • Enter: Go to commit • n: New checkpoint • e: New experiment • r: Refresh[/dim]",
            id="help",
        )

    def on_mount(self) -> None:
        """When screen is mounted, build and display graph."""
        self.refresh_graph()

    def refresh_graph(self) -> None:
        """Rebuild and redisplay the graph."""
        try:
            # Build graph
            self.nodes = self.graph.build_graph(limit=50, all_branches=True)

            # Render graph
            graph_lines = self.graph.render_graph(self.nodes, width=120)

            # Create graph view
            container = self.query_one("#graph_container", Container)
            container.remove_children()

            self.graph_view = GraphView(graph_lines)
            container.mount(self.graph_view)

            # Select current HEAD if possible
            for i, node in enumerate(self.nodes):
                if node.is_head:
                    self.graph_view.selected_index = i
                    break

        except Exception as e:
            self.notify(f"Error loading graph: {e}", severity="error")

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        if self.graph_view:
            self.graph_view.move_up()
            self._update_info()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        if self.graph_view:
            self.graph_view.move_down()
            self._update_info()

    def action_goto_commit(self) -> None:
        """Go to (checkout) selected commit."""
        if not self.graph_view:
            return

        commit = self.graph_view.get_selected_commit()
        if not commit:
            self.notify("No commit selected", severity="warning")
            return

        # Ask for confirmation
        msg = f"Go to commit {commit.short_sha}?\n{commit.message[:60]}"
        self.app.push_screen(
            ConfirmScreen(msg, commit), self._handle_goto_commit
        )

    def _handle_goto_commit(self, result) -> None:
        """Handle goto commit confirmation."""
        if result:
            confirmed, commit = result
            if confirmed:
                try:
                    # Checkout the commit (detached HEAD)
                    self.graph.repo.git.checkout(commit.sha)
                    self.notify(
                        f"Switched to commit {commit.short_sha}", severity="success"
                    )
                    self.refresh_graph()
                except Exception as e:
                    self.notify(f"Error: {e}", severity="error")

    def action_new_checkpoint(self) -> None:
        """Create a new checkpoint."""
        self.notify("Create checkpoint - TODO", severity="information")

    def action_new_experiment(self) -> None:
        """Create a new experiment from selected commit."""
        self.notify("Create experiment - TODO", severity="information")

    def action_refresh(self) -> None:
        """Refresh the graph."""
        self.refresh_graph()
        self.notify("Graph refreshed", severity="success")

    def _update_info(self) -> None:
        """Update info panel with selected commit details."""
        if not self.graph_view:
            return

        commit = self.graph_view.get_selected_commit()
        if commit:
            # Could show more details in a side panel
            pass


class ConfirmScreen(ModalScreen):
    """Confirmation dialog."""

    def __init__(self, message: str, commit: CommitNode):
        super().__init__()
        self.message = message
        self.commit = commit

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog."""
        yield Container(
            Static(self.message, classes="confirm_message"),
            Horizontal(
                Button("Yes", variant="primary", id="yes"),
                Button("Cancel", variant="default", id="cancel"),
                classes="button_row",
            ),
            id="confirm_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes":
            self.dismiss((True, self.commit))
        else:
            self.dismiss(None)
