#!/usr/bin/env python3
"""
Claude Code Hook for Branch Monkey Prompt Logging.

This hook logs AI prompt interactions to the Branch Monkey database.
It's designed for the "Stop" hook event which fires once per response.

Usage:
Add this to ~/.claude/settings.json:

{
  "hooks": {
    "Stop": [{
      "command": "python /path/to/branch_monkey/branch_monkey/hooks/claude_code_hook.py"
    }]
  }
}

Stdin receives JSON with:
- session_id: Session identifier
- transcript_path: Path to conversation JSONL file
- cwd: Current working directory
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from branch_monkey.core.prompts import log_claude_code_prompt


def read_transcript(transcript_path: str) -> tuple[str, str, str, int, int, float]:
    """Read the transcript file to extract conversation data.

    Returns:
        tuple of (prompt_preview, response_preview, model, input_tokens, output_tokens, duration_ms)
    """
    from datetime import datetime

    prompt_preview = ''
    response_preview = ''
    model = 'unknown'
    input_tokens = 0
    output_tokens = 0
    duration_ms = 0.0

    # Track timestamps for duration calculation
    last_user_timestamp = None
    last_assistant_timestamp = None

    try:
        with open(transcript_path, 'r') as f:
            # JSONL file - each line is a JSON object
            lines = f.readlines()

            # Find the last user and assistant messages
            for line in reversed(lines):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    msg_type = entry.get('type', '')
                    message = entry.get('message', {})
                    timestamp_str = entry.get('timestamp', '')

                    # Extract from assistant messages
                    if msg_type == 'assistant':
                        # Model is inside message object
                        if model == 'unknown' and 'model' in message:
                            model = message['model']

                        # Token usage is inside message.usage
                        usage = message.get('usage', {})
                        if usage:
                            input_tokens = max(input_tokens, usage.get('input_tokens', 0))
                            output_tokens = max(output_tokens, usage.get('output_tokens', 0))

                        # Response content
                        if not response_preview:
                            content = message.get('content', '')
                            if isinstance(content, str):
                                response_preview = content[:500]
                            elif isinstance(content, list):
                                texts = [b.get('text', '') for b in content if isinstance(b, dict) and 'text' in b]
                                response_preview = ' '.join(texts)[:500]

                        # Track last assistant timestamp
                        if not last_assistant_timestamp and timestamp_str:
                            try:
                                last_assistant_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except:
                                pass

                    # Extract from user messages
                    elif msg_type == 'user':
                        if not prompt_preview:
                            content = message.get('content', '')
                            if isinstance(content, str):
                                prompt_preview = content[:500]
                            elif isinstance(content, list):
                                texts = [b.get('text', '') for b in content if isinstance(b, dict) and 'text' in b]
                                prompt_preview = ' '.join(texts)[:500]

                            # Track user timestamp (only for the message we're extracting)
                            if timestamp_str:
                                try:
                                    last_user_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                except:
                                    pass

                    if prompt_preview and response_preview and model != 'unknown':
                        break

                except json.JSONDecodeError:
                    continue

        # Calculate duration if we have both timestamps
        if last_user_timestamp and last_assistant_timestamp:
            delta = last_assistant_timestamp - last_user_timestamp
            duration_ms = max(0, delta.total_seconds() * 1000)

    except Exception:
        pass

    return prompt_preview, response_preview, model, input_tokens, output_tokens, duration_ms


def main():
    """Main entry point for the hook."""
    # Debug log will be set after we know the cwd
    debug_log = None

    def log_debug(msg):
        if debug_log is None:
            return  # Skip logging if we don't have a path yet
        try:
            debug_log.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_log, 'a') as f:
                from datetime import datetime
                f.write(f"{datetime.now()}: {msg}\n")
        except Exception:
            pass  # Silently ignore debug log failures

    try:
        # Read hook data from stdin
        if sys.stdin.isatty():
            return

        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        data = json.loads(input_data)

        # Set debug log path based on cwd
        cwd = data.get('cwd', os.getcwd())
        debug_log = Path(cwd) / ".branch_monkey" / "hook_debug.log"

        log_debug("Hook started")
        log_debug(f"Parsed JSON: cwd={cwd}, session={data.get('session_id')}")

        # Extract fields from stdin JSON
        cwd = data.get('cwd', os.getcwd())
        session_id = data.get('session_id', '')
        transcript_path = data.get('transcript_path', '')

        # Read transcript file for conversation data
        prompt_preview = ''
        response_preview = ''
        model = 'unknown'
        input_tokens = 0
        output_tokens = 0
        duration_ms = 0.0

        if transcript_path and Path(transcript_path).exists():
            prompt_preview, response_preview, model, input_tokens, output_tokens, duration_ms = read_transcript(transcript_path)

        # User
        user = os.environ.get('USER', 'unknown')

        # Log the prompt
        result = log_claude_code_prompt(
            cwd=cwd,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            session_id=session_id,
            user=user,
            prompt_preview=prompt_preview,
            response_preview=response_preview,
            status='success',
            error_message=None
        )

        log_debug(f"Logged prompt id={result.get('id')}, model={model}, tokens={input_tokens}+{output_tokens}")

        # Output result as JSON (stdout for success)
        print(json.dumps({'success': True, 'id': result.get('id')}))

        # User-friendly message to stderr (visible in Claude Code)
        total_tokens = input_tokens + output_tokens
        if total_tokens > 0:
            print(f"[Branch Monkey] Logged: {model} | {input_tokens:,}+{output_tokens:,} tokens", file=sys.stderr)
        else:
            print(f"[Branch Monkey] Logged prompt (no token data)", file=sys.stderr)

    except Exception as e:
        log_debug(f"Error: {str(e)}")
        # Error message to stderr
        print(f"[Branch Monkey] Failed to log prompt: {str(e)}", file=sys.stderr)
        print(json.dumps({'success': False, 'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
