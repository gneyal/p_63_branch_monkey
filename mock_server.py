#!/usr/bin/env python3
"""Mock web server with demo data."""

import json
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Mock data
MOCK_STATUS = {
    'success': True,
    'has_changes': True,
    'current_experiment': None,
    'recent_checkpoints': [
        {'short_id': 'a1b2c3d', 'age': '2 hours ago', 'message': 'Added user authentication', 'files_changed': 5, 'insertions': 120, 'deletions': 30},
        {'short_id': 'e4f5g6h', 'age': '5 hours ago', 'message': 'Fixed navigation bug', 'files_changed': 2, 'insertions': 15, 'deletions': 8},
        {'short_id': 'i7j8k9l', 'age': '1 day ago', 'message': 'Updated README', 'files_changed': 1, 'insertions': 25, 'deletions': 5},
    ]
}

MOCK_HISTORY = {
    'success': True,
    'entries': [
        {'short_sha': 'a1b2c3d', 'age': '2 hours ago', 'author': 'Alice', 'message': 'Added user authentication', 'summary_stats': '5 files, +120 -30'},
        {'short_sha': 'e4f5g6h', 'age': '5 hours ago', 'author': 'Bob', 'message': 'Fixed navigation bug', 'summary_stats': '2 files, +15 -8'},
        {'short_sha': 'i7j8k9l', 'age': '1 day ago', 'author': 'Charlie', 'message': 'Updated README', 'summary_stats': '1 file, +25 -5'},
        {'short_sha': 'm1n2o3p', 'age': '2 days ago', 'author': 'Alice', 'message': 'Initial commit', 'summary_stats': '10 files, +500 -0'},
    ]
}

MOCK_CHECKPOINTS = {
    'success': True,
    'checkpoints': [
        {'short_id': 'a1b2c3d', 'age': '2 hours ago', 'message': 'Added user authentication', 'files_changed': 5, 'insertions': 120, 'deletions': 30},
        {'short_id': 'e4f5g6h', 'age': '5 hours ago', 'message': 'Fixed navigation bug', 'files_changed': 2, 'insertions': 15, 'deletions': 8},
        {'short_id': 'i7j8k9l', 'age': '1 day ago', 'message': 'Updated README', 'files_changed': 1, 'insertions': 25, 'deletions': 5},
    ]
}

MOCK_EXPERIMENTS = {
    'success': True,
    'experiments': [
        {'name': 'feature-dark-mode', 'is_active': True, 'description': 'Implementing dark mode', 'age': '3 hours ago', 'status': 'Active'},
        {'name': 'refactor-api', 'is_active': False, 'description': 'API refactoring', 'age': '2 days ago', 'status': 'Inactive'},
    ]
}


class MockHandler(BaseHTTPRequestHandler):
    """Mock HTTP request handler."""

    def log_message(self, format, *args):
        """Suppress logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_index()
        elif self.path == '/api/status':
            self.send_json(MOCK_STATUS)
        elif self.path.startswith('/api/history'):
            self.send_json(MOCK_HISTORY)
        elif self.path.startswith('/api/checkpoints'):
            self.send_json(MOCK_CHECKPOINTS)
        elif self.path.startswith('/api/experiments'):
            self.send_json(MOCK_EXPERIMENTS)
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests."""
        # Read POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # All POST operations return success
        if self.path == '/api/save':
            self.send_json({'success': True, 'checkpoint': {'short_id': 'new1234', 'message': 'New checkpoint'}})
        elif self.path == '/api/quick-save':
            self.send_json({'success': True, 'checkpoint': {'short_id': 'quick123', 'message': 'Quick save'}})
        elif self.path == '/api/undo':
            self.send_json({'success': True, 'message': 'Undone successfully'})
        elif self.path == '/api/restore':
            self.send_json({'success': True, 'message': 'Restored successfully'})
        elif self.path == '/api/experiment/create':
            self.send_json({'success': True, 'experiment': {'name': 'new-experiment'}})
        elif self.path == '/api/experiment/switch':
            self.send_json({'success': True, 'message': 'Switched successfully'})
        elif self.path == '/api/experiment/keep':
            self.send_json({'success': True, 'message': 'Experiment merged'})
        elif self.path == '/api/experiment/discard':
            self.send_json({'success': True, 'message': 'Experiment discarded'})
        else:
            self.send_error(404)

    def serve_index(self):
        """Serve the main HTML page."""
        html_path = Path(__file__).parent / 'branch_monkey' / 'web' / 'templates' / 'index.html'
        try:
            with open(html_path, 'r') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, f"Could not load page: {e}")

    def send_json(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def main():
    """Run the mock server."""
    port = 8080
    server = HTTPServer(('127.0.0.1', port), MockHandler)

    # Auto-open browser
    def open_browser_delayed():
        import time
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')

    threading.Thread(target=open_browser_delayed, daemon=True).start()

    print(f"\n🐵 Branch Monkey Web Interface (Demo Mode)")
    print(f"   Running on http://localhost:{port}")
    print(f"   Using mock data for demonstration")
    print(f"   Press Ctrl+C to quit\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
