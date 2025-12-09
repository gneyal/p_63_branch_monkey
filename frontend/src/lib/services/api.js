/**
 * API service layer for Branch Monkey
 * Handles all communication with the FastAPI backend
 */

import { noBackendDetected, isDemoMode } from '../stores/store.js';
import { get } from 'svelte/store';
import { DEMO_DATA } from './demoData.js';

const API_BASE = '/api';

/**
 * Check if we're in demo mode and return demo data
 */
function inDemoMode() {
  return get(isDemoMode);
}

/**
 * Helper to safely parse JSON response
 * Detects when HTML is returned instead of JSON (no backend running)
 */
async function safeJsonParse(response, errorPrefix) {
  const text = await response.text();

  // Check if we got HTML instead of JSON (no backend)
  if (text.trim().startsWith('<!') || text.trim().startsWith('<html')) {
    // Don't show modal in demo mode - the demo API handles this
    if (!get(isDemoMode)) {
      noBackendDetected.set(true);
    }
    throw new Error('Backend not running - this app requires local installation');
  }

  try {
    return JSON.parse(text);
  } catch (e) {
    // If JSON parsing fails, might also be HTML
    if (text.includes('<!doctype') || text.includes('<html')) {
      // Don't show modal in demo mode
      if (!get(isDemoMode)) {
        noBackendDetected.set(true);
      }
      throw new Error('Backend not running - this app requires local installation');
    }
    throw new Error(`${errorPrefix}: Invalid response format`);
  }
}

/**
 * Fetch the commit tree
 * @param {number} limit - Number of commits to fetch
 * @param {number} offset - Number of commits to skip
 * @returns {Promise<Object>} Commit tree data
 */
export async function fetchCommitTree(limit = 50, offset = 0) {
  if (inDemoMode()) return DEMO_DATA.commitTree;
  const response = await fetch(`${API_BASE}/commit-tree?limit=${limit}&offset=${offset}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch commit tree: ${response.statusText}`);
  }
  return safeJsonParse(response, 'Failed to fetch commit tree');
}

/**
 * Fetch all experiments
 * @returns {Promise<Array>} List of experiments
 */
export async function fetchExperiments() {
  if (inDemoMode()) return DEMO_DATA.experiments;
  const response = await fetch(`${API_BASE}/experiments`);
  if (!response.ok) {
    throw new Error(`Failed to fetch experiments: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Create a new experiment
 * @param {string} name - Experiment name
 * @param {string} description - Experiment description
 * @returns {Promise<Object>} Created experiment
 */
export async function createExperiment(name, description = '') {
  const response = await fetch(`${API_BASE}/experiment/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      description,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create experiment');
  }

  return response.json();
}

/**
 * Switch to an experiment
 * @param {string} experimentName - Name of experiment to switch to
 * @returns {Promise<Object>} Response
 */
export async function switchExperiment(experimentName) {
  const response = await fetch(`${API_BASE}/experiment/switch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: experimentName,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to switch experiment');
  }

  return response.json();
}

/**
 * Keep (merge) an experiment
 * @param {string} experimentName - Name of experiment to merge
 * @returns {Promise<Object>} Response
 */
export async function keepExperiment(experimentName) {
  const response = await fetch(`${API_BASE}/experiment/keep`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: experimentName,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to keep experiment');
  }

  return response.json();
}

/**
 * Discard an experiment
 * @param {string} experimentName - Name of experiment to discard
 * @returns {Promise<Object>} Response
 */
export async function discardExperiment(experimentName) {
  const response = await fetch(`${API_BASE}/experiment/discard`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: experimentName,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to discard experiment');
  }

  return response.json();
}

/**
 * Fetch notes for a commit
 * @param {string} sha - Commit SHA
 * @returns {Promise<Array>} List of notes
 */
export async function fetchNotes(sha) {
  if (inDemoMode()) return DEMO_DATA.notes.notes;
  const response = await fetch(`${API_BASE}/notes/${sha}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch notes: ${response.statusText}`);
  }
  const data = await response.json();
  return data.notes || [];
}

/**
 * Add a note to a commit
 * @param {string} sha - Commit SHA
 * @param {string} text - Note text
 * @returns {Promise<Object>} Created note
 */
export async function addNote(sha, text) {
  const response = await fetch(`${API_BASE}/notes/${sha}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to add note');
  }

  return response.json();
}

/**
 * Delete a note from a commit
 * @param {string} sha - Commit SHA
 * @param {number} noteId - Note ID to delete
 * @returns {Promise<Array>} Remaining notes
 */
export async function deleteNote(sha, noteId) {
  const response = await fetch(`${API_BASE}/notes/${sha}/${noteId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete note');
  }

  const data = await response.json();
  return data.notes || [];
}

/**
 * Get current repository info
 * @returns {Promise<Object>} Repository information
 */
export async function fetchRepoInfo() {
  if (inDemoMode()) return DEMO_DATA.repoInfo;
  const response = await fetch(`${API_BASE}/repo/info`);
  if (!response.ok) {
    throw new Error(`Failed to fetch repo info: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Set the current repository path
 * @param {string} path - Repository path
 * @returns {Promise<Object>} Response
 */
export async function setRepoPath(path) {
  const response = await fetch(`${API_BASE}/repo/set`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ path }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to set repository path');
  }

  return response.json();
}

/**
 * Get the example project path for the tour
 * @returns {Promise<Object>} Example project info
 */
export async function getExampleProject() {
  const response = await fetch(`${API_BASE}/example-project`);
  if (!response.ok) {
    throw new Error('Failed to get example project');
  }
  return response.json();
}

/**
 * Search for repository paths
 * @param {string} query - Search query
 * @returns {Promise<Array>} List of matching paths
 */
export async function searchRepoPaths(query) {
  const response = await fetch(`${API_BASE}/repo/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Failed to search paths: ${response.statusText}`);
  }

  const data = await response.json();
  return data.suggestions || [];
}

/**
 * Create a new branch at a specific commit
 * @param {string} name - Branch name
 * @param {string} fromCommit - Commit SHA to create branch from (optional)
 * @returns {Promise<Object>} Response
 */
export async function createBranch(name, fromCommit = null) {
  const response = await fetch(`${API_BASE}/branch/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      from_commit: fromCommit
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create branch');
  }

  return response.json();
}

/**
 * Get all branches
 * @returns {Promise<Object>} Branches data with list and current branch
 */
export async function fetchBranches() {
  if (inDemoMode()) return DEMO_DATA.branches;
  const response = await fetch(`${API_BASE}/branches`);
  if (!response.ok) {
    throw new Error(`Failed to fetch branches: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get working tree status
 * @returns {Promise<Object>} Working tree status with staged, modified, and untracked counts
 */
export async function fetchWorkingTreeStatus() {
  if (inDemoMode()) return DEMO_DATA.workingTree;
  const response = await fetch(`${API_BASE}/working-tree`);
  if (!response.ok) {
    throw new Error(`Failed to fetch working tree status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get remote tracking status
 * @returns {Promise<Object>} Remote status with ahead/behind counts
 */
export async function fetchRemoteStatus() {
  if (inDemoMode()) return DEMO_DATA.remoteStatus;
  const response = await fetch(`${API_BASE}/remote/status`);
  if (!response.ok) {
    throw new Error(`Failed to fetch remote status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get prompt for a commit
 * @param {string} sha - Commit SHA
 * @returns {Promise<Object>} Prompt data with prompt text and timestamp
 */
export async function fetchPrompt(sha) {
  const response = await fetch(`${API_BASE}/prompts/${sha}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch prompt: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Save or update prompt for a commit
 * @param {string} sha - Commit SHA
 * @param {string} promptText - Prompt text to save
 * @returns {Promise<Object>} Saved prompt data
 */
export async function savePrompt(sha, promptText) {
  const response = await fetch(`${API_BASE}/prompts/${sha}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt: promptText }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save prompt');
  }

  return response.json();
}

/**
 * Delete prompt for a commit
 * @param {string} sha - Commit SHA
 * @returns {Promise<Object>} Delete result
 */
export async function deletePrompt(sha) {
  const response = await fetch(`${API_BASE}/prompts/${sha}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete prompt');
  }

  return response.json();
}

/**
 * Get all prompts for the current repository
 * @returns {Promise<Object>} All prompts with commit info
 */
export async function fetchAllPrompts() {
  if (inDemoMode()) return DEMO_DATA.allPrompts;
  const response = await fetch(`${API_BASE}/prompts/all/list`);
  if (!response.ok) {
    throw new Error(`Failed to fetch prompts: ${response.statusText}`);
  }
  return response.json();
}

// === Context Library API ===

/**
 * Get counts of summaries for each context type
 * @returns {Promise<Object>} Counts by type
 */
export async function fetchContextCounts() {
  if (inDemoMode()) return DEMO_DATA.contextCounts;
  const response = await fetch(`${API_BASE}/context/counts`);
  if (!response.ok) {
    throw new Error(`Failed to fetch context counts: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get the AI prompt for generating a context summary
 * @param {string} contextType - One of 'codebase', 'architecture', 'prompts'
 * @returns {Promise<Object>} Prompt data
 */
export async function fetchContextPrompt(contextType) {
  const response = await fetch(`${API_BASE}/context/prompt/${contextType}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch context prompt: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Save an AI-generated context summary
 * @param {string} contextType - One of 'codebase', 'architecture', 'prompts'
 * @param {string} content - The summary content
 * @returns {Promise<Object>} Saved entry
 */
export async function saveContextSummary(contextType, content) {
  const response = await fetch(`${API_BASE}/context/save/${contextType}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content }),
  });
  if (!response.ok) {
    throw new Error(`Failed to save context summary: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get historical summaries for a context type
 * @param {string} contextType - One of 'codebase', 'architecture', 'prompts'
 * @param {number} limit - Maximum entries to return
 * @returns {Promise<Object>} History data
 */
export async function fetchContextHistory(contextType, limit = 50) {
  if (inDemoMode()) return DEMO_DATA.contextHistory[contextType] || { entries: [] };
  const response = await fetch(`${API_BASE}/context/history/${contextType}?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch context history: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get a specific context entry by ID
 * @param {number} entryId - Entry ID
 * @returns {Promise<Object>} Entry data
 */
export async function fetchContextEntry(entryId) {
  const response = await fetch(`${API_BASE}/context/entry/${entryId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch context entry: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Delete a context entry
 * @param {number} entryId - Entry ID to delete
 * @returns {Promise<Object>} Delete result
 */
export async function deleteContextEntry(entryId) {
  const response = await fetch(`${API_BASE}/context/entry/${entryId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete context entry: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get the latest summary for a context type
 * @param {string} contextType - One of 'codebase', 'architecture', 'prompts'
 * @returns {Promise<Object>} Latest entry
 */
export async function fetchLatestContext(contextType) {
  if (inDemoMode()) {
    const history = DEMO_DATA.contextHistory[contextType];
    return { entry: history?.entries?.[0] || null };
  }
  const response = await fetch(`${API_BASE}/context/latest/${contextType}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch latest context: ${response.statusText}`);
  }
  return response.json();
}

// === Tasks API ===

/**
 * Fetch all tasks for the current repository
 * @returns {Promise<Object>} Tasks data
 */
export async function fetchTasks() {
  if (inDemoMode()) return DEMO_DATA.tasks;
  const response = await fetch(`${API_BASE}/tasks`);
  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`);
  }
  return safeJsonParse(response, 'Failed to fetch tasks');
}

/**
 * Create a new task
 * @param {Object} task - Task data
 * @returns {Promise<Object>} Created task
 */
export async function createTask(task) {
  const response = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  });
  if (!response.ok) {
    throw new Error(`Failed to create task: ${response.statusText}`);
  }
  return safeJsonParse(response, 'Failed to create task');
}

/**
 * Update a task
 * @param {number} taskId - Task ID
 * @param {Object} updates - Task updates
 * @returns {Promise<Object>} Updated task
 */
export async function updateTask(taskId, updates) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });
  if (!response.ok) {
    throw new Error(`Failed to update task: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Delete a task
 * @param {number} taskId - Task ID
 * @returns {Promise<Object>} Delete result
 */
export async function deleteTask(taskId) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete task: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Reorder tasks
 * @param {Array<number>} taskIds - Array of task IDs in desired order
 * @returns {Promise<Object>} Reorder result
 */
export async function reorderTasks(taskIds) {
  const response = await fetch(`${API_BASE}/tasks/reorder`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ task_ids: taskIds }),
  });
  if (!response.ok) {
    throw new Error(`Failed to reorder tasks: ${response.statusText}`);
  }
  return response.json();
}

// === Versions API ===

/**
 * Fetch all versions for the current repository
 * @returns {Promise<Object>} Versions data
 */
export async function fetchVersions() {
  if (inDemoMode()) return DEMO_DATA.versions;
  const response = await fetch(`${API_BASE}/versions`);
  if (!response.ok) {
    throw new Error(`Failed to fetch versions: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Create a new version
 * @param {Object} version - Version data (key, label, sort_order)
 * @returns {Promise<Object>} Created version
 */
export async function createVersion(version) {
  const response = await fetch(`${API_BASE}/versions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(version),
  });
  if (!response.ok) {
    throw new Error(`Failed to create version: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Update a version
 * @param {string} versionKey - Version key
 * @param {Object} updates - Version updates (label, sort_order)
 * @returns {Promise<Object>} Updated version
 */
export async function updateVersion(versionKey, updates) {
  const response = await fetch(`${API_BASE}/versions/${versionKey}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });
  if (!response.ok) {
    throw new Error(`Failed to update version: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Delete a version and move its tasks to target_version
 * @param {string} versionKey - Version key to delete
 * @param {string} targetVersion - Version to move tasks to
 * @returns {Promise<Object>} Delete result
 */
export async function deleteVersion(versionKey, targetVersion = 'backlog') {
  const response = await fetch(`${API_BASE}/versions/${versionKey}?target_version=${targetVersion}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete version: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Reorder versions
 * @param {Array<string>} order - Array of version keys in desired order
 * @returns {Promise<Object>} Reorder result
 */
export async function reorderVersions(order) {
  const response = await fetch(`${API_BASE}/versions/reorder`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ order }),
  });
  if (!response.ok) {
    throw new Error(`Failed to reorder versions: ${response.statusText}`);
  }
  return response.json();
}

// === Prompt Logs API ===

/**
 * Fetch prompt logs for the current repository
 * @param {Object} options - Query options
 * @param {number} options.limit - Max results (default 100)
 * @param {number} options.offset - Offset for pagination
 * @param {string} options.session_id - Filter by session ID
 * @param {string} options.provider - Filter by provider
 * @param {string} options.status - Filter by status
 * @returns {Promise<Object>} Prompt logs data
 */
export async function fetchPromptLogs(options = {}) {
  if (inDemoMode()) return DEMO_DATA.promptLogs;
  const params = new URLSearchParams();
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  if (options.session_id) params.append('session_id', options.session_id);
  if (options.provider) params.append('provider', options.provider);
  if (options.status) params.append('status', options.status);

  const queryString = params.toString();
  const url = `${API_BASE}/prompt-logs${queryString ? '?' + queryString : ''}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch prompt logs: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Log a new prompt interaction
 * @param {Object} promptData - Prompt data
 * @returns {Promise<Object>} Created prompt log entry
 */
export async function logPrompt(promptData) {
  const response = await fetch(`${API_BASE}/prompt-logs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(promptData),
  });
  if (!response.ok) {
    throw new Error(`Failed to log prompt: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get aggregate statistics for prompt logs
 * @returns {Promise<Object>} Stats data
 */
export async function fetchPromptStats() {
  if (inDemoMode()) return DEMO_DATA.promptLogs.stats;
  const response = await fetch(`${API_BASE}/prompt-logs/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch prompt stats: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Delete a prompt log entry
 * @param {number} promptId - Prompt log ID to delete
 * @returns {Promise<Object>} Delete result
 */
export async function deletePromptLog(promptId) {
  const response = await fetch(`${API_BASE}/prompt-logs/${promptId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete prompt log: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Clear all prompt logs for the current repository
 * @returns {Promise<Object>} Clear result
 */
export async function clearPromptLogs() {
  const response = await fetch(`${API_BASE}/prompt-logs`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to clear prompt logs: ${response.statusText}`);
  }
  return response.json();
}

/**
 * List all git projects in a parent folder
 * @param {string} folderPath - Parent folder path
 * @returns {Promise<Array>} List of projects with name and path
 */
export async function listProjectsInFolder(folderPath) {
  const response = await fetch(`${API_BASE}/repo/list-projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ folder_path: folderPath }),
  });
  if (!response.ok) {
    throw new Error(`Failed to list projects: ${response.statusText}`);
  }
  const data = await response.json();
  return data.projects || [];
}
