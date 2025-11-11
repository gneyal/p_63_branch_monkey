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
    <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
    <style>
        :root {
            --bg-primary: #111827;
            --bg-secondary: #1f2937;
            --bg-tertiary: #374151;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --border-color: #4b5563;
            --canvas-bg: #111827;
        }

        [data-theme="light"] {
            --bg-primary: #ffffff;
            --bg-secondary: #f3f4f6;
            --bg-tertiary: #e5e7eb;
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --border-color: #d1d5db;
            --canvas-bg: #f9fafb;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }

        .bg-themed {
            background-color: var(--bg-secondary);
        }

        .bg-canvas {
            background-color: var(--canvas-bg);
        }

        .text-themed {
            color: var(--text-primary);
        }

        .text-secondary-themed {
            color: var(--text-secondary);
        }
    </style>
</head>
<body class="transition-colors duration-200">
    <div class="container mx-auto p-3 max-w-6xl">
        <div class="flex justify-between items-center mb-2">
            <h1 class="text-lg font-bold">🐵 Branch Monkey</h1>
            <button onclick="toggleTheme()" id="themeToggle" class="px-2 py-1 rounded text-xs bg-gray-700 hover:bg-gray-600" title="Toggle theme">
                <span id="themeIcon">🌙</span>
            </button>
        </div>

        <!-- Repository Selector - Compact -->
        <div class="bg-gray-800 rounded p-2 mb-3">
            <div class="flex gap-2 items-center">
                <button onclick="toggleFavorite()" id="btnFavorite" class="bg-yellow-600 hover:bg-yellow-700 px-2 py-1 rounded text-xs flex-none" title="Favorite">★</button>
                <div class="relative flex-1">
                    <input type="text" id="repoPath" placeholder="Repository path..."
                           class="bg-gray-700 px-2 py-1 rounded w-full text-xs font-mono"
                           autocomplete="off">
                    <div id="autocomplete" class="absolute z-10 w-full bg-gray-700 rounded mt-1 shadow-lg hidden max-h-60 overflow-y-auto"></div>
                </div>
                <button onclick="changeRepo()" class="bg-purple-600 hover:bg-purple-700 px-2 py-1 rounded text-xs flex-none">Switch</button>
            </div>
            <div id="currentRepo" class="text-gray-500 text-xs mt-1 truncate" title=""></div>

            <!-- Favorites - Collapsible -->
            <div id="favorites" class="mt-2 hidden">
                <div id="favoritesList" class="flex flex-col gap-1"></div>
            </div>
        </div>

        <!-- MAIN FEATURE: Commit Tree Visualization -->
        <div class="bg-gray-800 rounded-lg p-3 mb-3">
            <div class="flex justify-between items-center mb-2">
                <h2 class="text-lg font-bold">🌳 Commit Tree</h2>
                <div class="text-xs text-gray-400">Drag to pan, scroll to zoom, click nodes to navigate</div>
            </div>
            <div id="canvasContainer" class="w-full rounded overflow-hidden" style="height: 500px;">
                <canvas id="commitTree" class="bg-canvas" style="display: block;"></canvas>
            </div>
        </div>

        <!-- Actions -->
        <div class="bg-gray-800 rounded-lg p-3 mb-3">
            <h2 class="text-lg font-bold mb-2">Actions</h2>
            <div class="space-y-2">
                <div class="flex gap-2">
                    <input type="text" id="saveMessage" placeholder="Save message..."
                           class="bg-gray-700 px-2 py-1 rounded flex-1 text-xs">
                    <button onclick="save()" class="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs flex-none">
                        Save
                    </button>
                </div>
                <div class="flex gap-2">
                    <button onclick="quickSave()" class="bg-yellow-600 hover:bg-yellow-700 px-2 py-1 rounded text-xs flex-1">
                        Quick Save
                    </button>
                    <button onclick="undo()" class="bg-orange-600 hover:bg-orange-700 px-2 py-1 rounded text-xs flex-1">
                        Undo
                    </button>
                </div>
            </div>
        </div>

        <!-- Checkpoints -->
        <div class="bg-gray-800 rounded-lg p-3 mb-3">
            <h2 class="text-lg font-bold mb-2">Checkpoints</h2>
            <div id="checkpoints" class="space-y-1"></div>
        </div>

        <!-- Experiments -->
        <div class="bg-gray-800 rounded-lg p-3 mb-3">
            <h2 class="text-lg font-bold mb-2">Experiments</h2>
            <div class="space-y-2 mb-2">
                <input type="text" id="expName" placeholder="Name..."
                       class="bg-gray-700 px-2 py-1 rounded text-xs w-full">
                <input type="text" id="expDesc" placeholder="Description..."
                       class="bg-gray-700 px-2 py-1 rounded text-xs w-full">
                <button onclick="createExperiment()" class="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs w-full">
                    Create
                </button>
            </div>
            <div id="experiments" class="space-y-1"></div>
        </div>

        <!-- History -->
        <div class="bg-gray-800 rounded-lg p-3">
            <h2 class="text-lg font-bold mb-2">History</h2>
            <div id="history" class="space-y-1"></div>
        </div>
    </div>

    <script>
        // Theme management
        function getTheme() {
            return localStorage.getItem('branchMonkeyTheme') || 'dark';
        }

        function setTheme(theme) {
            localStorage.setItem('branchMonkeyTheme', theme);
            document.documentElement.setAttribute('data-theme', theme);

            // Update icon
            const icon = document.getElementById('themeIcon');
            icon.textContent = theme === 'light' ? '🌙' : '☀️';

            // Redraw canvas with new theme
            if (commitTreeData) {
                drawCommitTree(commitTreeData);
            }
        }

        function toggleTheme() {
            const currentTheme = getTheme();
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        }

        // Initialize theme on load
        document.addEventListener('DOMContentLoaded', () => {
            setTheme(getTheme());
        });

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

        // Favorites management
        function getFavorites() {
            const favs = localStorage.getItem('branchMonkeyFavorites');
            return favs ? JSON.parse(favs) : [];
        }

        function saveFavorites(favorites) {
            localStorage.setItem('branchMonkeyFavorites', JSON.stringify(favorites));
        }

        function isFavorite(path) {
            const favorites = getFavorites();
            return favorites.includes(path);
        }

        function toggleFavorite() {
            const data = branchesData;
            if (!data) return;

            const currentPath = document.getElementById('currentRepo').textContent.replace('Current: ', '');
            const favorites = getFavorites();
            const index = favorites.indexOf(currentPath);

            if (index >= 0) {
                // Remove from favorites
                favorites.splice(index, 1);
                alert('Removed from favorites');
            } else {
                // Add to favorites
                favorites.push(currentPath);
                alert('Added to favorites!');
            }

            saveFavorites(favorites);
            updateFavoriteButton(currentPath);
            renderFavorites();
        }

        function updateFavoriteButton(path) {
            const btn = document.getElementById('btnFavorite');
            if (isFavorite(path)) {
                btn.classList.remove('bg-yellow-600', 'hover:bg-yellow-700');
                btn.classList.add('bg-yellow-400', 'hover:bg-yellow-500');
                btn.title = 'Remove from favorites';
            } else {
                btn.classList.remove('bg-yellow-400', 'hover:bg-yellow-500');
                btn.classList.add('bg-yellow-600', 'hover:bg-yellow-700');
                btn.title = 'Add to favorites';
            }
        }

        function renderFavorites() {
            const favorites = getFavorites();
            const container = document.getElementById('favorites');
            const list = document.getElementById('favoritesList');

            if (favorites.length === 0) {
                container.classList.add('hidden');
                return;
            }

            container.classList.remove('hidden');

            const html = favorites.map(path => {
                const shortPath = path.split('/').slice(-2).join('/');
                return `
                    <div class="flex items-center gap-2 bg-gray-700 px-2 py-1 rounded text-xs">
                        <button onclick="switchToFavorite('${path}')" class="hover:text-blue-400 font-mono truncate flex-1 text-left" title="${path}">
                            ${shortPath}
                        </button>
                        <button onclick="removeFavorite('${path}')" class="text-red-400 hover:text-red-300 flex-none" title="Remove">
                            ×
                        </button>
                    </div>
                `;
            }).join('');

            list.innerHTML = html;
        }

        async function switchToFavorite(path) {
            document.getElementById('repoPath').value = path;
            await changeRepo();
        }

        function removeFavorite(path) {
            const favorites = getFavorites();
            const index = favorites.indexOf(path);
            if (index >= 0) {
                favorites.splice(index, 1);
                saveFavorites(favorites);
                renderFavorites();
                updateFavoriteButton(document.getElementById('currentRepo').textContent.replace('Current: ', ''));
            }
        }

        async function loadRepoInfo() {
            const data = await api('/repo/info');
            const currentPath = data.path;
            document.getElementById('currentRepo').textContent = `Current: ${currentPath}`;
            document.getElementById('repoPath').placeholder = currentPath;
            updateFavoriteButton(currentPath);
            renderFavorites();
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
                <div class="px-2 py-1 hover:bg-gray-600 cursor-pointer text-xs font-mono autocomplete-item"
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
            const branchData = await api('/branches');
            const currentBranch = branchData.current;

            document.getElementById('status').innerHTML = `
                <div class="space-y-1 text-xs">
                    <div>🐵 Current: <span class="text-green-400 font-bold">${currentBranch}</span></div>
                    <div>Changes: <span class="${data.has_changes ? 'text-yellow-400' : 'text-green-400'}">${data.has_changes ? 'Yes' : 'No'}</span></div>
                    ${data.current_experiment ? `<div>Experiment: <span class="text-blue-400">${data.current_experiment.name}</span></div>` : ''}
                </div>
            `;
        }

        async function loadCheckpoints() {
            const data = await api('/checkpoints');
            const html = data.checkpoints.map(cp => `
                <div class="flex justify-between items-start bg-gray-700 p-2 rounded">
                    <div class="flex-1 min-w-0">
                        <div>
                            <span class="text-cyan-400 font-mono text-xs">${cp.short_id}</span>
                            <span class="text-gray-400 text-xs ml-2">${cp.age}</span>
                        </div>
                        <div class="text-xs mt-1 truncate">${cp.message}</div>
                    </div>
                    <button onclick="restore('${cp.short_id}')"
                            class="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs ml-2 flex-none">
                        Restore
                    </button>
                </div>
            `).join('');
            document.getElementById('checkpoints').innerHTML = html || '<div class="text-gray-400 text-xs">No checkpoints yet</div>';
        }

        async function loadExperiments() {
            const data = await api('/experiments');
            const html = data.experiments.map(exp => `
                <div class="bg-gray-700 p-2 rounded ${exp.is_active ? 'border-2 border-blue-500' : ''}">
                    <div class="mb-2">
                        <span class="font-bold text-xs">${exp.name}</span>
                        ${exp.is_active ? '<span class="text-blue-400 ml-2 text-xs">● Active</span>' : ''}
                        ${exp.description ? `<div class="text-xs text-gray-400 mt-1 truncate">${exp.description}</div>` : ''}
                    </div>
                    <div class="flex gap-1">
                        ${!exp.is_active ? `<button onclick="switchExperiment('${exp.name}')" class="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs flex-1">Switch</button>` : ''}
                        <button onclick="keepExperiment('${exp.name}')" class="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs flex-1">Keep</button>
                        <button onclick="discardExperiment('${exp.name}')" class="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs flex-1">Discard</button>
                    </div>
                </div>
            `).join('');
            document.getElementById('experiments').innerHTML = html || '<div class="text-gray-400 text-xs">No experiments yet</div>';
        }

        let commitTreeData = null;

        async function loadCommitTree() {
            const data = await api('/commit-tree');
            commitTreeData = data;
            drawCommitTree(data);
        }

        // Pan and zoom state
        let panOffset = { x: 0, y: 0 };
        let zoomLevel = 1.0;
        let isDragging = false;
        let dragStart = { x: 0, y: 0 };

        function drawCommitTree(data) {
            const canvas = document.getElementById('commitTree');
            const ctx = canvas.getContext('2d');

            // Set canvas size to match displayed size (only if not set or changed)
            const rect = canvas.getBoundingClientRect();
            const needsResize = canvas.width !== rect.width || canvas.height !== rect.height;
            if (needsResize) {
                canvas.width = rect.width;
                canvas.height = rect.height;
            }

            // Get theme colors
            const isLight = getTheme() === 'light';
            const bgColor = isLight ? '#f9fafb' : '#111827';
            const textColor = isLight ? '#111827' : '#f3f4f6';
            const textSecondary = isLight ? '#6b7280' : '#9ca3af';
            const lineColor = isLight ? '#d1d5db' : '#4b5563';

            // Reset transformations and clear entire canvas
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.fillStyle = bgColor;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Apply pan and zoom transformations
            ctx.translate(panOffset.x, panOffset.y);
            ctx.scale(zoomLevel, zoomLevel);

            if (!data.commits || data.commits.length === 0) {
                ctx.fillStyle = textSecondary;
                ctx.font = '14px monospace';
                ctx.fillText('No commits yet', 20, 30);
                return;
            }

            const commits = data.commits;
            const nodeRadius = 10;
            const verticalSpacing = 60;
            const columnSpacing = 50;
            const startX = 60;
            const startY = 30;
            const branchColors = ['#60a5fa', '#34d399', '#fbbf24', '#f472b6', '#a78bfa', '#fb923c', '#c084fc'];

            // Build commit map
            const commitMap = {};
            commits.forEach((commit, i) => {
                commitMap[commit.sha] = i;
            });

            // Assign columns to commits based on branches
            const branchToColumn = {};
            const usedColumns = new Set();

            // Reserve column 0 for main/master branch
            branchToColumn['main'] = 0;
            branchToColumn['master'] = 0;
            let nextColumn = 1;

            // First pass: assign columns based on branch names
            commits.forEach((commit, i) => {
                if (commit.branches.length > 0) {
                    // Commit has branches - assign it to a column for that branch
                    const mainBranch = commit.branches[0];
                    if (branchToColumn[mainBranch] === undefined) {
                        branchToColumn[mainBranch] = nextColumn++;
                    }
                    commit.column = branchToColumn[mainBranch];
                    commit.color = branchColors[commit.column % branchColors.length];
                } else if (commit.parents.length > 0) {
                    // No branch label - inherit from parent
                    const parentIdx = commitMap[commit.parents[0]];
                    if (parentIdx !== undefined && commits[parentIdx].column !== undefined) {
                        commit.column = commits[parentIdx].column;
                        commit.color = commits[parentIdx].color;
                    } else {
                        commit.column = 0;
                        commit.color = branchColors[0];
                    }
                } else {
                    // Root commit
                    commit.column = 0;
                    commit.color = branchColors[0];
                }
                usedColumns.add(commit.column);
            });

            const commitPositions = commits.map((commit, i) => {
                return {
                    x: startX + commit.column * columnSpacing,
                    y: startY + i * verticalSpacing,
                    commit: commit
                };
            });

            // Draw connecting lines first (with branch colors)
            ctx.lineWidth = 3;
            commitPositions.forEach((pos, i) => {
                const commit = pos.commit;
                commit.parents.forEach(parentSha => {
                    const parentIdx = commitMap[parentSha];
                    if (parentIdx !== undefined) {
                        const parentPos = commitPositions[parentIdx];

                        // Use the commit's branch color for the line
                        ctx.strokeStyle = commit.color || lineColor;
                        ctx.beginPath();
                        ctx.moveTo(pos.x, pos.y);

                        // If parent is in different column, draw curved line
                        if (Math.abs(pos.x - parentPos.x) > 5) {
                            const midY = (pos.y + parentPos.y) / 2;
                            ctx.bezierCurveTo(
                                pos.x, midY,
                                parentPos.x, midY,
                                parentPos.x, parentPos.y
                            );
                        } else {
                            ctx.lineTo(parentPos.x, parentPos.y);
                        }
                        ctx.stroke();
                    }
                });
            });

            // Draw commit nodes
            canvas.clickAreas = [];
            commitPositions.forEach((pos, i) => {
                const commit = pos.commit;
                const x = pos.x;
                const y = pos.y;

                // Draw node circle
                ctx.beginPath();
                ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI);
                ctx.fillStyle = commit.is_head ? '#fbbf24' : commit.color;
                ctx.fill();
                ctx.strokeStyle = commit.is_head ? '#f59e0b' : (isLight ? '#374151' : '#1f2937');
                ctx.lineWidth = 2;
                ctx.stroke();

                // Draw monkey emoji at HEAD
                if (commit.is_head) {
                    ctx.font = '20px sans-serif';
                    ctx.fillText('🐵', x - 10, y - 15);
                }

                // Draw commit message (truncated)
                ctx.fillStyle = textColor;
                ctx.font = 'bold 11px monospace';
                const maxLen = 40;
                const message = commit.message.length > maxLen ? commit.message.substring(0, maxLen) + '...' : commit.message;
                ctx.fillText(message, x + 20, y);

                // Draw SHA and age
                ctx.fillStyle = textSecondary;
                ctx.font = '10px monospace';
                ctx.fillText(`${commit.sha} • ${commit.age}`, x + 20, y + 12);

                // Draw branch labels
                if (commit.branches.length > 0) {
                    commit.branches.forEach((branch, idx) => {
                        const branchY = y + 25 + idx * 12;
                        // Use the commit's branch color for the label background
                        ctx.fillStyle = commit.color;
                        ctx.fillRect(x + 20, branchY - 10, ctx.measureText(branch).width + 6, 12);
                        ctx.fillStyle = '#ffffff';
                        ctx.font = 'bold 9px sans-serif';
                        ctx.fillText(branch, x + 23, branchY);
                    });
                }

                // Store click area
                canvas.clickAreas.push({
                    x: x - nodeRadius,
                    y: y - nodeRadius,
                    width: nodeRadius * 2,
                    height: nodeRadius * 2,
                    commit: commit
                });
            });
        }

        // Helper function to transform screen coordinates to canvas coordinates
        function screenToCanvas(x, y) {
            return {
                x: (x - panOffset.x) / zoomLevel,
                y: (y - panOffset.y) / zoomLevel
            };
        }

        // Add event handlers for commit tree
        document.addEventListener('DOMContentLoaded', () => {
            const canvas = document.getElementById('commitTree');

            // Mouse down - start dragging
            canvas.addEventListener('mousedown', (e) => {
                isDragging = true;
                dragStart = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
                canvas.style.cursor = 'grabbing';
            });

            // Mouse up - stop dragging
            canvas.addEventListener('mouseup', () => {
                isDragging = false;
                canvas.style.cursor = 'default';
            });

            // Mouse leave - stop dragging
            canvas.addEventListener('mouseleave', () => {
                isDragging = false;
                canvas.style.cursor = 'default';
            });

            // Mouse move - handle dragging and hover
            canvas.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    // Update pan offset
                    panOffset.x = e.clientX - dragStart.x;
                    panOffset.y = e.clientY - dragStart.y;
                    if (commitTreeData) {
                        drawCommitTree(commitTreeData);
                    }
                    return;
                }

                // Check hover for cursor change
                if (!canvas.clickAreas) return;

                const rect = canvas.getBoundingClientRect();
                const screenX = e.clientX - rect.left;
                const screenY = e.clientY - rect.top;
                const canvasCoords = screenToCanvas(screenX, screenY);

                let isOverNode = false;
                canvas.clickAreas.forEach(area => {
                    if (canvasCoords.x >= area.x && canvasCoords.x <= area.x + area.width &&
                        canvasCoords.y >= area.y && canvasCoords.y <= area.y + area.height) {
                        isOverNode = true;
                    }
                });

                canvas.style.cursor = isOverNode ? 'pointer' : 'grab';
            });

            // Click handler with coordinate transformation
            canvas.addEventListener('click', (e) => {
                if (!canvas.clickAreas) return;

                const rect = canvas.getBoundingClientRect();
                const screenX = e.clientX - rect.left;
                const screenY = e.clientY - rect.top;
                const canvasCoords = screenToCanvas(screenX, screenY);

                canvas.clickAreas.forEach(area => {
                    if (canvasCoords.x >= area.x && canvasCoords.x <= area.x + area.width &&
                        canvasCoords.y >= area.y && canvasCoords.y <= area.y + area.height) {
                        const commit = area.commit;

                        // If commit has branches, switch to the first branch
                        if (commit.branches.length > 0) {
                            switchBranch(commit.branches[0]);
                        } else if (!commit.is_head) {
                            // Otherwise checkout the commit SHA directly
                            if (confirm(`Checkout commit ${commit.sha}?\n\n${commit.message}\n\nThis will put you in detached HEAD state.`)) {
                                checkoutCommit(commit.sha);
                            }
                        }
                    }
                });
            });

            // Wheel handler for zooming
            canvas.addEventListener('wheel', (e) => {
                e.preventDefault();

                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                // Get canvas coordinates before zoom
                const canvasBefore = screenToCanvas(mouseX, mouseY);

                // Update zoom level
                const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
                zoomLevel *= zoomFactor;
                zoomLevel = Math.max(0.1, Math.min(5, zoomLevel)); // Clamp between 0.1 and 5

                // Get canvas coordinates after zoom
                const canvasAfter = screenToCanvas(mouseX, mouseY);

                // Adjust pan offset to keep mouse position fixed
                panOffset.x += (canvasAfter.x - canvasBefore.x) * zoomLevel;
                panOffset.y += (canvasAfter.y - canvasBefore.y) * zoomLevel;

                if (commitTreeData) {
                    drawCommitTree(commitTreeData);
                }
            });
        });

        async function loadHistory() {
            const data = await api('/history');
            const html = data.entries.slice(0, 10).map(entry => `
                <div class="bg-gray-700 p-2 rounded">
                    <div class="flex items-center gap-2 text-xs">
                        <span class="text-cyan-400 font-mono">${entry.short_sha}</span>
                        <span class="text-gray-400">${entry.age}</span>
                        <span class="text-yellow-400 truncate">${entry.author}</span>
                    </div>
                    <div class="text-xs mt-1 truncate">${entry.message.split('\\n')[0]}</div>
                </div>
            `).join('');
            document.getElementById('history').innerHTML = html || '<div class="text-gray-400 text-xs">No history yet</div>';
        }

        async function switchBranch(name) {
            if (confirm(`Switch to branch "${name}"?`)) {
                // Simple git checkout via API
                await api('/branch/switch', 'POST', { name });
                loadAll();
            }
        }

        async function checkoutCommit(sha) {
            await api('/branch/switch', 'POST', { name: sha });
            loadAll();
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
            loadCommitTree();
            loadStatus();
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


@app.get("/api/commit-tree")
def get_commit_tree():
    """Get commit tree with parent relationships for visualization."""
    import subprocess
    try:
        # Get current HEAD
        current_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_PATH,
            text=True
        ).strip()[:7]

        # Get all branches with their SHAs
        branch_output = subprocess.check_output(
            ["git", "branch", "-a", "--format=%(refname:short)|%(objectname:short)"],
            cwd=REPO_PATH,
            text=True
        ).strip()

        # Map SHA to branch names
        sha_to_branches = {}
        for line in branch_output.split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 2:
                branch_name, sha = parts
                if sha not in sha_to_branches:
                    sha_to_branches[sha] = []
                sha_to_branches[sha].append(branch_name)

        # Get commit log with parents (limit to last 50 commits for performance)
        log_output = subprocess.check_output(
            ["git", "log", "--all", "--format=%H|%h|%p|%s|%an|%ar", "-50"],
            cwd=REPO_PATH,
            text=True
        ).strip()

        commits = []
        for line in log_output.split('\n'):
            if not line:
                continue
            parts = line.split('|', 5)
            if len(parts) >= 6:
                full_sha, short_sha, parents, subject, author, age = parts
                parent_list = [p[:7] for p in parents.split()] if parents else []

                commits.append({
                    "sha": short_sha,
                    "message": subject,
                    "author": author,
                    "age": age,
                    "parents": parent_list,
                    "branches": sha_to_branches.get(short_sha, []),
                    "is_head": short_sha == current_sha
                })

        return {"success": True, "commits": commits, "current_sha": current_sha}
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


def run_server(repo_path: Optional[Path] = None, port: int = 8081, open_browser: bool = True):
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
