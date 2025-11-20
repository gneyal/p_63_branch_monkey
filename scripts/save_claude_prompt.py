#!/usr/bin/env python3
"""
Claude Code hook to automatically save conversation prompts to Branch Monkey.
This hook is triggered by Claude Code when a conversation stops or ends.
"""

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess


def get_current_commit_sha():
    """Get the current git HEAD commit SHA."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def parse_transcript(transcript_path):
    """Parse the Claude Code transcript and extract conversation."""
    conversation = []

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                entry = json.loads(line)
                entry_type = entry.get('type', '')

                # Extract user messages
                if entry_type == 'user':
                    content = entry.get('message', {}).get('content', '')
                    if isinstance(content, list):
                        # Handle multipart messages
                        text_parts = [
                            part.get('text', '')
                            for part in content
                            if part.get('type') == 'text'
                        ]
                        content = '\n'.join(text_parts)

                    conversation.append({
                        'role': 'user',
                        'content': content,
                        'timestamp': entry.get('timestamp', '')
                    })

                # Extract assistant responses
                elif entry_type == 'assistant':
                    content = entry.get('message', {}).get('content', '')
                    if isinstance(content, list):
                        # Handle multipart messages
                        text_parts = [
                            part.get('text', '')
                            for part in content
                            if part.get('type') == 'text'
                        ]
                        content = '\n'.join(text_parts)

                    conversation.append({
                        'role': 'assistant',
                        'content': content,
                        'timestamp': entry.get('timestamp', '')
                    })

    except Exception as e:
        print(f"Error parsing transcript: {e}", file=sys.stderr)
        return []

    return conversation


def format_conversation(conversation):
    """Format the conversation into a readable prompt."""
    if not conversation:
        return None

    # Build formatted conversation
    formatted_parts = []

    for i, msg in enumerate(conversation):
        role = msg['role'].upper()
        content = msg['content'].strip()

        if content:
            formatted_parts.append(f"[{role}]")
            formatted_parts.append(content)
            formatted_parts.append("")  # Empty line between messages

    return '\n'.join(formatted_parts).strip()


def save_to_database(sha, prompt_text, repo_path):
    """Save the prompt to the Branch Monkey prompts database."""
    db_path = Path.home() / '.branch_monkey' / 'prompts.db'

    if not db_path.exists():
        print(f"Database not found at {db_path}", file=sys.stderr)
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()

        # Insert or replace the prompt
        cursor.execute(
            """
            INSERT OR REPLACE INTO prompts (sha, prompt, timestamp, repo_path)
            VALUES (?, ?, ?, ?)
            """,
            (sha, prompt_text, timestamp, str(repo_path))
        )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error saving to database: {e}", file=sys.stderr)
        return False


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        # Get transcript path
        transcript_path = Path(hook_input.get('transcript_path', ''))
        if not transcript_path.exists():
            print(f"Transcript not found: {transcript_path}", file=sys.stderr)
            return

        # Get current working directory (repo path)
        cwd = Path(hook_input.get('cwd', Path.cwd()))

        # Get current commit SHA
        sha = get_current_commit_sha()
        if not sha:
            print("Not in a git repository or no commits yet", file=sys.stderr)
            return

        # Parse the conversation
        conversation = parse_transcript(transcript_path)
        if not conversation:
            print("No conversation found in transcript", file=sys.stderr)
            return

        # Format the conversation
        prompt_text = format_conversation(conversation)
        if not prompt_text:
            print("Could not format conversation", file=sys.stderr)
            return

        # Save to database
        if save_to_database(sha, prompt_text, cwd):
            print(f"✓ Saved conversation to commit {sha[:7]}", file=sys.stderr)
        else:
            print("Failed to save conversation", file=sys.stderr)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
