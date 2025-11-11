#!/usr/bin/env python
"""Test TUI components."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane

from branch_monkey.tui.screens.graph import GraphScreen


class TestApp(App):
    """Simple test app."""

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            with TabPane("Test", id="test"):
                yield Static("Hello World")

            with TabPane("Graph", id="graph"):
                yield GraphScreen()

        yield Footer()


if __name__ == "__main__":
    app = TestApp()
    app.run()
