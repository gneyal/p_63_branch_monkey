"""Checkpoints screen - manage save points."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widgets import Static, Button, Input, ListView, ListItem, Label
from textual.binding import Binding
from textual.screen import ModalScreen
from rich.text import Text

from ...core.checkpoint import CheckpointManager, Checkpoint


class CheckpointListItem(ListItem):
    """List item for a checkpoint."""

    def __init__(self, checkpoint: Checkpoint):
        super().__init__()
        self.checkpoint = checkpoint

    def compose(self) -> ComposeResult:
        """Compose the list item."""
        # Create header
        header = Text()

        if self.checkpoint.is_temporary:
            header.append("⏱️  ", style="")
            header.append("TEMP ", style="bold yellow")
        else:
            header.append("✓ ", style="green")

        header.append(f"{self.checkpoint.short_id} ", style="bold cyan")
        header.append(f"({self.checkpoint.age})", style="dim")

        # Message
        message = Text(self.checkpoint.message)

        # Stats
        stats_parts = []
        if self.checkpoint.files_changed > 0:
            stats_parts.append(
                f"{self.checkpoint.files_changed} file{'s' if self.checkpoint.files_changed != 1 else ''}"
            )
        if self.checkpoint.insertions > 0:
            stats_parts.append(f"+{self.checkpoint.insertions}")
        if self.checkpoint.deletions > 0:
            stats_parts.append(f"-{self.checkpoint.deletions}")

        stats = Text(", ".join(stats_parts) if stats_parts else "No changes", style="dim")

        yield Static(header)
        yield Static(message)
        yield Static(stats)


class CreateCheckpointModal(ModalScreen):
    """Modal for creating a checkpoint."""

    def compose(self) -> ComposeResult:
        """Compose the modal."""
        yield Container(
            Static("[bold]Create Checkpoint[/bold]\n"),
            Input(placeholder="Description of what you're saving", id="checkpoint_message"),
            Horizontal(
                Button("Save", variant="primary", id="save_btn"),
                Button("Cancel", variant="default", id="cancel_btn"),
            ),
            Static("\n[dim]Enter: Save • Esc: Cancel[/dim]"),
            id="modal_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "save_btn":
            message_input = self.query_one("#checkpoint_message", Input)
            message = message_input.value.strip()
            if message:
                self.dismiss(message)
            else:
                self.app.notify("Please enter a description", severity="warning")
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        message = event.value.strip()
        if message:
            self.dismiss(message)


class CheckpointsScreen(Static):
    """Checkpoints screen for managing save points."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("n", "new_checkpoint", "New Checkpoint"),
        Binding("t", "new_temp", "Quick Save"),
        Binding("r", "restore", "Restore"),
        Binding("delete", "delete_checkpoint", "Delete"),
    ]

    def __init__(self, checkpoint_mgr: CheckpointManager):
        super().__init__()
        self.checkpoint_mgr = checkpoint_mgr
        self.checkpoints = []
        self.temp_checkpoints = []

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Static(
            "[bold]💾 Checkpoints[/bold]\n[dim]Save points you can restore to[/dim]\n"
        )

        yield Horizontal(
            Button("➕ New Checkpoint", variant="primary", id="new_checkpoint_btn"),
            Button("⏱️  Quick Save", variant="default", id="quick_save_btn"),
            id="button_bar",
        )

        yield Static("\n[bold yellow]Quick Saves (Temporary)[/bold yellow]")
        yield VerticalScroll(
            ListView(id="temp_list"),
            id="temp_scroll",
        )

        yield Static("\n[bold green]Checkpoints (Permanent)[/bold green]")
        yield VerticalScroll(
            ListView(id="checkpoint_list"),
            id="checkpoint_scroll",
        )

        yield Static(
            "\n[dim]n: New • t: Quick Save • r: Restore • Del: Delete[/dim]",
            id="help_text",
        )

    def on_mount(self) -> None:
        """When screen is mounted, load checkpoints."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh checkpoint data."""
        try:
            self.checkpoints = self.checkpoint_mgr.list_checkpoints(limit=20)
            self.temp_checkpoints = self.checkpoint_mgr.list_temporary()
            self._populate_lists()
        except Exception as e:
            self.notify(f"Error loading checkpoints: {e}", severity="error")

    def _populate_lists(self) -> None:
        """Populate checkpoint lists."""
        # Populate temporary checkpoints
        temp_list = self.query_one("#temp_list", ListView)
        temp_list.clear()

        if not self.temp_checkpoints:
            temp_list.append(
                ListItem(Label("[dim]No quick saves yet[/dim]"))
            )
        else:
            for checkpoint in self.temp_checkpoints:
                temp_list.append(CheckpointListItem(checkpoint))

        # Populate permanent checkpoints
        checkpoint_list = self.query_one("#checkpoint_list", ListView)
        checkpoint_list.clear()

        if not self.checkpoints:
            checkpoint_list.append(
                ListItem(Label("[dim]No checkpoints yet. Create one![/dim]"))
            )
        else:
            for checkpoint in self.checkpoints:
                checkpoint_list.append(CheckpointListItem(checkpoint))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "new_checkpoint_btn":
            self.action_new_checkpoint()
        elif event.button.id == "quick_save_btn":
            self.action_new_temp()

    def action_new_checkpoint(self) -> None:
        """Create a new checkpoint."""
        if not self.checkpoint_mgr.has_changes():
            self.notify("No changes to save", severity="warning")
            return

        def handle_result(message: str | None) -> None:
            if message:
                try:
                    checkpoint = self.checkpoint_mgr.create(message, include_untracked=True)
                    self.notify(
                        f"Checkpoint created: {checkpoint.short_id}", severity="success"
                    )
                    self.refresh_data()
                except Exception as e:
                    self.notify(f"Error creating checkpoint: {e}", severity="error")

        self.app.push_screen(CreateCheckpointModal(), handle_result)

    def action_new_temp(self) -> None:
        """Create a quick save (temporary checkpoint)."""
        if not self.checkpoint_mgr.has_changes():
            self.notify("No changes to save", severity="warning")
            return

        try:
            checkpoint = self.checkpoint_mgr.create_temporary("Quick save")
            self.notify("Quick save created", severity="success")
            self.refresh_data()
        except Exception as e:
            self.notify(f"Error creating quick save: {e}", severity="error")

    def action_restore(self) -> None:
        """Restore to selected checkpoint."""
        # Determine which list is focused
        try:
            temp_list = self.query_one("#temp_list", ListView)
            checkpoint_list = self.query_one("#checkpoint_list", ListView)

            # Check if temp list has focus
            if temp_list.has_focus and temp_list.index is not None:
                if temp_list.index < len(self.temp_checkpoints):
                    checkpoint = self.temp_checkpoints[temp_list.index]
                    self._restore_checkpoint(checkpoint)
                    return

            # Check checkpoint list
            if checkpoint_list.index is not None:
                if checkpoint_list.index < len(self.checkpoints):
                    checkpoint = self.checkpoints[checkpoint_list.index]
                    self._restore_checkpoint(checkpoint)
                    return

            self.notify("No checkpoint selected", severity="warning")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def _restore_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Restore to a checkpoint."""
        try:
            # Always keep changes for safety
            self.checkpoint_mgr.restore(checkpoint, keep_changes=True)
            self.notify(
                f"Restored to {checkpoint.short_id} (changes kept)", severity="success"
            )
            self.refresh_data()
        except Exception as e:
            self.notify(f"Error restoring: {e}", severity="error")

    def action_cursor_down(self) -> None:
        """Move cursor down in focused list."""
        # This is handled by ListView itself
        pass

    def action_cursor_up(self) -> None:
        """Move cursor up in focused list."""
        # This is handled by ListView itself
        pass
