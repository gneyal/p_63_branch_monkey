"""
Branch Monkey MCP Server

This module provides an MCP (Model Context Protocol) server that exposes
Branch Monkey functionality to AI assistants like Claude Code.

Usage:
    Run as MCP server:
        python -m branch_monkey.mcp_server

    Or add to Claude Code config (~/.claude/claude_desktop_config.json):
        {
            "mcpServers": {
                "branch-monkey": {
                    "command": "python",
                    "args": ["-m", "branch_monkey.mcp_server"]
                }
            }
        }
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Any

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from .api import BranchMonkey
from .core.context import CONTEXT_TYPES

# Create the MCP server
server = Server("branch-monkey")


def get_repo_path() -> Path:
    """Get the current repository path from environment or cwd."""
    return Path(os.environ.get("MONKEY_REPO_PATH", os.getcwd()))


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Branch Monkey tools."""
    return [
        Tool(
            name="monkey_ui",
            description="Start the Branch Monkey web UI for visual git management. Opens a browser with the commit tree visualization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "port": {
                        "type": "integer",
                        "description": "Port to run the server on (default: 8081)",
                        "default": 8081
                    }
                }
            }
        ),
        Tool(
            name="monkey_status",
            description="Get the current status of the repository including unsaved changes, current branch/experiment, and recent checkpoints.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="monkey_save",
            description="Save current work as a checkpoint (like a save point in a video game). This stages and commits all changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Description of what you're saving"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="monkey_undo",
            description="Go back to the previous checkpoint. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keep_changes": {
                        "type": "boolean",
                        "description": "Whether to keep current changes (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="monkey_experiment_start",
            description="Start a new experiment branch for trying something new without affecting main work.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the experiment (e.g., 'refactor', 'new-feature')"
                    },
                    "description": {
                        "type": "string",
                        "description": "What you're trying (optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="monkey_experiment_keep",
            description="Keep the current experiment by merging it into the base branch.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="monkey_experiment_discard",
            description="Discard the current experiment and return to the base branch.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="monkey_context_prompt",
            description="Get an AI prompt for generating a context summary. Copy this prompt, run it, then save the result with monkey_context_save.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context_type": {
                        "type": "string",
                        "enum": ["codebase", "architecture", "prompts"],
                        "description": "Type of context to generate: 'codebase' (file structure), 'architecture' (system design), or 'prompts' (AI prompts inventory)"
                    }
                },
                "required": ["context_type"]
            }
        ),
        Tool(
            name="monkey_context_save",
            description="Save an AI-generated context summary to the history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context_type": {
                        "type": "string",
                        "enum": ["codebase", "architecture", "prompts"],
                        "description": "Type of context being saved"
                    },
                    "content": {
                        "type": "string",
                        "description": "The AI-generated summary content to save"
                    }
                },
                "required": ["context_type", "content"]
            }
        ),
        Tool(
            name="monkey_context_latest",
            description="Get the most recent context summary for a given type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context_type": {
                        "type": "string",
                        "enum": ["codebase", "architecture", "prompts"],
                        "description": "Type of context to retrieve"
                    }
                },
                "required": ["context_type"]
            }
        ),
        Tool(
            name="monkey_history",
            description="Show recent commit history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of commits to show (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        repo_path = get_repo_path()
        monkey = BranchMonkey(repo_path)

        if name == "monkey_ui":
            port = arguments.get("port", 8081)
            # Start the server in the background
            subprocess.Popen(
                [sys.executable, "-c",
                 f"from branch_monkey.fastapi_server import run_server; run_server(port={port})"],
                cwd=str(repo_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return [TextContent(
                type="text",
                text=f"Branch Monkey UI starting at http://localhost:{port}\n\nThe web interface provides:\n- Visual commit tree\n- Experiment management\n- Context library\n- Checkpoint controls"
            )]

        elif name == "monkey_status":
            has_changes = monkey.has_changes()
            experiment = monkey.current_experiment()
            recent = monkey.list_saves(limit=3)

            status_lines = []
            if experiment:
                status_lines.append(f"🔬 In experiment: {experiment['name']}")
                if experiment.get('description'):
                    status_lines.append(f"   {experiment['description']}")
            else:
                status_lines.append("📍 On main branch")

            status_lines.append("")
            if has_changes:
                status_lines.append("✏️  You have unsaved changes")
            else:
                status_lines.append("✓ No unsaved changes")

            if recent:
                status_lines.append("\nRecent checkpoints:")
                for cp in recent:
                    status_lines.append(f"  • {cp['short_id']} ({cp['age']}): {cp['message'][:50]}")

            return [TextContent(type="text", text="\n".join(status_lines))]

        elif name == "monkey_save":
            message = arguments["message"]
            checkpoint = monkey.save(message)
            return [TextContent(
                type="text",
                text=f"✓ Checkpoint created: {checkpoint['short_id']}\n  {checkpoint['message']}"
            )]

        elif name == "monkey_undo":
            keep_changes = arguments.get("keep_changes", True)
            monkey.undo(keep_changes=keep_changes)
            msg = "✓ Restored to previous checkpoint"
            if keep_changes:
                msg += " (changes kept)"
            return [TextContent(type="text", text=msg)]

        elif name == "monkey_experiment_start":
            name_arg = arguments["name"]
            description = arguments.get("description", "")
            experiment = monkey.try_something(name_arg, description)
            return [TextContent(
                type="text",
                text=f"🔬 Experiment '{experiment['name']}' created and activated\n{description}"
            )]

        elif name == "monkey_experiment_keep":
            monkey.keep_experiment()
            return [TextContent(type="text", text="✓ Experiment merged successfully")]

        elif name == "monkey_experiment_discard":
            monkey.discard_experiment()
            return [TextContent(type="text", text="✗ Experiment discarded")]

        elif name == "monkey_context_prompt":
            context_type = arguments["context_type"]
            prompt = monkey.get_context_prompt(context_type)
            return [TextContent(
                type="text",
                text=f"# AI Prompt for {context_type.title()} Summary\n\nRun the following analysis, then save the result with monkey_context_save:\n\n---\n\n{prompt}"
            )]

        elif name == "monkey_context_save":
            context_type = arguments["context_type"]
            content = arguments["content"]
            entry = monkey.save_context_summary(context_type, content)
            return [TextContent(
                type="text",
                text=f"✓ {context_type.title()} summary saved (ID: {entry['id']})\n  Created: {entry['created_at']}"
            )]

        elif name == "monkey_context_latest":
            context_type = arguments["context_type"]
            entry = monkey.get_latest_context(context_type)
            if entry:
                return [TextContent(
                    type="text",
                    text=f"# Latest {context_type.title()} Summary\n\nCreated: {entry['created_at']}\n\n---\n\n{entry['content']}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"No {context_type} summary found. Use monkey_context_prompt to generate one."
                )]

        elif name == "monkey_history":
            limit = arguments.get("limit", 10)
            history = monkey.what_happened(limit)

            lines = ["# Recent History\n"]
            for entry in history:
                lines.append(f"• {entry['short_sha']} ({entry['age']}) - {entry['author']}")
                lines.append(f"  {entry['message'].split(chr(10))[0][:60]}")
                lines.append("")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
