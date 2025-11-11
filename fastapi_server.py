#!/usr/bin/env python3
"""FastAPI server for Branch Monkey."""

import webbrowser
import threading
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from branch_monkey.api import BranchMonkey

app = FastAPI(title="Branch Monkey Web API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store repo path
REPO_PATH: Optional[Path] = None


def get_monkey():
    """Get BranchMonkey instance."""
    try:
        return BranchMonkey(REPO_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not initialize BranchMonkey: {str(e)}")


class SaveRequest(BaseModel):
    message: str


class RestoreRequest(BaseModel):
    checkpoint_id: str


class ExperimentRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class RepoRequest(BaseModel):
    path: str


class PathSearchRequest(BaseModel):
    query: str


# HTML Frontend
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Branch Monkey</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100">
    <div class="container mx-auto p-6 max-w-6xl">
        <h1 class="text-4xl font-bold mb-6">🐵 Branch Monkey</h1>

        <!-- Repository Selector -->
        <div class="bg-gray-800 rounded-lg p-4 mb-6">
            <div class="flex items-center gap-4">
                <span class="text-gray-400 text-sm">Repository:</span>
                <div class="flex-1 relative">
                    <input type="text" id="repoPath" placeholder="Enter repository path..."
                           class="bg-gray-700 px-4 py-2 rounded w-full text-sm font-mono"
                           autocomplete="off">
                    <div id="autocomplete" class="absolute z-10 w-full bg-gray-700 rounded mt-1 shadow-lg hidden max-h-60 overflow-y-auto"></div>
                </div>
                <button onclick="changeRepo()" class="bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded">
                    Switch Repo
                </button>
            </div>
            <div id="currentRepo" class="text-gray-500 text-xs mt-2"></div>
        </div>

        <!-- Status -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-2xl font-bold mb-4">Status</h2>
            <div id="status" class="text-gray-400">Loading...</div>
        </div>

        <!-- Branches -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-2xl font-bold">Branches</h2>
                <div class="flex gap-2">
                    <button onclick="showBranchView('list')" id="btnListView" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded">
                        List View
                    </button>
                    <button onclick="showBranchView('graph')" id="btnGraphView" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded">
                        Graph View
                    </button>
                </div>
            </div>
            <div id="branchListView" class="space-y-2"></div>
            <canvas id="branchGraphView" class="hidden w-full" height="400"></canvas>
        </div>

        <!-- Actions -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-2xl font-bold mb-4">Actions</h2>
            <div class="flex gap-4 flex-wrap">
                <div class="flex gap-2">
                    <input type="text" id="saveMessage" placeholder="Save message..."
                           class="bg-gray-700 px-4 py-2 rounded flex-1 min-w-64">
                    <button onclick="save()" class="bg-green-600 hover:bg-green-700 px-6 py-2 rounded">
                        Save
                    </button>
                </div>
                <button onclick="quickSave()" class="bg-yellow-600 hover:bg-yellow-700 px-6 py-2 rounded">
                    Quick Save
                </button>
                <button onclick="undo()" class="bg-orange-600 hover:bg-orange-700 px-6 py-2 rounded">
                    Undo
                </button>
            </div>
        </div>

        <!-- Checkpoints -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-2xl font-bold mb-4">Checkpoints</h2>
            <div id="checkpoints" class="space-y-2"></div>
        </div>

        <!-- Experiments -->
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-2xl font-bold mb-4">Experiments</h2>
            <div class="flex gap-2 mb-4">
                <input type="text" id="expName" placeholder="Experiment name..."
                       class="bg-gray-700 px-4 py-2 rounded">
                <input type="text" id="expDesc" placeholder="Description..."
                       class="bg-gray-700 px-4 py-2 rounded flex-1">
                <button onclick="createExperiment()" class="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded">
                    Create
                </button>
            </div>
            <div id="experiments" class="space-y-2"></div>
        </div>

        <!-- History -->
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-bold mb-4">History</h2>
            <div id="history" class="space-y-2"></div>
        </div>
    </div>

    <script>
        async function api(endpoint, method = 'GET', body = null) {
            try {
                const options = { method };
                if (body) {
                    options.headers = { 'Content-Type': 'application/json' };
                    options.body = JSON.stringify(body);
                }
                const response = await fetch(`/api${endpoint}`, options);
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'Request failed');
                return data;
            } catch (error) {
                alert('Error: ' + error.message);
                throw error;
            }
        }

        async function loadRepoInfo() {
            const data = await api('/repo/info');
            document.getElementById('currentRepo').textContent = `Current: ${data.path}`;
            document.getElementById('repoPath').placeholder = data.path;
        }

        let autocompleteTimeout = null;
        let selectedIndex = -1;

        async function searchPaths(query) {
            if (!query) {
                hideAutocomplete();
                return;
            }

            clearTimeout(autocompleteTimeout);
            autocompleteTimeout = setTimeout(async () => {
                try {
                    const data = await api('/repo/search', 'POST', { query });
                    showAutocomplete(data.suggestions);
                } catch (error) {
                    hideAutocomplete();
                }
            }, 300);
        }

        function showAutocomplete(suggestions) {
            const container = document.getElementById('autocomplete');
            if (!suggestions || suggestions.length === 0) {
                hideAutocomplete();
                return;
            }

            selectedIndex = -1;
            const html = suggestions.map((path, idx) => `
                <div class="px-4 py-2 hover:bg-gray-600 cursor-pointer text-sm font-mono autocomplete-item"
                     data-path="${path}"
                     data-index="${idx}"
                     onclick="selectPath('${path}')">
                    ${path}
                </div>
            `).join('');

            container.innerHTML = html;
            container.classList.remove('hidden');
        }

        function hideAutocomplete() {
            document.getElementById('autocomplete').classList.add('hidden');
            selectedIndex = -1;
        }

        function selectPath(path) {
            document.getElementById('repoPath').value = path;
            hideAutocomplete();
        }

        function handleKeyNavigation(e) {
            const container = document.getElementById('autocomplete');
            const items = container.querySelectorAll('.autocomplete-item');

            if (items.length === 0) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                updateSelection(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection(items);
            } else if (e.key === 'Enter' && selectedIndex >= 0) {
                e.preventDefault();
                const path = items[selectedIndex].dataset.path;
                selectPath(path);
            } else if (e.key === 'Escape') {
                hideAutocomplete();
            }
        }

        function updateSelection(items) {
            items.forEach((item, idx) => {
                if (idx === selectedIndex) {
                    item.classList.add('bg-gray-600');
                } else {
                    item.classList.remove('bg-gray-600');
                }
            });
        }

        // Setup event listeners for autocomplete
        document.addEventListener('DOMContentLoaded', () => {
            const input = document.getElementById('repoPath');
            input.addEventListener('input', (e) => searchPaths(e.target.value));
            input.addEventListener('keydown', handleKeyNavigation);

            // Hide autocomplete when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('#repoPath') && !e.target.closest('#autocomplete')) {
                    hideAutocomplete();
                }
            });
        });

        async function changeRepo() {
            const path = document.getElementById('repoPath').value;
            if (!path) return alert('Please enter a repository path');
            try {
                await api('/repo/set', 'POST', { path });
                alert('Repository changed! Reloading...');
                loadAll();
            } catch (error) {
                // Error already shown by api() function
            }
        }

        async function loadStatus() {
            const data = await api('/status');
            document.getElementById('status').innerHTML = `
                <div class="space-y-2">
                    <div>Changes: <span class="${data.has_changes ? 'text-yellow-400' : 'text-green-400'}">${data.has_changes ? 'Yes' : 'No'}</span></div>
                    ${data.current_experiment ? `<div>Experiment: <span class="text-blue-400">${data.current_experiment.name}</span></div>` : ''}
                </div>
            `;
        }

        async function loadCheckpoints() {
            const data = await api('/checkpoints');
            const html = data.checkpoints.map(cp => `
                <div class="flex justify-between items-center bg-gray-700 p-3 rounded">
                    <div>
                        <span class="text-cyan-400 font-mono">${cp.short_id}</span>
                        <span class="text-gray-400 text-sm ml-3">${cp.age}</span>
                        <div class="text-sm mt-1">${cp.message}</div>
                    </div>
                    <button onclick="restore('${cp.short_id}')"
                            class="bg-blue-600 hover:bg-blue-700 px-4 py-1 rounded text-sm">
                        Restore
                    </button>
                </div>
            `).join('');
            document.getElementById('checkpoints').innerHTML = html || '<div class="text-gray-400">No checkpoints yet</div>';
        }

        async function loadExperiments() {
            const data = await api('/experiments');
            const html = data.experiments.map(exp => `
                <div class="flex justify-between items-center bg-gray-700 p-3 rounded ${exp.is_active ? 'border-2 border-blue-500' : ''}">
                    <div>
                        <span class="font-bold">${exp.name}</span>
                        ${exp.is_active ? '<span class="text-blue-400 ml-2">● Active</span>' : ''}
                        ${exp.description ? `<div class="text-sm text-gray-400 mt-1">${exp.description}</div>` : ''}
                    </div>
                    <div class="flex gap-2">
                        ${!exp.is_active ? `<button onclick="switchExperiment('${exp.name}')" class="bg-blue-600 hover:bg-blue-700 px-4 py-1 rounded text-sm">Switch</button>` : ''}
                        <button onclick="keepExperiment('${exp.name}')" class="bg-green-600 hover:bg-green-700 px-4 py-1 rounded text-sm">Keep</button>
                        <button onclick="discardExperiment('${exp.name}')" class="bg-red-600 hover:bg-red-700 px-4 py-1 rounded text-sm">Discard</button>
                    </div>
                </div>
            `).join('');
            document.getElementById('experiments').innerHTML = html || '<div class="text-gray-400">No experiments yet</div>';
        }

        let currentBranchView = 'list';
        let branchesData = null;

        async function loadBranches() {
            const data = await api('/branches');
            branchesData = data;

            // Update list view
            const html = data.branches.map(branch => `
                <div class="flex justify-between items-center bg-gray-700 p-4 rounded ${branch.is_current ? 'border-2 border-green-500' : ''}">
                    <div class="flex-1">
                        <div class="flex items-center gap-3">
                            <span class="text-lg font-bold ${branch.is_current ? 'text-green-400' : 'text-blue-400'}">${branch.name}</span>
                            ${branch.is_current ? '<span class="text-green-400 text-sm">● Current</span>' : ''}
                        </div>
                        <div class="text-sm text-gray-400 mt-1">
                            <span class="font-mono">${branch.sha}</span>
                            <span class="mx-2">•</span>
                            <span>${branch.age}</span>
                        </div>
                        <div class="text-sm mt-1">${branch.message}</div>
                    </div>
                    ${!branch.is_current ? `<button onclick="switchBranch('${branch.name}')" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded ml-4">Switch</button>` : ''}
                </div>
            `).join('');
            document.getElementById('branchListView').innerHTML = html || '<div class="text-gray-400">No branches</div>';

            // Update graph view if that's the current view
            if (currentBranchView === 'graph') {
                drawBranchGraph(data);
            }
        }

        function showBranchView(view) {
            currentBranchView = view;
            const listView = document.getElementById('branchListView');
            const graphView = document.getElementById('branchGraphView');
            const btnList = document.getElementById('btnListView');
            const btnGraph = document.getElementById('btnGraphView');

            if (view === 'list') {
                listView.classList.remove('hidden');
                graphView.classList.add('hidden');
                btnList.classList.add('bg-blue-600');
                btnList.classList.remove('bg-gray-700');
                btnGraph.classList.remove('bg-blue-600');
                btnGraph.classList.add('bg-gray-700');
            } else {
                listView.classList.add('hidden');
                graphView.classList.remove('hidden');
                btnGraph.classList.add('bg-blue-600');
                btnGraph.classList.remove('bg-gray-700');
                btnList.classList.remove('bg-blue-600');
                btnList.classList.add('bg-gray-700');
                if (branchesData) {
                    drawBranchGraph(branchesData);
                }
            }
        }

        function drawBranchGraph(data) {
            const canvas = document.getElementById('branchGraphView');
            const ctx = canvas.getContext('2d');

            // Clear canvas
            ctx.fillStyle = '#1f2937';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            if (!data.branches || data.branches.length === 0) {
                ctx.fillStyle = '#9ca3af';
                ctx.font = '14px monospace';
                ctx.fillText('No branches', 20, 30);
                return;
            }

            const branches = data.branches;
            const nodeRadius = 8;
            const horizontalSpacing = 150;
            const verticalSpacing = 80;
            const startX = 100;
            const startY = 50;

            // Draw lines first (so they appear behind nodes)
            ctx.strokeStyle = '#4b5563';
            ctx.lineWidth = 2;

            // Simple layout: arrange branches vertically
            branches.forEach((branch, i) => {
                const y = startY + i * verticalSpacing;

                // Draw line to parent (simplified - just draw to previous for now)
                if (i > 0) {
                    ctx.beginPath();
                    ctx.moveTo(startX, startY + (i-1) * verticalSpacing);
                    ctx.lineTo(startX, y);
                    ctx.stroke();
                }
            });

            // Draw nodes and labels
            branches.forEach((branch, i) => {
                const x = startX;
                const y = startY + i * verticalSpacing;

                // Draw node circle
                ctx.beginPath();
                ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI);
                ctx.fillStyle = branch.is_current ? '#34d399' : '#60a5fa';
                ctx.fill();
                ctx.strokeStyle = branch.is_current ? '#10b981' : '#3b82f6';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Draw branch name
                ctx.fillStyle = '#f3f4f6';
                ctx.font = 'bold 14px monospace';
                ctx.fillText(branch.name, x + 20, y + 5);

                // Draw commit info
                ctx.fillStyle = '#9ca3af';
                ctx.font = '12px monospace';
                ctx.fillText(`${branch.sha} • ${branch.age}`, x + 20, y + 22);

                // Draw current indicator
                if (branch.is_current) {
                    ctx.fillStyle = '#34d399';
                    ctx.font = '12px sans-serif';
                    ctx.fillText('● Current', x + 20, y - 10);
                }

                // Make it clickable (store click areas)
                if (!canvas.clickAreas) canvas.clickAreas = [];
                canvas.clickAreas[i] = {
                    x: x - nodeRadius,
                    y: y - nodeRadius,
                    width: nodeRadius * 2,
                    height: nodeRadius * 2,
                    branch: branch
                };
            });
        }

        // Add click handler for graph view
        document.addEventListener('DOMContentLoaded', () => {
            const canvas = document.getElementById('branchGraphView');
            canvas.addEventListener('click', (e) => {
                if (currentBranchView !== 'graph' || !canvas.clickAreas) return;

                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                canvas.clickAreas.forEach(area => {
                    if (x >= area.x && x <= area.x + area.width &&
                        y >= area.y && y <= area.y + area.height) {
                        if (!area.branch.is_current) {
                            switchBranch(area.branch.name);
                        }
                    }
                });
            });

            // Show cursor pointer on hover
            canvas.addEventListener('mousemove', (e) => {
                if (currentBranchView !== 'graph' || !canvas.clickAreas) return;

                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                let isOverNode = false;
                canvas.clickAreas.forEach(area => {
                    if (x >= area.x && x <= area.x + area.width &&
                        y >= area.y && y <= area.y + area.height) {
                        isOverNode = true;
                    }
                });

                canvas.style.cursor = isOverNode ? 'pointer' : 'default';
            });

            // Initialize with list view
            showBranchView('list');
        });

        async function loadHistory() {
            const data = await api('/history');
            const html = data.entries.slice(0, 10).map(entry => `
                <div class="bg-gray-700 p-3 rounded">
                    <div class="flex items-center gap-3">
                        <span class="text-cyan-400 font-mono">${entry.short_sha}</span>
                        <span class="text-gray-400 text-sm">${entry.age}</span>
                        <span class="text-yellow-400 text-sm">${entry.author}</span>
                    </div>
                    <div class="text-sm mt-1">${entry.message.split('\\n')[0]}</div>
                </div>
            `).join('');
            document.getElementById('history').innerHTML = html || '<div class="text-gray-400">No history yet</div>';
        }

        async function switchBranch(name) {
            if (confirm(`Switch to branch "${name}"?`)) {
                // Simple git checkout via API
                await api('/branch/switch', 'POST', { name });
                loadAll();
            }
        }

        async function save() {
            const message = document.getElementById('saveMessage').value;
            if (!message) return alert('Please enter a message');
            await api('/save', 'POST', { message });
            document.getElementById('saveMessage').value = '';
            loadAll();
        }

        async function quickSave() {
            await api('/quick-save', 'POST', { message: 'Quick save' });
            loadAll();
        }

        async function undo() {
            if (confirm('Undo to previous checkpoint?')) {
                await api('/undo', 'POST');
                loadAll();
            }
        }

        async function restore(checkpoint_id) {
            if (confirm(`Restore to ${checkpoint_id}?`)) {
                await api('/restore', 'POST', { checkpoint_id });
                loadAll();
            }
        }

        async function createExperiment() {
            const name = document.getElementById('expName').value;
            const description = document.getElementById('expDesc').value;
            if (!name) return alert('Please enter a name');
            await api('/experiment/create', 'POST', { name, description });
            document.getElementById('expName').value = '';
            document.getElementById('expDesc').value = '';
            loadAll();
        }

        async function switchExperiment(name) {
            await api('/experiment/switch', 'POST', { name });
            loadAll();
        }

        async function keepExperiment(name) {
            if (confirm(`Keep experiment "${name}"?`)) {
                await api('/experiment/keep', 'POST', { name });
                loadAll();
            }
        }

        async function discardExperiment(name) {
            if (confirm(`Discard experiment "${name}"? This cannot be undone.`)) {
                await api('/experiment/discard', 'POST', { name });
                loadAll();
            }
        }

        function loadAll() {
            loadRepoInfo();
            loadStatus();
            loadBranches();
            loadCheckpoints();
            loadExperiments();
            loadHistory();
        }

        // Load on startup
        loadAll();

        // Auto-refresh every 5 seconds
        setInterval(loadAll, 5000);
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the HTML page."""
    return HTML_PAGE


@app.get("/api/status")
def get_status():
    """Get current status."""
    monkey = get_monkey()
    has_changes = monkey.has_changes()
    current_exp = monkey.current_experiment()
    recent = monkey.list_saves(limit=5)

    return {
        "success": True,
        "has_changes": has_changes,
        "current_experiment": current_exp,
        "recent_checkpoints": recent
    }


@app.get("/api/history")
def get_history():
    """Get commit history."""
    monkey = get_monkey()
    entries = monkey.what_happened(limit=30)
    return {"success": True, "entries": entries}


@app.get("/api/checkpoints")
def get_checkpoints():
    """Get checkpoints."""
    monkey = get_monkey()
    checkpoints = monkey.list_saves(limit=30)
    return {"success": True, "checkpoints": checkpoints}


@app.get("/api/experiments")
def get_experiments():
    """Get experiments."""
    monkey = get_monkey()
    experiments = monkey.list_experiments()
    return {"success": True, "experiments": experiments}


@app.get("/api/branches")
def get_branches():
    """Get all branches."""
    import subprocess
    try:
        # Get current branch
        current = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_PATH,
            text=True
        ).strip()

        # Get all branches with info
        output = subprocess.check_output(
            ["git", "branch", "-a", "--format=%(refname:short)|%(committerdate:relative)|%(subject)|%(objectname:short)"],
            cwd=REPO_PATH,
            text=True
        ).strip()

        branches = []
        for line in output.split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) >= 4:
                name, age, message, sha = parts
                branches.append({
                    "name": name,
                    "age": age,
                    "message": message,
                    "sha": sha,
                    "is_current": name == current
                })

        return {"success": True, "branches": branches, "current": current}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/save")
def create_save(request: SaveRequest):
    """Create a checkpoint."""
    monkey = get_monkey()
    checkpoint = monkey.save(request.message, include_untracked=True)
    return {"success": True, "checkpoint": checkpoint}


@app.post("/api/quick-save")
def create_quick_save():
    """Create a quick save."""
    monkey = get_monkey()
    checkpoint = monkey.quick_save("Quick save")
    return {"success": True, "checkpoint": checkpoint}


@app.post("/api/undo")
def undo_checkpoint():
    """Undo to previous checkpoint."""
    monkey = get_monkey()
    monkey.undo(keep_changes=True)
    return {"success": True, "message": "Restored to previous checkpoint"}


@app.post("/api/restore")
def restore_checkpoint(request: RestoreRequest):
    """Restore to a checkpoint."""
    monkey = get_monkey()
    monkey.restore(request.checkpoint_id, keep_changes=True)
    return {"success": True, "message": f"Restored to {request.checkpoint_id}"}


@app.post("/api/experiment/create")
def create_experiment(request: ExperimentRequest):
    """Create an experiment."""
    monkey = get_monkey()
    experiment = monkey.try_something(request.name, request.description)
    return {"success": True, "experiment": experiment}


@app.post("/api/experiment/switch")
def switch_experiment(request: ExperimentRequest):
    """Switch to an experiment."""
    monkey = get_monkey()
    monkey.switch_to(request.name)
    return {"success": True, "message": f"Switched to {request.name}"}


@app.post("/api/experiment/keep")
def keep_experiment(request: ExperimentRequest):
    """Keep an experiment."""
    monkey = get_monkey()
    monkey.keep_experiment(request.name)
    return {"success": True, "message": "Experiment merged"}


@app.post("/api/experiment/discard")
def discard_experiment(request: ExperimentRequest):
    """Discard an experiment."""
    monkey = get_monkey()
    monkey.discard_experiment(request.name)
    return {"success": True, "message": "Experiment discarded"}


@app.post("/api/branch/switch")
def switch_branch(request: ExperimentRequest):
    """Switch to a branch."""
    import subprocess
    try:
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )

        has_changes = bool(result.stdout.strip())

        # If there are changes, stash them first
        if has_changes:
            subprocess.check_call(
                ["git", "stash", "push", "-m", f"Auto-stash before switching to {request.name}"],
                cwd=REPO_PATH,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Switch branch
        subprocess.check_call(
            ["git", "checkout", request.name],
            cwd=REPO_PATH,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        message = f"Switched to {request.name}"
        if has_changes:
            message += " (changes stashed)"

        return {"success": True, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/repo/info")
def get_repo_info():
    """Get current repository information."""
    import os
    path = REPO_PATH if REPO_PATH else Path.cwd()
    return {
        "success": True,
        "path": str(path.absolute()),
        "exists": path.exists(),
        "is_git_repo": (path / ".git").exists()
    }


@app.post("/api/repo/set")
def set_repo_path(request: RepoRequest):
    """Set the repository path."""
    global REPO_PATH
    path = Path(request.path).expanduser().resolve()

    # Validate path
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"Path does not exist: {path}")

    if not (path / ".git").exists():
        raise HTTPException(status_code=400, detail=f"Not a Git repository: {path}")

    REPO_PATH = path
    return {
        "success": True,
        "message": f"Repository changed to {path}",
        "path": str(path)
    }


@app.post("/api/repo/search")
def search_repo_paths(request: PathSearchRequest):
    """Search for directory paths matching the query."""
    import os

    query = request.query.strip()
    if not query:
        return {"success": True, "suggestions": []}

    try:
        # Expand home directory
        query_path = Path(query).expanduser()

        # Determine the directory to search in
        if query.endswith('/') or query.endswith(os.sep):
            # User is typing inside a directory
            search_dir = query_path
            prefix = ""
        else:
            # User is typing a partial name
            search_dir = query_path.parent
            prefix = query_path.name

        # Get absolute path
        if not search_dir.is_absolute():
            search_dir = Path.cwd() / search_dir

        suggestions = []

        if search_dir.exists() and search_dir.is_dir():
            try:
                # List directories
                for item in sorted(search_dir.iterdir()):
                    if item.is_dir() and not item.name.startswith('.'):
                        # Filter by prefix if typing partial name
                        if not prefix or item.name.lower().startswith(prefix.lower()):
                            full_path = str(item)
                            # Mark Git repos with a special indicator
                            is_git_repo = (item / ".git").exists()
                            suggestions.append({
                                "path": full_path,
                                "is_git_repo": is_git_repo
                            })

                # Sort: Git repos first, then alphabetically
                suggestions.sort(key=lambda x: (not x["is_git_repo"], x["path"]))

                # Limit to 10 suggestions
                suggestions = suggestions[:10]

                # Extract just the paths
                paths = [s["path"] for s in suggestions]

                return {"success": True, "suggestions": paths}
            except PermissionError:
                return {"success": True, "suggestions": []}

        return {"success": True, "suggestions": []}

    except Exception as e:
        return {"success": True, "suggestions": []}


def run_server(repo_path: Optional[Path] = None, port: int = 8080, open_browser: bool = True):
    """Run the FastAPI server."""
    global REPO_PATH
    REPO_PATH = repo_path

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

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


if __name__ == "__main__":
    run_server()
