<script>
  import { onMount } from 'svelte';
  import {
    fetchContextPrompt,
    fetchContextHistory,
    fetchContextEntry,
    saveContextSummary,
    deleteContextEntry
  } from '../services/api.js';
  import { showToast } from '../stores/store.js';

  export let onClose = () => {};

  let history = [];
  let loading = true;
  let loadingHistory = false;
  let selectedEntry = null;
  let showPromptModal = false;
  let showSaveModal = false;
  let currentPrompt = '';
  let saveContent = '';
  let saving = false;

  onMount(async () => {
    await loadHistory();
    loading = false;
  });

  async function loadHistory() {
    try {
      loadingHistory = true;
      const data = await fetchContextHistory('architecture');
      history = data.history || [];
    } catch (err) {
      showToast(`Failed to load history: ${err.message}`, 'error');
      history = [];
    } finally {
      loadingHistory = false;
    }
  }

  async function handleEntryClick(entry) {
    try {
      const data = await fetchContextEntry(entry.id);
      selectedEntry = data.entry;
    } catch (err) {
      showToast(`Failed to load entry: ${err.message}`, 'error');
    }
  }

  async function handleGeneratePrompt() {
    try {
      const data = await fetchContextPrompt('architecture');
      currentPrompt = data.prompt;
      showPromptModal = true;
    } catch (err) {
      showToast(`Failed to get prompt: ${err.message}`, 'error');
    }
  }

  function handleCopyPrompt() {
    navigator.clipboard.writeText(currentPrompt);
    showToast('Prompt copied to clipboard! Paste it in your AI tool.', 'success');
  }

  function handleOpenSaveModal() {
    saveContent = '';
    showSaveModal = true;
  }

  async function handleSave() {
    if (!saveContent.trim()) {
      showToast('Please enter the summary content', 'error');
      return;
    }

    try {
      saving = true;
      await saveContextSummary('architecture', saveContent);
      showToast('Summary saved successfully!', 'success');
      showSaveModal = false;
      saveContent = '';
      await loadHistory();
    } catch (err) {
      showToast(`Failed to save: ${err.message}`, 'error');
    } finally {
      saving = false;
    }
  }

  async function handleDelete(entryId) {
    if (!confirm('Are you sure you want to delete this summary?')) {
      return;
    }

    try {
      await deleteContextEntry(entryId);
      showToast('Summary deleted', 'success');
      if (selectedEntry?.id === entryId) {
        selectedEntry = null;
      }
      await loadHistory();
    } catch (err) {
      showToast(`Failed to delete: ${err.message}`, 'error');
    }
  }

  function handleCopyContent() {
    if (selectedEntry?.content) {
      navigator.clipboard.writeText(selectedEntry.content);
      showToast('Content copied to clipboard', 'success');
    }
  }

  function formatDate(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="architecture-backdrop" on:click={onClose}>
  <div class="architecture-panel" on:click|stopPropagation>
    <div class="panel-header">
      <h3>Architecture</h3>
      <button class="close-btn" on:click={onClose}>X</button>
    </div>

    {#if loading}
      <div class="loading">
        <div class="spinner"></div>
        <p>Loading...</p>
      </div>
    {:else}
      <div class="panel-body">
        <div class="tab-header">
          <div class="tab-info">
            <p class="tab-description">System design, tech stack, and API structure</p>
          </div>
          <div class="tab-actions">
            <button class="action-btn primary" on:click={handleGeneratePrompt}>
              Generate Prompt
            </button>
            <button class="action-btn" on:click={handleOpenSaveModal}>
              Save Summary
            </button>
          </div>
        </div>

        <div class="content-layout">
          <!-- History Table -->
          <div class="history-panel">
            <div class="history-header">History ({history.length})</div>
            {#if loadingHistory}
              <div class="loading-small">
                <div class="spinner-small"></div>
              </div>
            {:else if history.length === 0}
              <div class="empty-history">
                <p>No summaries yet</p>
                <p class="hint">Click "Generate Prompt" to create one</p>
              </div>
            {:else}
              <div class="history-list">
                {#each history as entry}
                  <div
                    class="history-item"
                    class:selected={selectedEntry?.id === entry.id}
                    role="button"
                    tabindex="0"
                    on:click={() => handleEntryClick(entry)}
                    on:keydown={(e) => e.key === 'Enter' && handleEntryClick(entry)}
                  >
                    <div class="history-date">{formatDate(entry.created_at)}</div>
                    <div class="history-preview">{entry.preview}</div>
                    <button
                      class="delete-btn"
                      on:click|stopPropagation={() => handleDelete(entry.id)}
                      title="Delete"
                    >
                      X
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <!-- Content Viewer -->
          <div class="content-panel">
            {#if selectedEntry}
              <div class="content-header">
                <span class="content-date">{formatDate(selectedEntry.created_at)}</span>
                <button class="copy-btn" on:click={handleCopyContent}>Copy</button>
              </div>
              <div class="content-body">
                <pre>{selectedEntry.content}</pre>
              </div>
            {:else}
              <div class="empty-content">
                <p>Select a summary to view</p>
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Prompt Modal -->
{#if showPromptModal}
  <div class="modal-backdrop" on:click={() => showPromptModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h4>AI Prompt for Architecture</h4>
        <button class="close-btn" on:click={() => showPromptModal = false}>X</button>
      </div>
      <div class="modal-body">
        <p class="modal-instructions">
          Copy this prompt and paste it into your AI tool (Claude, ChatGPT, etc.).
          The AI will analyze your codebase and generate a summary.
        </p>
        <pre class="prompt-content">{currentPrompt}</pre>
      </div>
      <div class="modal-footer">
        <button class="action-btn primary" on:click={handleCopyPrompt}>
          Copy Prompt
        </button>
        <button class="action-btn" on:click={() => showPromptModal = false}>
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Save Modal -->
{#if showSaveModal}
  <div class="modal-backdrop" on:click={() => showSaveModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h4>Save Architecture Summary</h4>
        <button class="close-btn" on:click={() => showSaveModal = false}>X</button>
      </div>
      <div class="modal-body">
        <p class="modal-instructions">
          Paste the AI-generated summary below:
        </p>
        <textarea
          class="save-textarea"
          bind:value={saveContent}
          placeholder="Paste your AI-generated summary here..."
          rows="15"
        ></textarea>
      </div>
      <div class="modal-footer">
        <button
          class="action-btn primary"
          on:click={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Summary'}
        </button>
        <button class="action-btn" on:click={() => showSaveModal = false}>
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .architecture-backdrop {
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
  }

  .architecture-panel {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 95%;
    max-width: 1000px;
    height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
  }

  .panel-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
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
    font-size: 16px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 2px;
  }

  .close-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .panel-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .tab-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
  }

  .tab-description {
    margin: 0;
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .tab-actions {
    display: flex;
    gap: 8px;
  }

  .action-btn {
    padding: 8px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 1px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .action-btn.primary {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: var(--bg-primary);
  }

  .action-btn.primary:hover {
    opacity: 0.9;
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .content-layout {
    flex: 1;
    display: grid;
    grid-template-columns: 280px 1fr;
    overflow: hidden;
  }

  .history-panel {
    border-right: 1px solid var(--border-primary);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .history-header {
    padding: 10px 16px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-secondary);
    flex-shrink: 0;
  }

  .history-list {
    flex: 1;
    overflow-y: auto;
  }

  .history-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid var(--border-secondary);
    background: transparent;
    cursor: pointer;
    text-align: left;
    width: 100%;
    position: relative;
    transition: all 0.15s;
  }

  .history-item:hover {
    background: var(--bg-hover);
  }

  .history-item.selected {
    background: var(--bg-secondary);
    border-left: 3px solid var(--accent-primary);
    padding-left: 13px;
  }

  .history-date {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .history-preview {
    font-size: 10px;
    color: var(--text-tertiary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 24px;
  }

  .history-item .delete-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    padding: 4px 8px;
    font-size: 10px;
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    opacity: 0;
    transition: all 0.15s;
  }

  .history-item:hover .delete-btn {
    opacity: 1;
  }

  .history-item .delete-btn:hover {
    color: #ff6b6b;
  }

  .content-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .content-header {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-secondary);
    flex-shrink: 0;
  }

  .content-date {
    font-size: 11px;
    color: var(--text-secondary);
  }

  .copy-btn {
    padding: 4px 12px;
    background: transparent;
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 1px;
    cursor: pointer;
  }

  .copy-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .content-body {
    flex: 1;
    overflow: auto;
    padding: 16px;
  }

  .content-body pre {
    margin: 0;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .empty-history,
  .empty-content,
  .loading,
  .loading-small {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 32px;
    color: var(--text-tertiary);
    gap: 8px;
  }

  .empty-history p,
  .empty-content p {
    margin: 0;
    font-size: 12px;
  }

  .hint {
    font-size: 11px !important;
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

  .spinner-small {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-secondary);
    border-top-color: var(--text-secondary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Modal Styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }

  .modal {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
  }

  .modal-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h4 {
    margin: 0;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .modal-body {
    flex: 1;
    padding: 20px;
    overflow: auto;
  }

  .modal-instructions {
    margin: 0 0 16px;
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .prompt-content {
    background: var(--bg-secondary);
    padding: 16px;
    border-radius: 2px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 400px;
    overflow: auto;
  }

  .save-textarea {
    width: 100%;
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    resize: vertical;
  }

  .save-textarea:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .modal-footer {
    padding: 16px 20px;
    border-top: 1px solid var(--border-primary);
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  @media (max-width: 768px) {
    .content-layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }

    .history-panel {
      border-right: none;
      border-bottom: 1px solid var(--border-primary);
      max-height: 200px;
    }
  }
</style>
