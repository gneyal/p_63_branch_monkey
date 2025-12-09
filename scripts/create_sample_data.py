#!/usr/bin/env python3
"""
Create sample data for Branch Monkey demo.
This populates the .branch_monkey/data.db with realistic demo data.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

# Sample data directory - create in the example folder
EXAMPLE_DIR = Path(__file__).parent.parent / "example_project" / ".branch_monkey"


def init_database(db_path: Path):
    """Initialize database with schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create prompt_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            total_tokens INTEGER NOT NULL DEFAULT 0,
            cost REAL NOT NULL DEFAULT 0.0,
            duration REAL NOT NULL DEFAULT 0.0,
            prompt_preview TEXT,
            response_preview TEXT,
            status TEXT NOT NULL DEFAULT 'success',
            error_message TEXT,
            session_id TEXT,
            user TEXT,
            tool_name TEXT,
            metadata TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_logs_timestamp ON prompt_logs(timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_logs_session ON prompt_logs(session_id)")

    # Create context_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_type ON context_history(context_type, created_at DESC)")

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'todo',
            priority INTEGER NOT NULL DEFAULT 0,
            sprint TEXT DEFAULT 'backlog',
            sort_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create versions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    return conn


def create_sample_prompts(cursor):
    """Create realistic sample prompt logs."""

    models = [
        ("anthropic", "claude-opus-4-5-20251101", 15.0, 75.0),
        ("anthropic", "claude-sonnet-4-20250514", 3.0, 15.0),
        ("anthropic", "claude-3-5-haiku-20241022", 0.8, 4.0),
    ]

    prompts_data = [
        ("Analyze the authentication flow in this codebase and suggest improvements",
         "The authentication flow uses JWT tokens stored in httpOnly cookies. Here are my suggestions:\n\n1. **Token Refresh**: Implement automatic token refresh...",
         "success"),
        ("Refactor the UserService class to use dependency injection",
         "I'll refactor the UserService to use constructor injection:\n\n```python\nclass UserService:\n    def __init__(self, db: Database, cache: CacheService)...",
         "success"),
        ("Write unit tests for the payment processing module",
         "Here are comprehensive unit tests for the payment module:\n\n```python\nimport pytest\nfrom payment import PaymentProcessor...",
         "success"),
        ("Explain how the event sourcing pattern works in this system",
         "The event sourcing pattern in this system works as follows:\n\n1. **Event Store**: All state changes are stored as events...",
         "success"),
        ("Debug the memory leak in the WebSocket handler",
         "I found the memory leak! The issue is in the connection cleanup:\n\n```python\n# Before (leaking)\nself.connections.append(ws)\n\n# After (fixed)...",
         "success"),
        ("Create a new API endpoint for bulk user import",
         "I'll create a bulk import endpoint with proper validation and error handling:\n\n```python\n@app.post('/api/users/bulk-import')...",
         "success"),
        ("Optimize the database queries in the dashboard component",
         "I've identified several N+1 query issues. Here's the optimized version using eager loading:\n\n```python\nquery = session.query(User).options...",
         "success"),
        ("Add error handling for the file upload feature",
         "I'll add comprehensive error handling for file uploads:\n\n```python\ntry:\n    file = await request.files.get('file')...",
         "success"),
        ("Implement rate limiting for the API",
         "Here's a Redis-based rate limiter implementation:\n\n```python\nfrom redis import Redis\n\nclass RateLimiter:\n    def __init__(self, redis: Redis)...",
         "success"),
        ("Review this pull request for security vulnerabilities",
         "I've reviewed the PR and found these security concerns:\n\n1. **SQL Injection** in line 45: Use parameterized queries\n2. **XSS vulnerability**...",
         "success"),
        ("Generate API documentation for the orders module",
         "# Orders API Documentation\n\n## Endpoints\n\n### GET /api/orders\nReturns a paginated list of orders...",
         "success"),
        ("Help me understand the caching strategy",
         "The caching strategy uses a multi-layer approach:\n\n1. **L1 Cache**: In-memory LRU cache for hot data\n2. **L2 Cache**: Redis for distributed...",
         "success"),
        ("Fix the race condition in the inventory update",
         "The race condition occurs when multiple requests update inventory simultaneously. Here's the fix using optimistic locking:\n\n```python...",
         "success"),
        ("Create a migration script for the new schema",
         "Here's the Alembic migration script:\n\n```python\ndef upgrade():\n    op.add_column('users', sa.Column('preferences', sa.JSON))...",
         "success"),
        ("Implement websocket notifications for real-time updates",
         "I'll implement a WebSocket notification system:\n\n```python\nclass NotificationHub:\n    def __init__(self):\n        self.connections = {}...",
         "success"),
    ]

    base_time = datetime.now() - timedelta(days=7)
    session_id = f"session-demo-{random.randint(1000, 9999)}"

    for i, (prompt, response, status) in enumerate(prompts_data):
        model_info = random.choice(models)
        provider, model, input_price, output_price = model_info

        input_tokens = random.randint(500, 3000)
        output_tokens = random.randint(1000, 5000)
        total_tokens = input_tokens + output_tokens
        cost = (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)
        duration = random.uniform(1.5, 8.0)

        timestamp = (base_time + timedelta(hours=i * 4 + random.randint(0, 3))).isoformat()

        cursor.execute("""
            INSERT INTO prompt_logs (
                timestamp, provider, model, input_tokens, output_tokens,
                total_tokens, cost, duration, prompt_preview, response_preview,
                status, session_id, user, tool_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, provider, model, input_tokens, output_tokens,
            total_tokens, round(cost, 4), round(duration, 2),
            prompt[:500], response[:500], status, session_id, "demo-user", "claude-code"
        ))

    print(f"Created {len(prompts_data)} sample prompt logs")


def create_sample_context(cursor):
    """Create sample context history entries."""

    codebase_summary = """# Codebase Summary

## Overview
This is a modern full-stack web application built with Python (FastAPI) backend and Svelte frontend.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Frontend**: Svelte 5, Vite, TypeScript
- **Styling**: CSS Variables, Custom Theme System

## Directory Structure
```
├── backend/
│   ├── api/          # REST API endpoints
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   └── utils/        # Helper functions
├── frontend/
│   ├── src/
│   │   ├── lib/      # Shared components
│   │   ├── routes/   # Page components
│   │   └── stores/   # State management
│   └── static/       # Static assets
└── tests/            # Test suites
```

## Key Features
1. **User Authentication** - JWT-based auth with refresh tokens
2. **Real-time Updates** - WebSocket connections for live data
3. **Task Management** - Kanban-style board with drag-and-drop
4. **Analytics Dashboard** - Charts and metrics visualization

## Recent Changes
- Added dark mode support with 25+ themes
- Implemented per-repository data storage
- Added tour guide for new users
"""

    architecture_doc = """{
  "name": "Demo Application",
  "version": "1.0.0",
  "description": "A modern full-stack web application",
  "tech_stack": [
    {"name": "Python", "version": "3.12", "category": "backend"},
    {"name": "FastAPI", "version": "0.104", "category": "backend"},
    {"name": "Svelte", "version": "5.0", "category": "frontend"},
    {"name": "SQLite", "version": "3.x", "category": "database"}
  ],
  "entities": [
    {
      "name": "User",
      "fields": ["id", "email", "name", "created_at"],
      "relationships": ["has_many: Tasks", "has_many: Sessions"]
    },
    {
      "name": "Task",
      "fields": ["id", "title", "status", "priority", "sprint"],
      "relationships": ["belongs_to: User", "belongs_to: Version"]
    },
    {
      "name": "Version",
      "fields": ["id", "key", "label", "sort_order"],
      "relationships": ["has_many: Tasks"]
    }
  ],
  "endpoints": [
    {"method": "GET", "path": "/api/tasks", "description": "List all tasks"},
    {"method": "POST", "path": "/api/tasks", "description": "Create a task"},
    {"method": "PUT", "path": "/api/tasks/{id}", "description": "Update a task"},
    {"method": "DELETE", "path": "/api/tasks/{id}", "description": "Delete a task"}
  ],
  "ui_components": [
    {"name": "TaskManager", "type": "page", "features": ["kanban board", "drag-drop", "filters"]},
    {"name": "Topbar", "type": "layout", "features": ["navigation", "repo selector", "theme picker"]},
    {"name": "TourGuide", "type": "overlay", "features": ["step-by-step guide", "highlights"]}
  ]
}"""

    prompts_summary = """# AI Prompts Analysis

## Usage Statistics
- **Total Prompts**: 47 in the last 7 days
- **Total Tokens**: 156,432 (42,100 input / 114,332 output)
- **Estimated Cost**: $12.45

## Most Common Use Cases
1. **Code Refactoring** (35%) - Improving code quality and structure
2. **Bug Fixes** (25%) - Debugging and fixing issues
3. **Feature Implementation** (20%) - Building new features
4. **Documentation** (12%) - Generating docs and comments
5. **Code Review** (8%) - Reviewing PRs and code quality

## Model Usage
- Claude Opus 4.5: 60% (complex tasks)
- Claude Sonnet 4: 30% (general coding)
- Claude Haiku: 10% (quick queries)

## Insights
- Peak usage hours: 10am-12pm, 2pm-4pm
- Average response time: 3.2 seconds
- Success rate: 98.5%

## Recommendations
- Consider using Haiku for simple queries to reduce costs
- Complex refactoring tasks benefit from Opus's reasoning
"""

    base_time = datetime.now() - timedelta(days=3)

    entries = [
        ("codebase", codebase_summary, base_time),
        ("architecture", architecture_doc, base_time + timedelta(hours=2)),
        ("prompts", prompts_summary, base_time + timedelta(hours=4)),
    ]

    for context_type, content, created_at in entries:
        cursor.execute("""
            INSERT INTO context_history (context_type, content, created_at)
            VALUES (?, ?, ?)
        """, (context_type, content, created_at.isoformat()))

    print(f"Created {len(entries)} sample context entries")


def create_sample_tasks(cursor):
    """Create sample tasks."""

    tasks = [
        # v1 - completed features
        ("Implement user authentication", "Add JWT-based login and registration", "done", "v1", 0),
        ("Create task management board", "Kanban-style board with drag-and-drop", "done", "v1", 1),
        ("Add dark mode support", "Implement theme system with multiple color schemes", "done", "v1", 2),
        ("Set up database migrations", "Alembic migrations for schema changes", "done", "v1", 3),

        # v1 - in progress
        ("Add real-time notifications", "WebSocket-based notification system", "in_progress", "v1", 4),
        ("Improve error handling", "Better error messages and logging", "in_progress", "v1", 5),

        # v2 - planned features
        ("Implement team collaboration", "Share tasks and boards with team members", "todo", "v2", 0),
        ("Add file attachments", "Allow attaching files to tasks", "todo", "v2", 1),
        ("Create mobile app", "React Native app for iOS and Android", "todo", "v2", 2),
        ("Add integrations", "Connect with GitHub, Slack, Jira", "todo", "v2", 3),
        ("Implement search", "Full-text search across all content", "todo", "v2", 4),

        # Backlog
        ("Performance optimization", "Improve load times and reduce bundle size", "todo", "backlog", 0),
        ("Accessibility audit", "Ensure WCAG 2.1 AA compliance", "todo", "backlog", 1),
        ("Add analytics dashboard", "Usage metrics and charts", "todo", "backlog", 2),
        ("Write documentation", "User guide and API docs", "todo", "backlog", 3),
        ("Set up CI/CD", "Automated testing and deployment", "todo", "backlog", 4),
    ]

    base_time = datetime.now() - timedelta(days=14)

    for i, (title, description, status, sprint, sort_order) in enumerate(tasks):
        created_at = (base_time + timedelta(days=i // 3)).isoformat()
        updated_at = datetime.now().isoformat() if status == "in_progress" else created_at
        priority = random.randint(0, 2)

        cursor.execute("""
            INSERT INTO tasks (title, description, status, priority, sprint, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, status, priority, sprint, sort_order, created_at, updated_at))

    print(f"Created {len(tasks)} sample tasks")


def create_sample_versions(cursor):
    """Create sample versions."""

    versions = [
        ("v1", "Version 1.0", 0),
        ("v2", "Version 2.0", 1),
    ]

    for key, label, sort_order in versions:
        cursor.execute("""
            INSERT INTO versions (key, label, sort_order, created_at)
            VALUES (?, ?, ?, ?)
        """, (key, label, sort_order, datetime.now().isoformat()))

    print(f"Created {len(versions)} sample versions")


def create_tasks_json(example_dir: Path):
    """Create tasks.json file for backward compatibility."""

    tasks_data = {
        "tasks": [],
        "versions": [
            {"id": 1, "key": "v1", "label": "Version 1.0", "sort_order": 0, "created_at": datetime.now().isoformat()},
            {"id": 2, "key": "v2", "label": "Version 2.0", "sort_order": 1, "created_at": datetime.now().isoformat()},
        ],
        "next_id": 17,
        "next_version_id": 3
    }

    # Add tasks matching the database
    tasks = [
        (1, "Implement user authentication", "Add JWT-based login and registration", "done", "v1", 0),
        (2, "Create task management board", "Kanban-style board with drag-and-drop", "done", "v1", 1),
        (3, "Add dark mode support", "Implement theme system with multiple color schemes", "done", "v1", 2),
        (4, "Set up database migrations", "Alembic migrations for schema changes", "done", "v1", 3),
        (5, "Add real-time notifications", "WebSocket-based notification system", "in_progress", "v1", 4),
        (6, "Improve error handling", "Better error messages and logging", "in_progress", "v1", 5),
        (7, "Implement team collaboration", "Share tasks and boards with team members", "todo", "v2", 0),
        (8, "Add file attachments", "Allow attaching files to tasks", "todo", "v2", 1),
        (9, "Create mobile app", "React Native app for iOS and Android", "todo", "v2", 2),
        (10, "Add integrations", "Connect with GitHub, Slack, Jira", "todo", "v2", 3),
        (11, "Implement search", "Full-text search across all content", "todo", "v2", 4),
        (12, "Performance optimization", "Improve load times and reduce bundle size", "todo", "backlog", 0),
        (13, "Accessibility audit", "Ensure WCAG 2.1 AA compliance", "todo", "backlog", 1),
        (14, "Add analytics dashboard", "Usage metrics and charts", "todo", "backlog", 2),
        (15, "Write documentation", "User guide and API docs", "todo", "backlog", 3),
        (16, "Set up CI/CD", "Automated testing and deployment", "todo", "backlog", 4),
    ]

    base_time = datetime.now() - timedelta(days=14)

    for id, title, description, status, sprint, sort_order in tasks:
        created_at = (base_time + timedelta(days=id // 3)).isoformat()
        updated_at = datetime.now().isoformat() if status == "in_progress" else created_at

        tasks_data["tasks"].append({
            "id": id,
            "title": title,
            "description": description,
            "status": status,
            "priority": random.randint(0, 2),
            "sprint": sprint,
            "sort_order": sort_order,
            "created_at": created_at,
            "updated_at": updated_at
        })

    tasks_json_path = example_dir / "tasks.json"
    with open(tasks_json_path, "w") as f:
        json.dump(tasks_data, f, indent=2)

    print(f"Created tasks.json at {tasks_json_path}")


def main():
    """Main function to create all sample data."""

    db_path = EXAMPLE_DIR / "data.db"

    print(f"Creating sample database at: {db_path}")

    # Remove existing database if present
    if db_path.exists():
        db_path.unlink()

    conn = init_database(db_path)
    cursor = conn.cursor()

    try:
        create_sample_prompts(cursor)
        create_sample_context(cursor)
        create_sample_tasks(cursor)
        create_sample_versions(cursor)

        conn.commit()
        print("\nDatabase created successfully!")

        # Also create tasks.json for compatibility
        create_tasks_json(EXAMPLE_DIR)

        print(f"\nSample data created in: {EXAMPLE_DIR}")
        print("\nTo use this data:")
        print(f"1. Copy {EXAMPLE_DIR} to your project")
        print("2. Or start the server with this as the repo path")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
