"""Prompt Logger - Tracks AI prompt usage, tokens, and costs."""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict


# Per-repo database filename (stored in <repo>/.branch_monkey/data.db)
LOCAL_DB_NAME = "data.db"


def get_local_db_path(repo_path: Path) -> Path:
    """Get the path to a repo's local database."""
    return repo_path / ".branch_monkey" / LOCAL_DB_NAME

# Known providers and their pricing (per 1M tokens as of late 2024)
PROVIDER_PRICING = {
    "anthropic": {
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
        "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
    },
    "openai": {
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }
}


@dataclass
class PromptLog:
    """A single prompt log entry."""
    id: int
    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    duration: float  # seconds
    prompt_preview: str
    response_preview: str
    status: str  # 'success', 'error'
    error_message: Optional[str]
    session_id: Optional[str]
    user: Optional[str]
    tool_name: Optional[str]  # 'claude-code', 'cursor', 'manual', etc.
    metadata: Optional[str]  # JSON string for extra data


def init_prompts_db(repo_path: Path):
    """Initialize the prompts database for a specific repo."""
    db_path = get_local_db_path(repo_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
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
    conn.commit()
    conn.close()


def calculate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate the cost of a prompt based on provider pricing."""
    provider_lower = provider.lower()
    model_lower = model.lower()

    if provider_lower in PROVIDER_PRICING:
        pricing = PROVIDER_PRICING[provider_lower]
        # Try exact match first
        if model_lower in pricing:
            rates = pricing[model_lower]
        else:
            # Try partial match
            for model_key, rates in pricing.items():
                if model_key in model_lower or model_lower in model_key:
                    break
            else:
                # Default to most common model pricing
                rates = list(pricing.values())[0]

        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        return round(input_cost + output_cost, 6)

    return 0.0


class PromptLogger:
    """
    Logs AI prompt interactions for tracking usage and costs.

    Designed to be called from hooks in AI tools like Claude Code.
    """

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize the prompt logger.

        Args:
            repo_path: Path to the Git repository (optional, can use current dir)
        """
        self.repo_path = repo_path or Path.cwd()
        self.db_path = get_local_db_path(self.repo_path)
        init_prompts_db(self.repo_path)

    def log_prompt(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration: float = 0.0,
        prompt_preview: str = "",
        response_preview: str = "",
        status: str = "success",
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        user: Optional[str] = None,
        tool_name: Optional[str] = None,
        cost: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> PromptLog:
        """
        Log a prompt interaction.

        Args:
            provider: AI provider ('anthropic', 'openai', etc.)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            duration: Request duration in seconds
            prompt_preview: First ~500 chars of the prompt
            response_preview: First ~500 chars of the response
            status: 'success' or 'error'
            error_message: Error message if status is 'error'
            session_id: Optional session/conversation ID
            user: Optional username
            tool_name: Tool that made the request ('claude-code', etc.)
            cost: Override calculated cost (optional)
            metadata: Additional metadata dict

        Returns:
            The created PromptLog entry
        """
        timestamp = datetime.now().isoformat()
        repo_path_str = str(self.repo_path.resolve())
        total_tokens = input_tokens + output_tokens

        # Calculate cost if not provided
        if cost is None:
            cost = calculate_cost(provider, model, input_tokens, output_tokens)

        # Truncate previews
        if prompt_preview and len(prompt_preview) > 500:
            prompt_preview = prompt_preview[:500] + "..."
        if response_preview and len(response_preview) > 500:
            response_preview = response_preview[:500] + "..."

        # Serialize metadata
        metadata_str = json.dumps(metadata) if metadata else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO prompt_logs (
                timestamp, provider, model,
                input_tokens, output_tokens, total_tokens, cost, duration,
                prompt_preview, response_preview, status, error_message,
                session_id, user, tool_name, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp, provider, model,
                input_tokens, output_tokens, total_tokens, cost, duration,
                prompt_preview, response_preview, status, error_message,
                session_id, user, tool_name, metadata_str
            )
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return PromptLog(
            id=entry_id,
            timestamp=timestamp,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            duration=duration,
            prompt_preview=prompt_preview,
            response_preview=response_preview,
            status=status,
            error_message=error_message,
            session_id=session_id,
            user=user,
            tool_name=tool_name,
            metadata=metadata_str
        )

    def get_prompts(
        self,
        limit: int = 100,
        offset: int = 0,
        session_id: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get prompt logs for this repository.

        Args:
            limit: Maximum number of entries to return
            offset: Offset for pagination
            session_id: Filter by session ID
            provider: Filter by provider
            status: Filter by status

        Returns:
            List of prompt log entries (most recent first)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT id, timestamp, provider, model,
                   input_tokens, output_tokens, total_tokens, cost, duration,
                   prompt_preview, response_preview, status, error_message,
                   session_id, user, tool_name, metadata
            FROM prompt_logs
            WHERE 1=1
        """
        params = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "provider": row[2],
                "model": row[3],
                "inputTokens": row[4],
                "outputTokens": row[5],
                "totalTokens": row[6],
                "cost": row[7],
                "duration": row[8],
                "promptPreview": row[9] or "",
                "responsePreview": row[10] or "",
                "status": row[11],
                "errorMessage": row[12],
                "sessionId": row[13],
                "user": row[14],
                "toolName": row[15],
                "metadata": json.loads(row[16]) if row[16] else None
            }
            for row in rows
        ]

    def get_stats(self) -> Dict:
        """
        Get aggregate statistics for this repository.

        Returns:
            Dict with total prompts, tokens, cost, etc.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) as total_prompts,
                COALESCE(SUM(input_tokens), 0) as total_input_tokens,
                COALESCE(SUM(output_tokens), 0) as total_output_tokens,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COALESCE(SUM(cost), 0) as total_cost,
                COALESCE(AVG(duration), 0) as avg_duration,
                COUNT(DISTINCT provider) as providers_used,
                COUNT(DISTINCT model) as models_used,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count
            FROM prompt_logs
            """
        )
        row = cursor.fetchone()

        # Get breakdown by provider
        cursor.execute(
            """
            SELECT provider, COUNT(*), SUM(cost), SUM(total_tokens)
            FROM prompt_logs
            GROUP BY provider
            """
        )
        provider_rows = cursor.fetchall()

        conn.close()

        return {
            "totalPrompts": row[0],
            "totalInputTokens": row[1],
            "totalOutputTokens": row[2],
            "totalTokens": row[3],
            "totalCost": round(row[4], 4),
            "avgDuration": round(row[5], 2),
            "providersUsed": row[6],
            "modelsUsed": row[7],
            "errorCount": row[8],
            "byProvider": {
                p_row[0]: {
                    "count": p_row[1],
                    "cost": round(p_row[2] or 0, 4),
                    "tokens": p_row[3] or 0
                }
                for p_row in provider_rows
            }
        }

    def delete_prompt(self, prompt_id: int) -> bool:
        """Delete a prompt log entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompt_logs WHERE id = ?", (prompt_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def clear_all(self) -> int:
        """Clear all prompt logs for this repository."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompt_logs")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted


# Convenience function for use from hooks
def log_claude_code_prompt(
    cwd: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    session_id: str,
    user: Optional[str] = None,
    prompt_preview: str = "",
    response_preview: str = "",
    status: str = "success",
    error_message: Optional[str] = None,
) -> Dict:
    """
    Convenience function for logging from Claude Code hooks.

    Args:
        cwd: Current working directory (repo path)
        model: Model name (e.g., 'claude-sonnet-4-20250514')
        input_tokens: Input token count
        output_tokens: Output token count
        duration_ms: Duration in milliseconds
        session_id: Claude Code session ID
        user: Username (optional)
        prompt_preview: Preview of the prompt
        response_preview: Preview of the response
        status: 'success' or 'error'
        error_message: Error message if any

    Returns:
        Dict with the logged entry
    """
    logger = PromptLogger(Path(cwd))
    entry = logger.log_prompt(
        provider="anthropic",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration=duration_ms / 1000.0,
        prompt_preview=prompt_preview,
        response_preview=response_preview,
        status=status,
        error_message=error_message,
        session_id=session_id,
        user=user or os.environ.get("USER", "unknown"),
        tool_name="claude-code",
    )
    return asdict(entry)
