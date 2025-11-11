"""Flask web application for Branch Monkey."""

import webbrowser
import threading
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from ..api import BranchMonkey


def create_app(repo_path: Optional[Path] = None):
    """Create and configure Flask app."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for local development

    # Store repo path in app config
    app.config['REPO_PATH'] = repo_path

    def get_monkey():
        """Get Branch Monkey instance (lazy initialization)."""
        return BranchMonkey(app.config['REPO_PATH'])

    @app.route('/')
    def index():
        """Main dashboard."""
        return render_template('index.html')

    @app.route('/api/status')
    def get_status():
        """Get current status."""
        try:
            monkey = get_monkey()
            has_changes = monkey.has_changes()
            current_exp = monkey.current_experiment()
            recent = monkey.list_saves(limit=5)

            return jsonify({
                'success': True,
                'has_changes': has_changes,
                'current_experiment': current_exp,
                'recent_checkpoints': recent
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/history')
    def get_history():
        """Get commit history."""
        try:
            monkey = get_monkey()
            limit = int(request.args.get('limit', 20))
            entries = monkey.what_happened(limit)
            return jsonify({'success': True, 'entries': entries})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/checkpoints')
    def get_checkpoints():
        """Get checkpoints list."""
        try:
            monkey = get_monkey()
            limit = int(request.args.get('limit', 20))
            checkpoints = monkey.list_saves(limit)
            return jsonify({'success': True, 'checkpoints': checkpoints})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/experiments')
    def get_experiments():
        """Get experiments list."""
        try:
            monkey = get_monkey()
            experiments = monkey.list_experiments()
            return jsonify({'success': True, 'experiments': experiments})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/save', methods=['POST'])
    def save_checkpoint():
        """Create a new checkpoint."""
        try:
            monkey = get_monkey()
            data = request.json
            message = data.get('message', '')
            include_untracked = data.get('include_untracked', True)

            if not message:
                return jsonify({'success': False, 'error': 'Message is required'}), 400

            checkpoint = monkey.save(message, include_untracked=include_untracked)
            return jsonify({'success': True, 'checkpoint': checkpoint})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/quick-save', methods=['POST'])
    def quick_save():
        """Create a quick save."""
        try:
            monkey = get_monkey()
            data = request.json or {}
            message = data.get('message', 'Quick save')

            checkpoint = monkey.quick_save(message)
            return jsonify({'success': True, 'checkpoint': checkpoint})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/restore', methods=['POST'])
    def restore_checkpoint():
        """Restore to a checkpoint."""
        try:
            monkey = get_monkey()
            data = request.json
            checkpoint_id = data.get('checkpoint_id', '')
            keep_changes = data.get('keep_changes', True)

            if not checkpoint_id:
                return jsonify({'success': False, 'error': 'Checkpoint ID is required'}), 400

            monkey.restore(checkpoint_id, keep_changes=keep_changes)
            return jsonify({'success': True, 'message': f'Restored to {checkpoint_id}'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/undo', methods=['POST'])
    def undo():
        """Undo to previous checkpoint."""
        try:
            monkey = get_monkey()
            data = request.json or {}
            keep_changes = data.get('keep_changes', True)

            monkey.undo(keep_changes=keep_changes)
            return jsonify({'success': True, 'message': 'Restored to previous checkpoint'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/experiment/create', methods=['POST'])
    def create_experiment():
        """Create a new experiment."""
        try:
            monkey = get_monkey()
            data = request.json
            name = data.get('name', '')
            description = data.get('description', '')

            if not name:
                return jsonify({'success': False, 'error': 'Name is required'}), 400

            experiment = monkey.try_something(name, description)
            return jsonify({'success': True, 'experiment': experiment})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/experiment/switch', methods=['POST'])
    def switch_experiment():
        """Switch to an experiment."""
        try:
            monkey = get_monkey()
            data = request.json
            name = data.get('name', '')

            if not name:
                return jsonify({'success': False, 'error': 'Name is required'}), 400

            monkey.switch_to(name)
            return jsonify({'success': True, 'message': f'Switched to {name}'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/experiment/keep', methods=['POST'])
    def keep_experiment():
        """Keep (merge) an experiment."""
        try:
            monkey = get_monkey()
            data = request.json
            name = data.get('name')

            monkey.keep_experiment(name)
            return jsonify({'success': True, 'message': 'Experiment merged successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/experiment/discard', methods=['POST'])
    def discard_experiment():
        """Discard an experiment."""
        try:
            monkey = get_monkey()
            data = request.json
            name = data.get('name')

            monkey.discard_experiment(name)
            return jsonify({'success': True, 'message': 'Experiment discarded'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/search')
    def search_history():
        """Search history."""
        try:
            monkey = get_monkey()
            query = request.args.get('query', '')
            search_in = request.args.get('where', 'message')

            if not query:
                return jsonify({'success': False, 'error': 'Query is required'}), 400

            results = monkey.search(query, search_in=search_in)
            return jsonify({'success': True, 'results': results})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/diff/<checkpoint_id>')
    def get_diff(checkpoint_id):
        """Get diff for a checkpoint."""
        try:
            monkey = get_monkey()
            diff = monkey.show_changes(checkpoint_id)
            return jsonify({'success': True, 'diff': diff})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    return app


def run_web(repo_path: Optional[Path] = None, port: int = 8080, open_browser: bool = True):
    """Run the web interface."""
    from waitress import serve

    app = create_app(repo_path)

    # Auto-open browser after a short delay
    if open_browser:
        def open_browser_delayed():
            import time
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f'http://localhost:{port}')

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    print(f"\n🐵 Branch Monkey Web Interface")
    print(f"   Running on http://localhost:{port}")
    print(f"   Press Ctrl+C to quit\n")

    # Run with waitress (production-ready WSGI server)
    serve(app, host='127.0.0.1', port=port)
