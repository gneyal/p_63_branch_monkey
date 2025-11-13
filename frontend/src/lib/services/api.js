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
