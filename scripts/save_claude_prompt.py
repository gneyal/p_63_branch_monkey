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
    """Format the conversation into a readable prompt - only first prompt and response."""
    if not conversation:
        return None

    # Find first user message and first assistant response
    first_user = None
    first_assistant = None

    for msg in conversation:
        if msg['role'] == 'user' and first_user is None:
            first_user = msg
        elif msg['role'] == 'assistant' and first_assistant is None and first_user is not None:
            first_assistant = msg
            break  # Stop after finding first response

    # Build formatted conversation with only first prompt and response
    formatted_parts = []

    if first_user and first_user['content'].strip():
        formatted_parts.append("[USER]")
        formatted_parts.append(first_user['content'].strip())
        formatted_parts.append("")

    if first_assistant and first_assistant['content'].strip():
        formatted_parts.append("[ASSISTANT]")
        formatted_parts.append(first_assistant['content'].strip())

    return '\n'.join(formatted_parts).strip() if formatted_parts else None


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

        # Debug: log what we received
        debug_log = Path.home() / '.branch_monkey' / 'hook_debug.log'
        debug_log.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_log, 'a') as f:
            f.write(f"\n{datetime.now()}: Hook received: {json.dumps(hook_input, indent=2)}\n")

        # Get transcript path
        transcript_path = Path(hook_input.get('transcript_path', ''))
        if not transcript_path.exists():
            print(f"Transcript not found: {transcript_path}", file=sys.stderr)
            with open(debug_log, 'a') as f:
                f.write(f"ERROR: Transcript not found at {transcript_path}\n")
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
