#!/usr/bin/env python
"""Test web server with debug output."""

from branch_monkey.web.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask app with debug...")
    app.run(host='127.0.0.1', port=8080, debug=True)
