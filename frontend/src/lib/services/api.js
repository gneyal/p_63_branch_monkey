/**
 * API service layer for Branch Monkey
 * Handles all communication with the FastAPI backend
 */

const API_BASE = '/api';

/**
 * Fetch the commit tree
 * @param {number} limit - Number of commits to fetch
 * @param {number} offset - Number of commits to skip
 * @returns {Promise<Object>} Commit tree data
 */
export async function fetchCommitTree(limit = 50, offset = 0) {
  const response = await fetch(`${API_BASE}/commit-tree?limit=${limit}&offset=${offset}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch commit tree: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch all experiments
 * @returns {Promise<Array>} List of experiments
 */
export async function fetchExperiments() {
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
  const response = await fetch(`${API_BASE}/prompts/all/list`);
  if (!response.ok) {
    throw new Error(`Failed to fetch prompts: ${response.statusText}`);
  }
  return response.json();
}

// === Context Library API ===

/**
 * Get status of all context files
 * @returns {Promise<Object>} Context files status
 */
export async function fetchContextStatus() {
  const response = await fetch(`${API_BASE}/context/status`);
  if (!response.ok) {
    throw new Error(`Failed to fetch context status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Update all context files
 * @returns {Promise<Object>} Update result
 */
export async function updateAllContext() {
  const response = await fetch(`${API_BASE}/context/update`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to update context: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get a specific context file content
 * @param {string} fileName - Name of the context file
 * @returns {Promise<Object>} File content
 */
export async function fetchContextFile(fileName) {
  const response = await fetch(`${API_BASE}/context/${encodeURIComponent(fileName)}`);
  if (!response.ok) {
    if (response.status === 404) {
      return { success: true, content: null };
    }
    throw new Error(`Failed to fetch context file: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Update only codebase context
 * @returns {Promise<Object>} Update result
 */
export async function updateCodebaseContext() {
  const response = await fetch(`${API_BASE}/context/update/codebase`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to update codebase context: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Update only architecture context
 * @returns {Promise<Object>} Update result
 */
export async function updateArchitectureContext() {
  const response = await fetch(`${API_BASE}/context/update/architecture`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to update architecture context: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Update only prompts context
 * @returns {Promise<Object>} Update result
 */
export async function updatePromptsContext() {
  const response = await fetch(`${API_BASE}/context/update/prompts`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to update prompts context: ${response.statusText}`);
  }
  return response.json();
}
