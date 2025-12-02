#!/usr/bin/env python3
"""
Claude Code Hook for Branch Monkey Prompt Logging.

This hook logs AI prompt interactions to the Branch Monkey database.

Usage:
1. Add this to your Claude Code hooks configuration (CLAUDE.md or settings):

   hooks:
     PostToolUse:
       - command: python /path/to/branch_monkey/hooks/claude_code_hook.py
         match: .*

2. Or use it manually by piping Claude Code tool output:
   echo '{"type": "assistant", "message": {...}, "session_id": "...", "cwd": "..."}' | python claude_code_hook.py

The hook reads JSON input from stdin with the following expected fields:
- cwd: Current working directory (repo path)
- session_id: Claude Code session ID
- model: Model name (e.g., 'claude-sonnet-4-20250514')
- input_tokens: Input token count (from usage)
- output_tokens: Output token count (from usage)
- duration_ms: Request duration in milliseconds
- message: The assistant message (for preview)
- tool_input: The user/tool input (for preview)
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
        # Read JSON from stdin
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
            if input_data.strip():
                data = json.loads(input_data)
            else:
                return
        else:
            # No input provided
            return

        # Extract required fields
        cwd = data.get('cwd', os.getcwd())
        session_id = data.get('session_id', data.get('sessionId', ''))
        model = data.get('model', 'unknown')

        # Token counts - try different field names
        input_tokens = data.get('input_tokens', data.get('inputTokens', 0))
        output_tokens = data.get('output_tokens', data.get('outputTokens', 0))

        # Duration in milliseconds
        duration_ms = data.get('duration_ms', data.get('durationMs', 0))

        # Get previews from message content
        prompt_preview = ''
        response_preview = ''

        # Handle different message formats
        if 'message' in data:
            msg = data['message']
            if isinstance(msg, str):
                response_preview = msg[:500]
            elif isinstance(msg, dict):
                content = msg.get('content', '')
                if isinstance(content, str):
                    response_preview = content[:500]
                elif isinstance(content, list):
                    # Handle content blocks
                    texts = [b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text']
                    response_preview = ' '.join(texts)[:500]

        if 'tool_input' in data:
            tool_input = data['tool_input']
            if isinstance(tool_input, str):
                prompt_preview = tool_input[:500]
            elif isinstance(tool_input, dict):
                prompt_preview = json.dumps(tool_input)[:500]
        elif 'prompt' in data:
            prompt_preview = str(data['prompt'])[:500]

        # Status
        status = 'success'
        error_message = None
        if data.get('error') or data.get('status') == 'error':
            status = 'error'
            error_message = data.get('error_message', data.get('error', 'Unknown error'))

        # User
        user = data.get('user', os.environ.get('USER', 'unknown'))

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
            status=status,
            error_message=error_message
        )

        # Output result as JSON
        print(json.dumps({'success': True, 'id': result.get('id')}))

    except json.JSONDecodeError as e:
        print(json.dumps({'success': False, 'error': f'Invalid JSON: {e}'}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
