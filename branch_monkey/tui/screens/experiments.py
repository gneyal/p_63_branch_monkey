"""Experiments screen - manage safe branches."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widgets import Static, Button, Input, ListView, ListItem, Label
from textual.binding import Binding
from textual.screen import ModalScreen
from rich.text import Text

from ...core.experiment import ExperimentManager, Experiment


class ExperimentListItem(ListItem):
    """List item for an experiment."""

    def __init__(self, experiment: Experiment):
        super().__init__()
        self.experiment = experiment

    def compose(self) -> ComposeResult:
        """Compose the list item."""
        # Create header
        header = Text()

        # Status icon
        if self.experiment.is_active:
            header.append("🔬 ", style="")
        else:
            header.append("⚗️  ", style="")

        # Name
        header.append(f"{self.experiment.name} ", style="bold cyan")

        # Status
        header.append(f"{self.experiment.status}", style="")

        # Age
        header.append(f" ({self.experiment.age})", style="dim")

        # Description
        description = Text(
            self.experiment.description or "[dim]No description[/dim]"
        )

        # Details
        details_parts = []
        details_parts.append(f"Based on: {self.experiment.base_branch}")
        if self.experiment.commits_ahead > 0:
            details_parts.append(f"{self.experiment.commits_ahead} commits ahead")
        if self.experiment.commits_behind > 0:
            details_parts.append(f"{self.experiment.commits_behind} commits behind")

        details = Text(" • ".join(details_parts), style="dim")

        yield Static(header)
        yield Static(description)
        yield Static(details)


class CreateExperimentModal(ModalScreen):
    """Modal for creating an experiment."""

    def compose(self) -> ComposeResult:
        """Compose the modal."""
        yield Container(
            Static("[bold]Create Experiment[/bold]\n"),
            Input(placeholder="Experiment name (e.g., 'new-feature')", id="exp_name"),
            Input(placeholder="What are you trying? (optional)", id="exp_description"),
            Horizontal(
                Button("Create", variant="primary", id="create_btn"),
                Button("Cancel", variant="default", id="cancel_btn"),
            ),
            Static("\n[dim]Enter: Create • Esc: Cancel[/dim]"),
            id="modal_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "create_btn":
            name_input = self.query_one("#exp_name", Input)
            desc_input = self.query_one("#exp_description", Input)

            name = name_input.value.strip()
            description = desc_input.value.strip()

            if name:
                self.dismiss((name, description))
            else:
                self.app.notify("Please enter a name", severity="warning")
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        if event.input.id == "exp_name":
            # Focus description
            desc_input = self.query_one("#exp_description", Input)
            desc_input.focus()
        elif event.input.id == "exp_description":
            # Submit
            name_input = self.query_one("#exp_name", Input)
            name = name_input.value.strip()
            description = event.value.strip()
            if name:
                self.dismiss((name, description))


class ExperimentsScreen(Static):
    """Experiments screen for managing safe branches."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("n", "new_experiment", "New Experiment"),
        Binding("enter", "switch_experiment", "Switch"),
        Binding("m", "merge_experiment", "Merge"),
        Binding("delete", "delete_experiment", "Delete"),
    ]

    def __init__(self, experiment_mgr: ExperimentManager):
        super().__init__()
        self.experiment_mgr = experiment_mgr
        self.experiments = []

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Static(
            "[bold]🔬 Experiments[/bold]\n[dim]Safe places to try new things[/dim]\n"
        )

        yield Horizontal(
            Button("➕ New Experiment", variant="primary", id="new_exp_btn"),
            id="button_bar",
        )

        yield Static("\n[bold]Your Experiments[/bold]")
        yield VerticalScroll(
            ListView(id="experiment_list"),
            id="scroll_container",
        )

        yield Static(
            "\n[dim]n: New • Enter: Switch • m: Merge • Del: Delete[/dim]",
            id="help_text",
        )

    def on_mount(self) -> None:
        """When screen is mounted, load experiments."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh experiment data."""
        try:
            self.experiments = self.experiment_mgr.list_experiments()
            self._populate_list()
        except Exception as e:
            self.notify(f"Error loading experiments: {e}", severity="error")

    def _populate_list(self) -> None:
        """Populate experiment list."""
        exp_list = self.query_one("#experiment_list", ListView)
        exp_list.clear()

        if not self.experiments:
            exp_list.append(
                ListItem(
                    Label(
                        "[dim]No experiments yet. Create one to try something new![/dim]"
                    )
                )
            )
        else:
            for experiment in self.experiments:
                exp_list.append(ExperimentListItem(experiment))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "new_exp_btn":
            self.action_new_experiment()

    def action_new_experiment(self) -> None:
        """Create a new experiment."""

        def handle_result(result: tuple | None) -> None:
            if result:
                name, description = result
                try:
                    experiment = self.experiment_mgr.create(name, description)
                    self.notify(
                        f"Experiment '{experiment.name}' created and activated",
                        severity="success",
                    )
                    self.refresh_data()
                except Exception as e:
                    self.notify(f"Error creating experiment: {e}", severity="error")

        self.app.push_screen(CreateExperimentModal(), handle_result)

    def action_switch_experiment(self) -> None:
        """Switch to selected experiment."""
        exp_list = self.query_one("#experiment_list", ListView)

        if exp_list.index is not None and exp_list.index < len(self.experiments):
            experiment = self.experiments[exp_list.index]

            if experiment.is_active:
                self.notify("Already in this experiment", severity="information")
                return

            try:
                self.experiment_mgr.switch(experiment, save_changes=True)
                self.notify(
                    f"Switched to experiment '{experiment.name}'", severity="success"
                )
                self.refresh_data()
            except Exception as e:
                self.notify(f"Error switching: {e}", severity="error")
        else:
            self.notify("No experiment selected", severity="warning")

    def action_merge_experiment(self) -> None:
        """Merge selected experiment."""
        exp_list = self.query_one("#experiment_list", ListView)

        if exp_list.index is not None and exp_list.index < len(self.experiments):
            experiment = self.experiments[exp_list.index]

            if experiment.is_active:
                self.notify(
                    "Cannot merge active experiment. Switch to base branch first.",
                    severity="warning",
                )
                return

            try:
                self.experiment_mgr.merge(experiment, delete_after=True)
                self.notify(
                    f"Experiment '{experiment.name}' merged successfully",
                    severity="success",
                )
                self.refresh_data()
            except Exception as e:
                self.notify(f"Error merging: {e}", severity="error")
        else:
            self.notify("No experiment selected", severity="warning")

    def action_delete_experiment(self) -> None:
        """Delete selected experiment."""
        exp_list = self.query_one("#experiment_list", ListView)

        if exp_list.index is not None and exp_list.index < len(self.experiments):
            experiment = self.experiments[exp_list.index]

            if experiment.is_active:
                self.notify(
                    "Cannot delete active experiment. Switch to another first.",
                    severity="warning",
                )
                return

            try:
                self.experiment_mgr.delete(experiment, force=True)
                self.notify(
                    f"Experiment '{experiment.name}' deleted", severity="success"
                )
                self.refresh_data()
            except Exception as e:
                self.notify(f"Error deleting: {e}", severity="error")
        else:
            self.notify("No experiment selected", severity="warning")

    def action_cursor_down(self) -> None:
        """Move cursor down in list."""
        # Handled by ListView
        pass

    def action_cursor_up(self) -> None:
        """Move cursor up in list."""
        # Handled by ListView
        pass
