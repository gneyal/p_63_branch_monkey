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
            return f'''Please analyze the architecture of the project at "{repo_path_str}" and generate a STRUCTURED JSON document for visualization as a flow diagram.

IMPORTANT: Output ONLY valid JSON, no markdown or explanation. Each element must have a unique "id" and "connects_to" array for the flow diagram.

ID NAMING CONVENTION:
- tech_stack: "tech_<name>" (e.g., "tech_python", "tech_react")
- endpoints: "ep_<method>_<path>" (e.g., "ep_get_users", "ep_post_auth_login")
- entities: "entity_<name>" (e.g., "entity_user", "entity_post")
- tables: "table_<name>" (e.g., "table_users", "table_posts")
- ui_components: "ui_<name>" (e.g., "ui_userlist", "ui_loginform")

The JSON must follow this exact schema:

{{
  "project_name": "Name of the project",
  "description": "Brief description of what the project does",
  "version": "Version if known",
  "tech_stack": [
    {{
      "id": "tech_python",
      "name": "Technology name (e.g., Python, React)",
      "category": "language|framework|database|tool|service",
      "version": "Version if known",
      "purpose": "What it's used for"
    }}
  ],
  "endpoints": [
    {{
      "id": "ep_get_users",
      "method": "GET|POST|PUT|PATCH|DELETE",
      "path": "/api/example",
      "description": "What this endpoint does",
      "params": [
        {{
          "name": "param_name",
          "type": "string|integer|boolean|object|array",
          "required": true,
          "description": "What this param is for",
          "location": "body|query|path|header"
        }}
      ],
      "response_type": "ReturnType",
      "response_description": "What the response contains",
      "auth_required": true,
      "tags": ["category"],
      "connects_to": ["entity_user"]
    }}
  ],
  "entities": [
    {{
      "id": "entity_user",
      "name": "EntityName",
      "description": "What this entity represents",
      "fields": [
        {{
          "name": "field_name",
          "type": "string|integer|boolean|datetime|etc",
          "description": "What this field is",
          "required": true,
          "default": null,
          "constraints": ["unique", "min:0", "max:100"]
        }}
      ],
      "relationships": ["has_many: OtherEntity", "belongs_to: Parent"],
      "file_path": "path/to/model.py",
      "connects_to": ["table_users", "entity_post"]
    }}
  ],
  "tables": [
    {{
      "id": "table_users",
      "name": "table_name",
      "description": "What this table stores",
      "columns": [
        {{
          "name": "column_name",
          "type": "INTEGER|TEXT|DATETIME|BOOLEAN|etc",
          "nullable": false,
          "primary_key": false,
          "foreign_key": "other_table.id or null",
          "default": "default value or null",
          "description": "What this column is"
        }}
      ],
      "indexes": [
        {{
          "name": "idx_name",
          "columns": ["col1", "col2"],
          "unique": true
        }}
      ],
      "relationships": ["Foreign key to users table"],
      "connects_to": ["table_posts"]
    }}
  ],
  "ui_components": [
    {{
      "id": "ui_userlist",
      "name": "ComponentName",
      "type": "page|component|layout|modal|form|widget",
      "description": "What this component does",
      "file_path": "src/components/Name.svelte",
      "props": ["prop1: Type", "prop2: Type"],
      "children": ["ChildComponent1", "ChildComponent2"],
      "routes": ["/path/to/page"],
      "connects_to": ["ui_usercard", "ep_get_users"]
    }}
  ],
  "notes": [
    "Important architectural decisions",
    "Authentication method used",
    "Deployment notes"
  ]
}}

INSTRUCTIONS:
1. Analyze all source files in the project
2. Extract ALL API endpoints (look for route decorators, handlers)
3. Extract ALL data models/entities (classes, schemas, types)
4. Extract ALL database tables (migrations, ORM models, SQL files)
5. Extract ALL UI components (React/Vue/Svelte components, pages)
6. List the complete tech stack with versions where possible
7. Include any important architectural notes
8. IMPORTANT: Set "connects_to" arrays to show relationships:
   - Endpoints connect to entities they use/return
   - Entities connect to their database tables and related entities
   - Tables connect to other tables via foreign keys
   - UI components connect to child components and endpoints they call

OUTPUT: Return ONLY the JSON object, no markdown code blocks, no explanations.'''

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
