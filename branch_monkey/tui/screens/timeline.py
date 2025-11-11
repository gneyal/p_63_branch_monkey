"""Timeline screen - visual history."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Static, Input, ListView, ListItem, Label
from textual.binding import Binding
from rich.text import Text

from ...core.history import HistoryNavigator, HistoryEntry


class HistoryListItem(ListItem):
    """List item for a history entry."""

    def __init__(self, entry: HistoryEntry):
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        """Compose the list item."""
        # Create header line
        header = Text()
        header.append(f"{self.entry.short_sha} ", style="bold cyan")
        header.append(f"({self.entry.age}) ", style="dim")
        header.append(f"{self.entry.author}", style="yellow")

        if self.entry.branch:
            header.append(f" [{self.entry.branch}]", style="bold green")

        for tag in self.entry.tags:
            header.append(f" 🏷️  {tag}", style="bold magenta")

        if self.entry.is_merge:
            header.append(" [MERGE]", style="bold blue")

        # Message
        message = Text(self.entry.message.split("\n")[0])  # First line only

        # Stats
        stats = Text(self.entry.summary_stats, style="dim")

        # Files changed preview (first 3 files)
        files_preview = Text()
        for i, file_change in enumerate(self.entry.files_changed[:3]):
            if i > 0:
                files_preview.append(", ")
            files_preview.append(f"{file_change.icon} ", style="")
            files_preview.append(file_change.path, style="dim")

        if len(self.entry.files_changed) > 3:
            files_preview.append(
                f" ... +{len(self.entry.files_changed) - 3} more", style="dim italic"
            )

        yield Static(header)
        yield Static(message)
        yield Static(stats)
        if files_preview.plain:
            yield Static(files_preview)


class TimelineScreen(Static):
    """Timeline view showing project history."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "view_details", "View Details"),
        Binding("d", "view_diff", "View Diff"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, history_nav: HistoryNavigator):
        super().__init__()
        self.history_nav = history_nav
        self.entries = []

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Static("[bold]📜 Timeline[/bold]\n[dim]Project history[/dim]\n")
        yield Input(placeholder="Search history... (press / to focus)", id="search_input")
        yield VerticalScroll(
            ListView(id="history_list"),
            id="scroll_container",
        )
        yield Static(
            "[dim]↑/↓: Navigate • Enter: Details • d: Diff • /: Search[/dim]",
            id="help_text",
        )

    def on_mount(self) -> None:
        """When screen is mounted, load history."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh history data."""
        try:
            self.entries = self.history_nav.get_history(limit=50)
            self._populate_list()
        except Exception as e:
            self.notify(f"Error loading history: {e}", severity="error")

    def _populate_list(self) -> None:
        """Populate the history list."""
        list_view = self.query_one("#history_list", ListView)
        list_view.clear()

        if not self.entries:
            list_view.append(
                ListItem(Label("[dim]No history yet. Make some checkpoints![/dim]"))
            )
            return

        for entry in self.entries:
            list_view.append(HistoryListItem(entry))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input."""
        query = event.value.strip()
        if not query:
            self.refresh_data()
            return

        try:
            # Search in commit messages
            self.entries = self.history_nav.search_history(query, search_in="message")
            self._populate_list()

            if not self.entries:
                self.notify(f"No results for '{query}'", severity="warning")
        except Exception as e:
            self.notify(f"Search error: {e}", severity="error")

    def action_search(self) -> None:
        """Focus search input."""
        search = self.query_one("#search_input", Input)
        search.focus()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        list_view = self.query_one("#history_list", ListView)
        if list_view.index is not None and list_view.index < len(list_view) - 1:
            list_view.index += 1

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        list_view = self.query_one("#history_list", ListView)
        if list_view.index is not None and list_view.index > 0:
            list_view.index -= 1

    def action_view_details(self) -> None:
        """View details of selected entry."""
        list_view = self.query_one("#history_list", ListView)
        if list_view.index is not None and list_view.index < len(self.entries):
            entry = self.entries[list_view.index]
            self._show_details(entry)

    def action_view_diff(self) -> None:
        """View diff of selected entry."""
        list_view = self.query_one("#history_list", ListView)
        if list_view.index is not None and list_view.index < len(self.entries):
            entry = self.entries[list_view.index]
            self._show_diff(entry)

    def _show_details(self, entry: HistoryEntry) -> None:
        """Show detailed view of an entry."""
        details = f"""[bold cyan]{entry.short_sha}[/bold cyan] by {entry.author}
[dim]{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({entry.age})[/dim]

[bold]Message:[/bold]
{entry.message}

[bold]Changes:[/bold] {entry.summary_stats}

[bold]Files:[/bold]
"""
        for file_change in entry.files_changed:
            details += f"\n{file_change.icon} {file_change.summary}"

        self.app.push_screen(
            "detail",
            lambda: Container(
                Static(details),
                Static("\n[dim]Press ESC to go back[/dim]"),
            ),
        )

    def _show_diff(self, entry: HistoryEntry) -> None:
        """Show diff for an entry."""
        try:
            diff = self.history_nav.get_diff(entry)
            if not diff:
                self.notify("No diff available", severity="warning")
                return

            # Truncate if too long
            if len(diff) > 10000:
                diff = diff[:10000] + "\n\n[... truncated ...]"

            self.notify(f"Showing diff for {entry.short_sha}", severity="information")
            # TODO: Create a proper diff viewer screen
        except Exception as e:
            self.notify(f"Error getting diff: {e}", severity="error")
