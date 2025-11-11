#!/usr/bin/env python
"""Test server directly."""

import sys
print("Python starting...", flush=True)

try:
    from branch_monkey.web.simple_app import run_simple_web
    print("Import successful!", flush=True)

    print("Starting server...", flush=True)
    run_simple_web(None, port=8080, open_browser=False)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
