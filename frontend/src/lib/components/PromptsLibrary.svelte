<script>
  import { onMount } from 'svelte';
  import { fetchAllPrompts, deletePrompt } from '../services/api.js';
  import { showToast } from '../stores/store.js';

  export let onClose = () => {};

  let prompts = [];
  let loading = true;
  let error = null;
  let expandedPromptSha = null;

  onMount(async () => {
    await loadPrompts();
  });

  async function loadPrompts() {
    try {
      loading = true;
      const data = await fetchAllPrompts();
      prompts = data.prompts || [];
    } catch (err) {
      error = err.message;
      showToast(`Failed to load prompts: ${err.message}`, 'error');
    } finally {
      loading = false;
    }
  }

  function toggleExpand(sha) {
    expandedPromptSha = expandedPromptSha === sha ? null : sha;
  }

  async function handleDelete(sha) {
    if (!confirm('Are you sure you want to delete this prompt?')) {
      return;
    }

    try {
      await deletePrompt(sha);
      showToast('Prompt deleted', 'success');
      await loadPrompts();
    } catch (err) {
      showToast(`Failed to delete prompt: ${err.message}`, 'error');
    }
  }

  function handleCopy(prompt) {
    navigator.clipboard.writeText(prompt);
    showToast('Prompt copied to clipboard', 'success');
  }

  function handleImprove(prompt) {
    const improvePrompt = `Please analyze and improve the following prompt for clarity, specificity, and effectiveness:\n\n---\n${prompt}\n---\n\nProvide:\n1. An improved version of the prompt\n2. Key improvements made\n3. Suggestions for making it even more effective`;

    navigator.clipboard.writeText(improvePrompt);
    showToast('Improvement request copied! Paste into a new conversation.', 'success');
  }
</script>

<div class="prompts-library-backdrop" on:click={onClose}>
  <div class="prompts-library-panel" on:click|stopPropagation>
    <div class="panel-header">
      <h3>Prompts Library</h3>
      <button class="close-btn" on:click={onClose}>✕</button>
    </div>

    <div class="panel-content">
      {#if loading}
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading prompts...</p>
        </div>
      {:else if error}
        <div class="error">
          <p>{error}</p>
        </div>
      {:else if prompts.length === 0}
        <div class="empty">
          <p>No prompts saved yet</p>
          <p class="empty-hint">Continue chatting with Claude Code and prompts will be auto-captured!</p>
        </div>
      {:else}
        <div class="prompts-table-container">
          <table class="prompts-table">
            <thead>
              <tr>
                <th>Commit</th>
                <th>Message</th>
                <th>Prompt Preview</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each prompts as prompt}
                <tr class="prompt-row">
                  <td class="commit-cell">
                    <span class="sha">{prompt.short_sha}</span>
                    <span class="author">{prompt.commit_author}</span>
                  </td>
                  <td class="message-cell">{prompt.commit_message}</td>
                  <td class="preview-cell">
                    <div class="preview-text" class:expanded={expandedPromptSha === prompt.sha}>
                      {expandedPromptSha === prompt.sha ? prompt.prompt : prompt.prompt_preview}
                    </div>
                    <button
                      class="expand-btn"
                      on:click={() => toggleExpand(prompt.sha)}
                    >
                      {expandedPromptSha === prompt.sha ? 'Collapse' : 'Expand'}
                    </button>
                  </td>
                  <td class="date-cell">{new Date(prompt.timestamp).toLocaleDateString()}</td>
                  <td class="actions-cell">
                    <button
                      class="action-btn improve-btn"
                      on:click={() => handleImprove(prompt.prompt)}
                      title="Copy improvement request to clipboard"
                    >
                      Improve
                    </button>
                    <button
                      class="action-btn copy-btn"
                      on:click={() => handleCopy(prompt.prompt)}
                      title="Copy prompt to clipboard"
                    >
                      Copy
                    </button>
                    <button
                      class="action-btn delete-btn"
                      on:click={() => handleDelete(prompt.sha)}
                      title="Delete prompt"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        <div class="panel-footer">
          <span class="prompt-count">{prompts.length} prompt{prompts.length !== 1 ? 's' : ''} saved</span>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .prompts-library-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .prompts-library-panel {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 95%;
    max-width: 1400px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
    animation: slideUp 0.2s ease;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .panel-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 20px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 2px;
    transition: all 0.15s;
  }

  .close-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .panel-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .loading,
  .error,
  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px;
    color: var(--text-tertiary);
    gap: 16px;
  }

  .empty-hint {
    font-size: 12px;
    opacity: 0.7;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 2px solid var(--border-secondary);
    border-top-color: var(--text-secondary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .prompts-table-container {
    overflow-x: auto;
  }

  .prompts-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }

  .prompts-table thead {
    background: var(--bg-secondary);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .prompts-table th {
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 10px;
    border-bottom: 1px solid var(--border-primary);
  }

  .prompts-table td {
    padding: 16px;
    border-bottom: 1px solid var(--border-secondary);
    vertical-align: top;
  }

  .prompt-row:hover {
    background: var(--bg-hover);
  }

  .commit-cell {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 120px;
  }

  .sha {
    font-family: 'Courier', monospace;
    font-size: 11px;
    color: var(--text-primary);
    font-weight: 500;
  }

  .author {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .message-cell {
    max-width: 200px;
    color: var(--text-primary);
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .preview-cell {
    max-width: 500px;
  }

  .preview-text {
    font-family: 'Courier', monospace;
    font-size: 11px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 8px;
    padding: 8px;
    background: var(--bg-secondary);
    border-radius: 1px;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 100px;
    overflow-y: auto;
  }

  .preview-text.expanded {
    max-height: 400px;
  }

  .expand-btn {
    font-size: 10px;
    padding: 4px 8px;
    background: transparent;
    border: 1px solid var(--border-secondary);
    color: var(--text-secondary);
    border-radius: 1px;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
    transition: all 0.15s;
  }

  .expand-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .date-cell {
    color: var(--text-tertiary);
    font-size: 11px;
    white-space: nowrap;
    min-width: 100px;
  }

  .actions-cell {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    min-width: 220px;
  }

  .action-btn {
    padding: 6px 12px;
    border-radius: 1px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.15s;
    border: 1px solid;
  }

  .improve-btn {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: var(--bg-primary);
  }

  .improve-btn:hover {
    opacity: 0.9;
    box-shadow: var(--shadow-small);
  }

  .copy-btn {
    background: transparent;
    border-color: var(--border-secondary);
    color: var(--text-secondary);
  }

  .copy-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .delete-btn {
    background: transparent;
    border-color: var(--border-secondary);
    color: var(--text-secondary);
  }

  .delete-btn:hover {
    border-color: #ff6b6b;
    color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
  }

  .panel-footer {
    padding: 12px 24px;
    border-top: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .prompt-count {
    font-size: 11px;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
</style>
