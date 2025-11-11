#!/usr/bin/env python3
"""Run the web server with debugging."""

import sys
import traceback

print("Starting Branch Monkey Web Server...", flush=True)

try:
    from branch_monkey.web.simple_app import run_simple_web
    print("Imports successful", flush=True)

    print("Launching server on port 8080...", flush=True)
    run_simple_web(None, port=8080, open_browser=True)

except Exception as e:
    print(f"\n❌ ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
