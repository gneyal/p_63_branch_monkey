"""Context Library - Maintains repository context for AI assistants."""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


# Database path for context history
CONTEXT_DB = Path.home() / ".branch_monkey" / "context_history.db"

# Context types
CONTEXT_TYPES = ["codebase", "architecture", "prompts"]


@dataclass
class ContextEntry:
    """A single context summary entry."""
    id: int
    context_type: str
    content: str
    created_at: str
    repo_path: str


def init_context_db():
    """Initialize the context history database."""
    CONTEXT_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(CONTEXT_DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            repo_path TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_context_repo_type
        ON context_history(repo_path, context_type)
    ''')
    conn.commit()
    conn.close()


class ContextLibrary:
    """
    Manages AI-generated context summaries for a repository.

    Workflow:
    1. User requests a prompt for a specific context type
    2. User copies the prompt and runs it in their AI tool
    3. AI generates a summary
    4. User saves the summary back to Branch Monkey
    5. Historical summaries are stored and viewable by date
    """

    def __init__(self, repo_path: Path):
        """
        Initialize the context library.

        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = repo_path
        init_context_db()

    def get_prompt(self, context_type: str) -> str:
        """
        Get the prompt template for generating a context summary.

        Args:
            context_type: One of 'codebase', 'architecture', 'prompts'

        Returns:
            A prompt string that users can copy and run in their AI
        """
        repo_name = self.repo_path.name
        repo_path_str = str(self.repo_path.resolve())

        if context_type == "codebase":
            return f'''Please analyze the codebase at "{repo_path_str}" and generate a comprehensive summary.

Include the following sections:

## Overview
- Brief description of what this project does
- Main technologies/languages used

## Directory Structure
- Key directories and their purposes
- Important files and what they contain

## Key Components
- Main modules/packages
- Core functionality areas
- Entry points (main files, CLI, API endpoints)

## Dependencies
- Key external dependencies
- Internal module dependencies

## Code Patterns
- Design patterns used
- Code organization style
- Testing approach

Please format the output as Markdown. Be specific and reference actual file paths.

After generating the summary, save it by calling:
curl -X POST http://localhost:8081/api/context/save/codebase -H "Content-Type: application/json" -d '{{"content": "<YOUR_SUMMARY_HERE>"}}'
'''

        elif context_type == "architecture":
            return f'''Please analyze the architecture of the project at "{repo_path_str}" and generate a detailed summary.

Include the following sections:

## System Overview
- High-level architecture description
- Main components and their relationships

## Technology Stack
- Languages and frameworks
- Databases and storage
- External services/APIs

## Component Architecture
- Frontend architecture (if applicable)
- Backend architecture (if applicable)
- Data flow between components

## API Design
- API patterns used (REST, GraphQL, etc.)
- Key endpoints and their purposes
- Authentication/authorization approach

## Data Models
- Key data structures
- Database schema overview
- Data relationships

## Infrastructure
- Deployment architecture
- CI/CD pipeline
- Environment configuration

## Design Decisions
- Notable architectural decisions
- Trade-offs made
- Areas for improvement

Please format the output as Markdown. Reference specific files and code where relevant.

After generating the summary, save it by calling:
curl -X POST http://localhost:8081/api/context/save/architecture -H "Content-Type: application/json" -d '{{"content": "<YOUR_SUMMARY_HERE>"}}'
'''

        elif context_type == "prompts":
            return f'''Please analyze the AI prompts that have been used in the project at "{repo_path_str}".

Look for:
1. Any .prompts files or prompt templates
2. AI-related configuration files
3. Comments mentioning AI/LLM usage
4. Prompt strings in the code

Generate a summary including:

## Prompt Inventory
- List of prompts found and their purposes
- Where each prompt is used

## Prompt Patterns
- Common prompt structures
- Variables/templates used
- Best practices observed

## AI Integration Points
- Where AI is used in the application
- Input/output handling
- Error handling for AI calls

## Recommendations
- Prompt improvements
- Missing prompts that might be useful
- Documentation needs

Please format the output as Markdown.

After generating the summary, save it by calling:
curl -X POST http://localhost:8081/api/context/save/prompts -H "Content-Type: application/json" -d '{{"content": "<YOUR_SUMMARY_HERE>"}}'
'''

        else:
            raise ValueError(f"Unknown context type: {context_type}. Must be one of: {CONTEXT_TYPES}")

    def save_summary(self, context_type: str, content: str) -> ContextEntry:
        """
        Save an AI-generated summary to the history.

        Args:
            context_type: One of 'codebase', 'architecture', 'prompts'
            content: The summary content to save

        Returns:
            The created ContextEntry
        """
        if context_type not in CONTEXT_TYPES:
            raise ValueError(f"Unknown context type: {context_type}. Must be one of: {CONTEXT_TYPES}")

        created_at = datetime.now().isoformat()
        repo_path_str = str(self.repo_path.resolve())

        conn = sqlite3.connect(CONTEXT_DB)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO context_history (context_type, content, created_at, repo_path)
            VALUES (?, ?, ?, ?)
            """,
            (context_type, content, created_at, repo_path_str)
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return ContextEntry(
            id=entry_id,
            context_type=context_type,
            content=content,
            created_at=created_at,
            repo_path=repo_path_str
        )

    def get_history(self, context_type: str, limit: int = 50) -> List[Dict]:
        """
        Get historical summaries for a context type.

        Args:
            context_type: One of 'codebase', 'architecture', 'prompts'
            limit: Maximum number of entries to return

        Returns:
            List of summary entries (most recent first)
        """
        if context_type not in CONTEXT_TYPES:
            raise ValueError(f"Unknown context type: {context_type}. Must be one of: {CONTEXT_TYPES}")

        repo_path_str = str(self.repo_path.resolve())

        conn = sqlite3.connect(CONTEXT_DB)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, context_type, content, created_at, repo_path
            FROM context_history
            WHERE repo_path = ? AND context_type = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (repo_path_str, context_type, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "context_type": row[1],
                "content": row[2],
                "preview": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                "created_at": row[3],
                "repo_path": row[4]
            }
            for row in rows
        ]

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """
        Get a specific context entry by ID.

        Args:
            entry_id: The entry ID

        Returns:
            The entry dict or None if not found
        """
        conn = sqlite3.connect(CONTEXT_DB)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, context_type, content, created_at, repo_path
            FROM context_history
            WHERE id = ?
            """,
            (entry_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "context_type": row[1],
                "content": row[2],
                "created_at": row[3],
                "repo_path": row[4]
            }
        return None

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a context entry.

        Args:
            entry_id: The entry ID to delete

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(CONTEXT_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM context_history WHERE id = ?", (entry_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def get_latest(self, context_type: str) -> Optional[Dict]:
        """
        Get the most recent summary for a context type.

        Args:
            context_type: One of 'codebase', 'architecture', 'prompts'

        Returns:
            The latest entry or None
        """
        history = self.get_history(context_type, limit=1)
        return history[0] if history else None

    def get_all_latest(self) -> Dict[str, Optional[Dict]]:
        """
        Get the latest summary for all context types.

        Returns:
            Dict mapping context_type to latest entry (or None)
        """
        return {
            context_type: self.get_latest(context_type)
            for context_type in CONTEXT_TYPES
        }

    def get_counts(self) -> Dict[str, int]:
        """
        Get counts of summaries for each context type.

        Returns:
            Dict mapping context_type to count
        """
        repo_path_str = str(self.repo_path.resolve())

        conn = sqlite3.connect(CONTEXT_DB)
        cursor = conn.cursor()

        counts = {}
        for context_type in CONTEXT_TYPES:
            cursor.execute(
                """
                SELECT COUNT(*) FROM context_history
                WHERE repo_path = ? AND context_type = ?
                """,
                (repo_path_str, context_type)
            )
            counts[context_type] = cursor.fetchone()[0]

        conn.close()
        return counts
