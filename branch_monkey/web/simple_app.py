"""Simple web server using Python's built-in HTTP server."""

import json
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

from ..api import BranchMonkey


class BranchMonkeyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Branch Monkey web interface."""

    repo_path = None

    @classmethod
    def set_repo_path(cls, repo_path: Optional[Path] = None):
        """Set the repository path."""
        cls.repo_path = repo_path

    def get_monkey(self):
        """Get a BranchMonkey instance (created per request)."""
        try:
            return BranchMonkey(self.repo_path)
        except Exception as e:
            raise Exception(f"Could not initialize BranchMonkey: {e}")

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass  # Comment this out to see request logs

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path == '/':
                self.serve_index()
            elif path == '/api/status':
                self.api_status()
            elif path == '/api/history':
                self.api_history()
            elif path == '/api/checkpoints':
                self.api_checkpoints()
            elif path == '/api/experiments':
                self.api_experiments()
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_error(str(e))

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            # Read POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data) if post_data else {}

            if path == '/api/save':
                self.api_save(data)
            elif path == '/api/quick-save':
                self.api_quick_save(data)
            elif path == '/api/undo':
                self.api_undo(data)
            elif path == '/api/restore':
                self.api_restore(data)
            elif path == '/api/experiment/create':
                self.api_experiment_create(data)
            elif path == '/api/experiment/switch':
                self.api_experiment_switch(data)
            elif path == '/api/experiment/keep':
                self.api_experiment_keep(data)
            elif path == '/api/experiment/discard':
                self.api_experiment_discard(data)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_error(str(e))

    def serve_index(self):
        """Serve the main HTML page."""
        html_path = Path(__file__).parent / 'templates' / 'index.html'
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

    def send_json_error(self, error_msg):
        """Send JSON error response."""
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'error': error_msg}).encode())

    # API Endpoints
    def api_status(self):
        """Get current status."""
        try:
            monkey = self.get_monkey()
            has_changes = monkey.has_changes()
            current_exp = monkey.current_experiment()
            recent = monkey.list_saves(limit=5)

            self.send_json({
                'success': True,
                'has_changes': has_changes,
                'current_experiment': current_exp,
                'recent_checkpoints': recent
            })
        except Exception as e:
            self.send_json_error(str(e))

    def api_history(self):
        """Get commit history."""
        try:
            monkey = self.get_monkey()
            entries = monkey.what_happened(limit=30)
            self.send_json({'success': True, 'entries': entries})
        except Exception as e:
            self.send_json_error(str(e))

    def api_checkpoints(self):
        """Get checkpoints."""
        try:
            monkey = self.get_monkey()
            checkpoints = monkey.list_saves(limit=30)
            self.send_json({'success': True, 'checkpoints': checkpoints})
        except Exception as e:
            self.send_json_error(str(e))

    def api_experiments(self):
        """Get experiments."""
        try:
            monkey = self.get_monkey()
            experiments = monkey.list_experiments()
            self.send_json({'success': True, 'experiments': experiments})
        except Exception as e:
            self.send_json_error(str(e))

    def api_save(self, data):
        """Create a checkpoint."""
        try:
            monkey = self.get_monkey()
            message = data.get('message', '')
            if not message:
                self.send_json_error('Message is required')
                return

            checkpoint = monkey.save(message, include_untracked=True)
            self.send_json({'success': True, 'checkpoint': checkpoint})
        except Exception as e:
            self.send_json_error(str(e))

    def api_quick_save(self, data):
        """Create a quick save."""
        try:
            monkey = self.get_monkey()
            checkpoint = monkey.quick_save('Quick save')
            self.send_json({'success': True, 'checkpoint': checkpoint})
        except Exception as e:
            self.send_json_error(str(e))

    def api_undo(self, data):
        """Undo to previous checkpoint."""
        try:
            monkey = self.get_monkey()
            monkey.undo(keep_changes=True)
            self.send_json({'success': True, 'message': 'Restored to previous checkpoint'})
        except Exception as e:
            self.send_json_error(str(e))

    def api_restore(self, data):
        """Restore to a checkpoint."""
        try:
            monkey = self.get_monkey()
            checkpoint_id = data.get('checkpoint_id', '')
            if not checkpoint_id:
                self.send_json_error('Checkpoint ID is required')
                return

            monkey.restore(checkpoint_id, keep_changes=True)
            self.send_json({'success': True, 'message': f'Restored to {checkpoint_id}'})
        except Exception as e:
            self.send_json_error(str(e))

    def api_experiment_create(self, data):
        """Create an experiment."""
        try:
            monkey = self.get_monkey()
            name = data.get('name', '')
            description = data.get('description', '')
            if not name:
                self.send_json_error('Name is required')
                return

            experiment = monkey.try_something(name, description)
            self.send_json({'success': True, 'experiment': experiment})
        except Exception as e:
            self.send_json_error(str(e))

    def api_experiment_switch(self, data):
        """Switch to an experiment."""
        try:
            monkey = self.get_monkey()
            name = data.get('name', '')
            if not name:
                self.send_json_error('Name is required')
                return

            monkey.switch_to(name)
            self.send_json({'success': True, 'message': f'Switched to {name}'})
        except Exception as e:
            self.send_json_error(str(e))

    def api_experiment_keep(self, data):
        """Keep an experiment."""
        try:
            monkey = self.get_monkey()
            name = data.get('name')
            monkey.keep_experiment(name)
            self.send_json({'success': True, 'message': 'Experiment merged'})
        except Exception as e:
            self.send_json_error(str(e))

    def api_experiment_discard(self, data):
        """Discard an experiment."""
        try:
            monkey = self.get_monkey()
            name = data.get('name')
            monkey.discard_experiment(name)
            self.send_json({'success': True, 'message': 'Experiment discarded'})
        except Exception as e:
            self.send_json_error(str(e))


def run_simple_web(repo_path: Optional[Path] = None, port: int = 8080, open_browser: bool = True):
    """Run the simple web server."""
    # Set repo path for handler
    BranchMonkeyHandler.set_repo_path(repo_path)

    # Create server
    server = HTTPServer(('127.0.0.1', port), BranchMonkeyHandler)

    # Auto-open browser
    if open_browser:
        def open_browser_delayed():
            import time
            time.sleep(1.5)
            webbrowser.open(f'http://localhost:{port}')

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    print(f"\n🐵 Branch Monkey Web Interface")
    print(f"   Running on http://localhost:{port}")
    print(f"   Press Ctrl+C to quit\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
