#!/usr/bin/env python3
"""
Migration script: Move data from global DBs to per-repo .branch_monkey/data.db files.

This script:
1. Reads data from global ~/.branch_monkey/*.db files
2. Creates per-repo .branch_monkey/data.db files
3. Migrates the data filtered by repo_path
"""

import sqlite3
from pathlib import Path
from datetime import datetime


# Global DB paths
GLOBAL_DIR = Path.home() / ".branch_monkey"
GLOBAL_PROMPTS_DB = GLOBAL_DIR / "prompts.db"
GLOBAL_CONTEXT_DB = GLOBAL_DIR / "context_history.db"

# Per-repo DB filename
LOCAL_DB_NAME = "data.db"


def get_local_db_path(repo_path: Path) -> Path:
    """Get the path to a repo's local database."""
    return repo_path / ".branch_monkey" / LOCAL_DB_NAME


def init_local_db(db_path: Path):
    """Initialize a local database with all required tables."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)

    # Prompt logs table
    conn.execute('''
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
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_prompt_logs_timestamp
        ON prompt_logs(timestamp DESC)
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_prompt_logs_session
        ON prompt_logs(session_id)
    ''')

    # Context history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_context_type
        ON context_history(context_type, created_at DESC)
    ''')

    # Tasks table (migrating from JSON to DB for consistency)
    conn.execute('''
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
    ''')

    # Versions/sprints table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"  Initialized: {db_path}")


def migrate_prompts(repo_path: Path, local_db_path: Path):
    """Migrate prompt_logs for a specific repo."""
    if not GLOBAL_PROMPTS_DB.exists():
        print(f"  No global prompts.db found, skipping prompts migration")
        return 0

    repo_path_str = str(repo_path.resolve())

    global_conn = sqlite3.connect(GLOBAL_PROMPTS_DB)
    local_conn = sqlite3.connect(local_db_path)

    cursor = global_conn.cursor()
    cursor.execute('''
        SELECT timestamp, provider, model, input_tokens, output_tokens,
               total_tokens, cost, duration, prompt_preview, response_preview,
               status, error_message, session_id, user, tool_name, metadata
        FROM prompt_logs
        WHERE repo_path = ?
        ORDER BY timestamp ASC
    ''', (repo_path_str,))

    rows = cursor.fetchall()

    for row in rows:
        local_conn.execute('''
            INSERT INTO prompt_logs (
                timestamp, provider, model, input_tokens, output_tokens,
                total_tokens, cost, duration, prompt_preview, response_preview,
                status, error_message, session_id, user, tool_name, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)

    local_conn.commit()
    global_conn.close()
    local_conn.close()

    return len(rows)


def migrate_context(repo_path: Path, local_db_path: Path):
    """Migrate context_history for a specific repo."""
    if not GLOBAL_CONTEXT_DB.exists():
        print(f"  No global context_history.db found, skipping context migration")
        return 0

    repo_path_str = str(repo_path.resolve())

    global_conn = sqlite3.connect(GLOBAL_CONTEXT_DB)
    local_conn = sqlite3.connect(local_db_path)

    cursor = global_conn.cursor()
    cursor.execute('''
        SELECT context_type, content, created_at
        FROM context_history
        WHERE repo_path = ?
        ORDER BY created_at ASC
    ''', (repo_path_str,))

    rows = cursor.fetchall()

    for row in rows:
        local_conn.execute('''
            INSERT INTO context_history (context_type, content, created_at)
            VALUES (?, ?, ?)
        ''', row)

    local_conn.commit()
    global_conn.close()
    local_conn.close()

    return len(rows)


def migrate_tasks_from_json(repo_path: Path, local_db_path: Path):
    """Migrate tasks from JSON file to local DB."""
    import json

    json_path = repo_path / ".branch_monkey" / "tasks.json"
    if not json_path.exists():
        return 0, 0

    try:
        with open(json_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return 0, 0

    local_conn = sqlite3.connect(local_db_path)

    tasks = data.get("tasks", [])
    versions = data.get("versions", [])

    # Migrate tasks
    for task in tasks:
        local_conn.execute('''
            INSERT INTO tasks (id, title, description, status, priority, sprint, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.get("id"),
            task.get("title", ""),
            task.get("description", ""),
            task.get("status", "todo"),
            task.get("priority", 0),
            task.get("sprint", "backlog"),
            task.get("sort_order", 0),
            task.get("created_at", datetime.now().isoformat()),
            task.get("updated_at", datetime.now().isoformat())
        ))

    # Migrate versions
    for version in versions:
        try:
            local_conn.execute('''
                INSERT INTO versions (name, description, status, created_at)
                VALUES (?, ?, ?, ?)
            ''', (
                version.get("name", ""),
                version.get("description", ""),
                version.get("status", "active"),
                version.get("created_at", datetime.now().isoformat())
            ))
        except sqlite3.IntegrityError:
            pass  # Version name already exists

    local_conn.commit()
    local_conn.close()

    return len(tasks), len(versions)


def get_all_repo_paths():
    """Get all unique repo paths from global DBs."""
    repos = set()

    if GLOBAL_PROMPTS_DB.exists():
        conn = sqlite3.connect(GLOBAL_PROMPTS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT repo_path FROM prompt_logs")
        for row in cursor.fetchall():
            repos.add(row[0])
        conn.close()

    if GLOBAL_CONTEXT_DB.exists():
        conn = sqlite3.connect(GLOBAL_CONTEXT_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT repo_path FROM context_history")
        for row in cursor.fetchall():
            repos.add(row[0])
        conn.close()

    return repos


def main():
    print("=" * 60)
    print("Branch Monkey: Migration to per-repo databases")
    print("=" * 60)
    print()

    # Get all repos that have data
    repos = get_all_repo_paths()

    # Also check for repos with tasks.json
    for potential_repo in Path.home().glob("Code/*/.branch_monkey/tasks.json"):
        repos.add(str(potential_repo.parent.parent.resolve()))

    if not repos:
        print("No repositories found with data to migrate.")
        return

    print(f"Found {len(repos)} repositories with data:")
    for repo in sorted(repos):
        print(f"  - {repo}")
    print()

    # Migrate each repo
    for repo_path_str in sorted(repos):
        repo_path = Path(repo_path_str)

        if not repo_path.exists():
            print(f"[SKIP] {repo_path_str} (directory does not exist)")
            continue

        print(f"[MIGRATE] {repo_path_str}")

        local_db_path = get_local_db_path(repo_path)

        # Initialize local DB
        init_local_db(local_db_path)

        # Migrate data
        prompts_count = migrate_prompts(repo_path, local_db_path)
        print(f"  Migrated {prompts_count} prompt logs")

        context_count = migrate_context(repo_path, local_db_path)
        print(f"  Migrated {context_count} context entries")

        tasks_count, versions_count = migrate_tasks_from_json(repo_path, local_db_path)
        print(f"  Migrated {tasks_count} tasks, {versions_count} versions")

        print()

    print("=" * 60)
    print("Migration complete!")
    print()
    print("Next steps:")
    print("1. Verify the data in .branch_monkey/data.db files")
    print("2. Update Branch Monkey to use local DBs (code changes)")
    print("3. Optionally backup and remove global DBs:")
    print(f"   mv {GLOBAL_DIR} {GLOBAL_DIR}.backup")
    print("=" * 60)


if __name__ == "__main__":
    main()
