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
      "command": "python /path/to/branch_monkey/hooks/claude_code_hook.py"
    }]
  }
}

Environment variables provided by Claude Code:
- CLAUDE_WORKING_DIRECTORY: Current project directory
- CLAUDE_SESSION_ID: Session identifier
- CLAUDE_MODEL: Model used (e.g., 'claude-sonnet-4-20250514')
- CLAUDE_INPUT_TOKENS: Total input tokens
- CLAUDE_OUTPUT_TOKENS: Total output tokens

Stdin contains JSON with conversation transcript.
"""

import sys
import json
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from branch_monkey.core.prompts import log_claude_code_prompt


def main():
    """Main entry point for the hook."""
    try:
        # Get data from environment variables (primary source for Stop hook)
        cwd = os.environ.get('CLAUDE_WORKING_DIRECTORY', os.getcwd())
        session_id = os.environ.get('CLAUDE_SESSION_ID', '')
        model = os.environ.get('CLAUDE_MODEL', 'unknown')
        input_tokens = int(os.environ.get('CLAUDE_INPUT_TOKENS', 0))
        output_tokens = int(os.environ.get('CLAUDE_OUTPUT_TOKENS', 0))

        # Skip if no token data (hook might have fired without actual API call)
        if input_tokens == 0 and output_tokens == 0:
            return

        # Try to read transcript from stdin for previews
        prompt_preview = ''
        response_preview = ''

        if not sys.stdin.isatty():
            try:
                input_data = sys.stdin.read()
                if input_data.strip():
                    data = json.loads(input_data)

                    # Extract last user message as prompt preview
                    if 'transcript' in data:
                        for msg in reversed(data['transcript']):
                            if msg.get('role') == 'user' and not prompt_preview:
                                content = msg.get('content', '')
                                if isinstance(content, str):
                                    prompt_preview = content[:500]
                                elif isinstance(content, list):
                                    texts = [b.get('text', '') for b in content if isinstance(b, dict)]
                                    prompt_preview = ' '.join(texts)[:500]
                            elif msg.get('role') == 'assistant' and not response_preview:
                                content = msg.get('content', '')
                                if isinstance(content, str):
                                    response_preview = content[:500]
                                elif isinstance(content, list):
                                    texts = [b.get('text', '') for b in content if isinstance(b, dict)]
                                    response_preview = ' '.join(texts)[:500]
                            if prompt_preview and response_preview:
                                break
            except (json.JSONDecodeError, KeyError):
                pass  # Previews are optional

        # User
        user = os.environ.get('USER', 'unknown')

        # Log the prompt
        result = log_claude_code_prompt(
            cwd=cwd,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=0,  # Not provided by Stop hook
            session_id=session_id,
            user=user,
            prompt_preview=prompt_preview,
            response_preview=response_preview,
            status='success',
            error_message=None
        )

        # Output result as JSON
        print(json.dumps({'success': True, 'id': result.get('id')}))

    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
