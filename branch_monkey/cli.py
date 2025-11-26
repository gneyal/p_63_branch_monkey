"""Command-line interface for Branch Monkey."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .api import BranchMonkey
from .tui.app import run_tui

app = typer.Typer(
    name="monkey",
    help="Branch Monkey - Git for humans",
    add_completion=False,
)

console = Console()


@app.command()
def tui(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    )
):
    """
    Launch the interactive TUI.

    This is the main visual interface with all features.
    """
    run_tui(path)


@app.command()
def save(
    message: str = typer.Argument(..., help="Description of what you're saving"),
    untracked: bool = typer.Option(
        True, "--untracked/--no-untracked", help="Include new files"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Save current work as a checkpoint.

    Example:
        monkey save "Before trying refactor"
    """
    try:
        monkey = BranchMonkey(path)
        checkpoint = monkey.save(message, include_untracked=untracked)
        console.print(
            f"[green]✓[/green] Checkpoint created: [cyan]{checkpoint['short_id']}[/cyan]"
        )
        console.print(f"[dim]  {checkpoint['message']}[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def quick(
    message: str = typer.Option("Quick save", "--message", "-m", help="Save message"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Quick save (temporary checkpoint).

    Example:
        monkey quick
        monkey quick -m "Before pulling"
    """
    try:
        monkey = BranchMonkey(path)
        checkpoint = monkey.quick_save(message)
        console.print(f"[yellow]⏱️ [/yellow] Quick save created")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def undo(
    keep: bool = typer.Option(
        True, "--keep/--discard", help="Keep current changes"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Go back to previous checkpoint.

    Example:
        monkey undo
        monkey undo --discard  # Discard current changes
    """
    try:
        monkey = BranchMonkey(path)
        monkey.undo(keep_changes=keep)
        console.print("[green]✓[/green] Restored to previous checkpoint")
        if keep:
            console.print("[dim]  (Your current changes are kept)[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def restore(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to restore"),
    keep: bool = typer.Option(
        True, "--keep/--discard", help="Keep current changes"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Restore to a specific checkpoint.

    Example:
        monkey restore a1b2c3d
    """
    try:
        monkey = BranchMonkey(path)
        monkey.restore(checkpoint_id, keep_changes=keep)
        console.print(
            f"[green]✓[/green] Restored to checkpoint [cyan]{checkpoint_id}[/cyan]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of entries to show"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Show recent history.

    Example:
        monkey history
        monkey history -n 20
    """
    try:
        monkey = BranchMonkey(path)
        entries = monkey.what_happened(limit)

        if not entries:
            console.print("[dim]No history yet[/dim]")
            return

        table = Table(title="Recent History", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Age", style="dim")
        table.add_column("Author", style="yellow")
        table.add_column("Message")

        for entry in entries:
            table.add_row(
                entry["short_sha"],
                entry["age"],
                entry["author"],
                entry["message"].split("\n")[0][:60],
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def try_it(
    name: str = typer.Argument(..., help="Experiment name"),
    description: str = typer.Option("", "--desc", "-d", help="What you're trying"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Start a new experiment.

    Example:
        monkey try refactor -d "Trying new architecture"
    """
    try:
        monkey = BranchMonkey(path)
        experiment = monkey.try_something(name, description)
        console.print(
            f"[green]🔬[/green] Experiment [cyan]'{experiment['name']}'[/cyan] created and activated"
        )
        if description:
            console.print(f"[dim]  {description}[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def switch(
    name: str = typer.Argument(..., help="Experiment name to switch to"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Switch to an experiment.

    Example:
        monkey switch refactor
    """
    try:
        monkey = BranchMonkey(path)
        monkey.switch_to(name)
        console.print(f"[green]✓[/green] Switched to experiment [cyan]'{name}'[/cyan]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def keep(
    name: Optional[str] = typer.Argument(None, help="Experiment name (default: current)"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Keep an experiment (merge it).

    Example:
        monkey keep  # Keep current experiment
        monkey keep refactor
    """
    try:
        monkey = BranchMonkey(path)
        monkey.keep_experiment(name)
        console.print(
            f"[green]✓[/green] Experiment merged successfully"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def discard(
    name: Optional[str] = typer.Argument(None, help="Experiment name (default: current)"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Discard an experiment.

    Example:
        monkey discard  # Discard current experiment
        monkey discard refactor
    """
    try:
        monkey = BranchMonkey(path)
        monkey.discard_experiment(name)
        console.print(f"[yellow]✗[/yellow] Experiment discarded")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def experiments(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    List all experiments.

    Example:
        monkey experiments
    """
    try:
        monkey = BranchMonkey(path)
        exps = monkey.list_experiments()

        if not exps:
            console.print("[dim]No experiments yet. Try: monkey try <name>[/dim]")
            return

        table = Table(title="Experiments", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Status")
        table.add_column("Description")
        table.add_column("Age", style="dim")

        for exp in exps:
            status = "🔬 Active" if exp["is_active"] else "⚗️  Inactive"
            table.add_row(
                exp["name"],
                status,
                exp["description"] or "[dim]No description[/dim]",
                exp["age"],
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def checkpoints(
    limit: int = typer.Option(10, "--limit", "-n", help="Number to show"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    List checkpoints.

    Example:
        monkey checkpoints
        monkey checkpoints -n 20
    """
    try:
        monkey = BranchMonkey(path)
        saves = monkey.list_saves(limit)

        if not saves:
            console.print("[dim]No checkpoints yet. Try: monkey save <message>[/dim]")
            return

        table = Table(title="Checkpoints", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Age", style="dim")
        table.add_column("Message")
        table.add_column("Changes", style="dim")

        for save in saves:
            changes = f"{save['files_changed']} files"
            if save['insertions'] > 0 or save['deletions'] > 0:
                changes += f", +{save['insertions']} -{save['deletions']}"

            table.add_row(
                save["short_id"],
                save["age"],
                save["message"][:60],
                changes,
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    where: str = typer.Option(
        "message", "--where", "-w", help="Where to search (message/author/content)"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Search history.

    Example:
        monkey search "bug fix"
        monkey search Alice -w author
    """
    try:
        monkey = BranchMonkey(path)
        results = monkey.search(query, search_in=where)

        if not results:
            console.print(f"[dim]No results for '{query}'[/dim]")
            return

        console.print(f"Found {len(results)} result(s):\n")

        for entry in results:
            console.print(
                f"[cyan]{entry['short_sha']}[/cyan] "
                f"[dim]({entry['age']})[/dim] "
                f"[yellow]{entry['author']}[/yellow]"
            )
            console.print(f"  {entry['message'].split(chr(10))[0]}")
            console.print()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def diff(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to show diff for"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Show changes in a checkpoint.

    Example:
        monkey diff a1b2c3d
    """
    try:
        monkey = BranchMonkey(path)
        changes = monkey.show_changes(checkpoint_id)
        console.print(changes)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to Git repository"
    ),
):
    """
    Show current status.

    Example:
        monkey status
    """
    try:
        monkey = BranchMonkey(path)

        # Check for changes
        has_changes = monkey.has_changes()

        # Get current experiment
        current_exp = monkey.current_experiment()

        # Get recent checkpoints
        recent = monkey.list_saves(limit=5)

        # Build status display
        status_text = Text()

        if current_exp:
            status_text.append("🔬 Experiment: ", style="bold")
            status_text.append(f"{current_exp['name']}\n", style="cyan")
            if current_exp['description']:
                status_text.append(f"   {current_exp['description']}\n", style="dim")
        else:
            status_text.append("📍 On main branch\n", style="dim")

        status_text.append("\n")

        if has_changes:
            status_text.append("✏️  You have unsaved changes\n", style="yellow")
            status_text.append("   Run 'monkey save <message>' to create a checkpoint\n", style="dim")
        else:
            status_text.append("✓ No unsaved changes\n", style="green")

        console.print(Panel(status_text, title="Status", border_style="blue"))

        if recent:
            console.print("\n[bold]Recent Checkpoints:[/bold]")
            for i, cp in enumerate(recent[:3]):
                console.print(
                    f"  {i+1}. [cyan]{cp['short_id']}[/cyan] [dim]({cp['age']})[/dim] {cp['message'][:50]}"
                )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def context(
    update: bool = typer.Option(
        False, "--update", "-u", help="Update all context files"
    ),
    codebase: bool = typer.Option(
        False, "--codebase", "-c", help="Update only codebase summary"
    ),
    architecture: bool = typer.Option(
        False, "--architecture", "-a", help="Update only architecture summary"
    ),
    prompts: bool = typer.Option(
        False, "--prompts", "-p", help="Update only prompts summary"
    ),
    show: Optional[str] = typer.Option(
        None, "--show", "-s", help="Show a specific context file"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", help="Path to Git repository"
    ),
):
    """
    Manage the .branch_monkey context library.

    The context library maintains summaries of your codebase, architecture,
    and AI prompts in the .branch_monkey directory.

    Examples:
        monkey context --update           # Update all context files
        monkey context --codebase         # Update only codebase summary
        monkey context --show codebase_summary.md  # Show a context file
        monkey context                    # Show context status
    """
    try:
        monkey = BranchMonkey(path)

        # Handle specific file updates
        if codebase:
            monkey.update_codebase_context()
            console.print("[green]✓[/green] Codebase summary updated")
            return

        if architecture:
            monkey.update_architecture_context()
            console.print("[green]✓[/green] Architecture summary updated")
            return

        if prompts:
            monkey.update_prompts_context()
            console.print("[green]✓[/green] Prompts summary updated")
            return

        # Handle show command
        if show:
            content = monkey.read_context_file(show)
            if content:
                console.print(Panel(content, title=show, border_style="blue"))
            else:
                console.print(f"[yellow]Context file '{show}' not found.[/yellow]")
                console.print("[dim]Run 'monkey context --update' to generate it.[/dim]")
            return

        # Handle update all
        if update:
            console.print("[dim]Updating context files...[/dim]")
            results = monkey.update_context()
            console.print(f"[green]✓[/green] Updated {len(results)} context files:")
            for file_name in results.keys():
                console.print(f"  • {file_name}")
            console.print(f"\n[dim]Files saved to: .branch_monkey/[/dim]")
            return

        # Default: show status
        status = monkey.get_context_status()

        table = Table(title=".branch_monkey Context Library", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Status")
        table.add_column("Last Updated", style="dim")
        table.add_column("Size", style="dim")

        for s in status:
            if s["exists"]:
                status_str = "[green]✓ exists[/green]"
                updated = s["last_updated"][:19] if s["last_updated"] else "-"
                size = f"{s['size_bytes']} bytes"
            else:
                status_str = "[yellow]✗ missing[/yellow]"
                updated = "-"
                size = "-"

            table.add_row(s["file_name"], status_str, updated, size)

        console.print(table)
        console.print("\n[dim]Run 'monkey context --update' to generate/update files[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit"
    ),
):
    """
    Branch Monkey - Git for humans.

    Run 'monkey tui' to launch the interactive interface.
    Run 'monkey --help' to see all commands.
    """
    if version:
        from . import __version__
        console.print(f"Branch Monkey v{__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        # No subcommand provided, show welcome and launch TUI
        console.print(
            Panel(
                "[bold cyan]🐵 Branch Monkey[/bold cyan]\n\n"
                "[dim]Git for humans - visual, safe, and beginner-friendly[/dim]\n\n"
                "Launching interactive interface...\n"
                "[dim]Press Ctrl+C to cancel[/dim]",
                border_style="cyan",
            )
        )
        try:
            run_tui()
        except KeyboardInterrupt:
            console.print("\n[dim]Cancelled[/dim]")
            raise typer.Exit()


if __name__ == "__main__":
    app()
