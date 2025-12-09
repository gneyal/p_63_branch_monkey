/**
 * Static demo data for the web demo tour
 * This data is used when the app is running in demo mode (no backend)
 */

export const DEMO_DATA = {
  repoInfo: {
    name: 'demo-project',
    path: '/demo/demo-project',
    branch: 'main',
    remote_url: 'https://github.com/demo/demo-project',
    is_demo: true
  },

  commitTree: {
    success: true,
    commits: [
      { sha: 'a1b2c3d', fullSha: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0', message: 'Add real-time notifications feature', author: 'Demo User', age: '2 hours ago', timestamp: '2025-12-09 08:00:00 +0000', parents: ['b2c3d4e'], branches: ['main'], is_head: true, has_stash: false, has_notes: false },
      { sha: 'b2c3d4e', fullSha: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1', message: 'Implement dark mode support with 25+ themes', author: 'Demo User', age: '5 hours ago', timestamp: '2025-12-09 05:00:00 +0000', parents: ['c3d4e5f'], branches: [], is_head: false, has_stash: true, has_notes: false },
      { sha: 'c3d4e5f', fullSha: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2', message: 'Create task management kanban board', author: 'Demo User', age: '1 day ago', timestamp: '2025-12-08 10:00:00 +0000', parents: ['d4e5f6a'], branches: [], is_head: false, has_stash: false, has_notes: true },
      { sha: 'd4e5f6a', fullSha: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3', message: 'Add JWT authentication flow', author: 'Demo User', age: '2 days ago', timestamp: '2025-12-07 14:00:00 +0000', parents: ['e5f6a7b'], branches: [], is_head: false, has_stash: false, has_notes: false },
      { sha: 'e5f6a7b', fullSha: 'e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4', message: 'Set up database migrations with Alembic', author: 'Demo User', age: '3 days ago', timestamp: '2025-12-06 09:00:00 +0000', parents: ['f6a7b8c'], branches: [], is_head: false, has_stash: false, has_notes: false },
      { sha: 'f6a7b8c', fullSha: 'f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5', message: 'Initialize FastAPI backend structure', author: 'Demo User', age: '4 days ago', timestamp: '2025-12-05 16:00:00 +0000', parents: ['a7b8c9d'], branches: [], is_head: false, has_stash: false, has_notes: false },
      { sha: 'a7b8c9d', fullSha: 'a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6', message: 'Create Svelte frontend scaffolding', author: 'Demo User', age: '5 days ago', timestamp: '2025-12-04 11:00:00 +0000', parents: ['b8c9d0e'], branches: ['feature/ui'], is_head: false, has_stash: false, has_notes: false },
      { sha: 'b8c9d0e', fullSha: 'b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7', message: 'Add project configuration files', author: 'Demo User', age: '6 days ago', timestamp: '2025-12-03 15:00:00 +0000', parents: ['c9d0e1f'], branches: [], is_head: false, has_stash: false, has_notes: false },
      { sha: 'c9d0e1f', fullSha: 'c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8', message: 'Initial commit - project setup', author: 'Demo User', age: '1 week ago', timestamp: '2025-12-02 10:00:00 +0000', parents: [], branches: [], is_head: false, has_stash: false, has_notes: false }
    ],
    current_sha: 'a1b2c3d',
    total: 9,
    offset: 0,
    limit: 50,
    has_more: false
  },

  tasks: {
    tasks: [
      { id: 1, title: 'Implement user authentication', description: 'Add JWT-based login and registration', status: 'done', priority: 0, sprint: 'v1', sort_order: 0 },
      { id: 2, title: 'Create task management board', description: 'Kanban-style board with drag-and-drop', status: 'done', priority: 1, sprint: 'v1', sort_order: 1 },
      { id: 3, title: 'Add dark mode support', description: 'Implement theme system with multiple color schemes', status: 'done', priority: 1, sprint: 'v1', sort_order: 2 },
      { id: 4, title: 'Set up database migrations', description: 'Alembic migrations for schema changes', status: 'done', priority: 0, sprint: 'v1', sort_order: 3 },
      { id: 5, title: 'Add real-time notifications', description: 'WebSocket-based notification system', status: 'in_progress', priority: 2, sprint: 'v1', sort_order: 4 },
      { id: 6, title: 'Improve error handling', description: 'Better error messages and logging', status: 'in_progress', priority: 0, sprint: 'v1', sort_order: 5 },
      { id: 7, title: 'Implement team collaboration', description: 'Share tasks and boards with team members', status: 'todo', priority: 0, sprint: 'v2', sort_order: 0 },
      { id: 8, title: 'Add file attachments', description: 'Allow attaching files to tasks', status: 'todo', priority: 0, sprint: 'v2', sort_order: 1 },
      { id: 9, title: 'Create mobile app', description: 'React Native app for iOS and Android', status: 'todo', priority: 2, sprint: 'v2', sort_order: 2 },
      { id: 10, title: 'Add integrations', description: 'Connect with GitHub, Slack, Jira', status: 'todo', priority: 1, sprint: 'v2', sort_order: 3 },
      { id: 11, title: 'Implement search', description: 'Full-text search across all content', status: 'todo', priority: 0, sprint: 'v2', sort_order: 4 },
      { id: 12, title: 'Performance optimization', description: 'Improve load times and reduce bundle size', status: 'todo', priority: 2, sprint: 'backlog', sort_order: 0 },
      { id: 13, title: 'Accessibility audit', description: 'Ensure WCAG 2.1 AA compliance', status: 'todo', priority: 0, sprint: 'backlog', sort_order: 1 },
      { id: 14, title: 'Add analytics dashboard', description: 'Usage metrics and charts', status: 'todo', priority: 1, sprint: 'backlog', sort_order: 2 },
      { id: 15, title: 'Write documentation', description: 'User guide and API docs', status: 'todo', priority: 2, sprint: 'backlog', sort_order: 3 },
      { id: 16, title: 'Set up CI/CD', description: 'Automated testing and deployment', status: 'todo', priority: 2, sprint: 'backlog', sort_order: 4 }
    ]
  },

  versions: {
    versions: [
      { id: 1, key: 'v1', label: 'Version 1.0', sort_order: 0 },
      { id: 2, key: 'v2', label: 'Version 2.0', sort_order: 1 }
    ]
  },

  promptLogs: {
    logs: [
      { id: 15, timestamp: '2025-12-04T20:16:55', provider: 'anthropic', model: 'claude-sonnet-4-20250514', input_tokens: 889, output_tokens: 4971, total_tokens: 5860, cost: 0.0772, duration: 5.58, prompt_preview: 'Implement websocket notifications for real-time updates', response_preview: "I'll implement a WebSocket notification system...", status: 'success' },
      { id: 14, timestamp: '2025-12-04T15:16:55', provider: 'anthropic', model: 'claude-3-5-haiku-20241022', input_tokens: 2743, output_tokens: 4789, total_tokens: 7532, cost: 0.0214, duration: 7.92, prompt_preview: 'Create a migration script for the new schema', response_preview: "Here's the Alembic migration script...", status: 'success' },
      { id: 13, timestamp: '2025-12-04T13:16:55', provider: 'anthropic', model: 'claude-3-5-haiku-20241022', input_tokens: 1784, output_tokens: 4260, total_tokens: 6044, cost: 0.0185, duration: 7.01, prompt_preview: 'Fix the race condition in the inventory update', response_preview: 'The race condition occurs when multiple requests update inventory simultaneously...', status: 'success' },
      { id: 12, timestamp: '2025-12-04T09:16:55', provider: 'anthropic', model: 'claude-3-5-haiku-20241022', input_tokens: 1838, output_tokens: 3975, total_tokens: 5813, cost: 0.0174, duration: 1.78, prompt_preview: 'Help me understand the caching strategy', response_preview: 'The caching strategy uses a multi-layer approach...', status: 'success' },
      { id: 11, timestamp: '2025-12-04T03:16:55', provider: 'anthropic', model: 'claude-sonnet-4-20250514', input_tokens: 2884, output_tokens: 1017, total_tokens: 3901, cost: 0.0239, duration: 7.69, prompt_preview: 'Generate API documentation for the orders module', response_preview: '# Orders API Documentation...', status: 'success' },
      { id: 10, timestamp: '2025-12-04T00:16:55', provider: 'anthropic', model: 'claude-sonnet-4-20250514', input_tokens: 2398, output_tokens: 3810, total_tokens: 6208, cost: 0.0643, duration: 7.96, prompt_preview: 'Review this pull request for security vulnerabilities', response_preview: "I've reviewed the PR and found these security concerns...", status: 'success' },
      { id: 9, timestamp: '2025-12-03T19:16:55', provider: 'anthropic', model: 'claude-sonnet-4-20250514', input_tokens: 1036, output_tokens: 2619, total_tokens: 3655, cost: 0.0424, duration: 5.21, prompt_preview: 'Implement rate limiting for the API', response_preview: "Here's a Redis-based rate limiter implementation...", status: 'success' },
      { id: 8, timestamp: '2025-12-03T16:16:55', provider: 'anthropic', model: 'claude-sonnet-4-20250514', input_tokens: 724, output_tokens: 2847, total_tokens: 3571, cost: 0.0449, duration: 4.47, prompt_preview: 'Add error handling for the file upload feature', response_preview: "I'll add comprehensive error handling for file uploads...", status: 'success' }
    ],
    stats: {
      total_prompts: 15,
      total_tokens: 71917,
      total_cost: 1.0654,
      providers: { anthropic: 15 },
      models: { 'claude-opus-4-5-20251101': 3, 'claude-sonnet-4-20250514': 5, 'claude-3-5-haiku-20241022': 7 }
    }
  },

  contextCounts: {
    codebase: 1,
    architecture: 1,
    prompts: 1
  },

  contextHistory: {
    codebase: {
      entries: [{
        id: 1,
        context_type: 'codebase',
        content: `# Codebase Summary

## Overview
This is a modern full-stack web application built with Python (FastAPI) backend and Svelte frontend.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Frontend**: Svelte 5, Vite, TypeScript
- **Styling**: CSS Variables, Custom Theme System

## Directory Structure
\`\`\`
├── backend/
│   ├── api/          # REST API endpoints
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   └── utils/        # Helper functions
├── frontend/
│   ├── src/
│   │   ├── lib/      # Shared components
│   │   ├── routes/   # Page components
│   │   └── stores/   # State management
│   └── static/       # Static assets
└── tests/            # Test suites
\`\`\`

## Key Features
1. **User Authentication** - JWT-based auth with refresh tokens
2. **Real-time Updates** - WebSocket connections for live data
3. **Task Management** - Kanban-style board with drag-and-drop
4. **Analytics Dashboard** - Charts and metrics visualization`,
        created_at: '2025-12-06T10:16:55.007735'
      }]
    },
    architecture: {
      entries: [{
        id: 2,
        context_type: 'architecture',
        content: JSON.stringify({
          name: 'Demo Application',
          version: '1.0.0',
          description: 'A modern full-stack web application',
          entities: [
            { name: 'User', description: 'User account with authentication', fields: ['id', 'email', 'password_hash', 'created_at'] },
            { name: 'Task', description: 'A task item in the kanban board', fields: ['id', 'title', 'description', 'status', 'priority'] },
            { name: 'Project', description: 'A project containing multiple tasks', fields: ['id', 'name', 'description', 'owner_id'] }
          ],
          endpoints: [
            { method: 'GET', path: '/api/tasks', description: 'List all tasks' },
            { method: 'POST', path: '/api/tasks', description: 'Create a new task' },
            { method: 'PUT', path: '/api/tasks/:id', description: 'Update a task' },
            { method: 'DELETE', path: '/api/tasks/:id', description: 'Delete a task' },
            { method: 'GET', path: '/api/users/me', description: 'Get current user' },
            { method: 'POST', path: '/api/auth/login', description: 'User login' }
          ],
          ui_components: [
            { name: 'TaskBoard', description: 'Kanban-style task board with columns' },
            { name: 'TaskCard', description: 'Individual task card with details' },
            { name: 'Header', description: 'Top navigation with user menu' },
            { name: 'Sidebar', description: 'Left sidebar with project list' }
          ],
          tech_stack: [
            { name: 'Python', version: '3.12', category: 'backend' },
            { name: 'FastAPI', version: '0.104', category: 'backend' },
            { name: 'Svelte', version: '5.0', category: 'frontend' },
            { name: 'SQLite', version: '3.x', category: 'database' },
            { name: 'Vite', version: '5.x', category: 'build' }
          ]
        }, null, 2),
        created_at: '2025-12-06T12:16:55.007735'
      }]
    },
    prompts: {
      entries: [{
        id: 3,
        context_type: 'prompts',
        content: `# AI Prompts Analysis

## Usage Statistics
- **Total Prompts**: 47 in the last 7 days
- **Total Tokens**: 156,432 (42,100 input / 114,332 output)
- **Estimated Cost**: $12.45

## Most Common Use Cases
1. **Code Refactoring** (35%) - Improving code quality and structure
2. **Bug Fixes** (25%) - Debugging and fixing issues
3. **Feature Implementation** (20%) - Building new features
4. **Documentation** (12%) - Writing docs and comments
5. **Code Review** (8%) - Reviewing PRs and code quality

## Key Insights
- Most prompts are focused on backend development
- Average prompt length: ~900 tokens
- Average response length: ~2,400 tokens
- Peak usage: weekday afternoons`,
        created_at: '2025-12-06T14:16:55.007735'
      }]
    }
  },

  branches: {
    branches: ['main', 'feature/ui', 'develop'],
    current: 'main'
  },

  workingTree: {
    staged: 0,
    modified: 0,
    untracked: 0,
    has_changes: false
  },

  remoteStatus: {
    ahead: 0,
    behind: 0,
    remote_sha: 'a1b2c3d'
  },

  experiments: [],

  allPrompts: {
    prompts: []
  },

  notes: {
    notes: []
  }
};
