#!/usr/bin/env python
"""Simple test of web server."""

from flask import Flask, jsonify
from waitress import serve
from branch_monkey.api import BranchMonkey

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Branch Monkey Web</h1><p>Server is running!</p>"

@app.route('/api/test')
def test_api():
    try:
        monkey = BranchMonkey()
        return jsonify({'success': True, 'message': 'BranchMonkey initialized'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting simple test server on http://localhost:8080")
    serve(app, host='127.0.0.1', port=8080)
