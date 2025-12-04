<script>
  import { onMount } from 'svelte';
  import { repoInfo } from '../stores/store.js';
  import {
    fetchRepoInfo,
    fetchContextCounts,
    fetchContextPrompt,
    fetchContextHistory,
    fetchContextEntry,
    saveContextSummary,
    deleteContextEntry
  } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Topbar from './Topbar.svelte';
  import ThemePicker from './ThemePicker.svelte';

  const CONTEXT_TYPES = ['codebase'];
  const TYPE_LABELS = {
    codebase: 'Codebase',
    architecture: 'Architecture'
  };
  const TYPE_DESCRIPTIONS = {
    codebase: 'File structure, key components, and code patterns',
    architecture: 'System design, tech stack, and API structure'
  };

  let activeTab = 'codebase';
  let counts = { codebase: 0, architecture: 0, prompts: 0 };
  let history = [];
  let loading = true;
  let loadingHistory = false;
  let selectedEntry = null;
  let showPromptModal = false;
  let showSaveModal = false;
  let currentPrompt = '';
  let saveContent = '';
  let saving = false;
  let toastMessage = '';
  let toastType = 'info';

  function showToast(message, type = 'info') {
    toastMessage = message;
    toastType = type;
    setTimeout(() => toastMessage = '', 3000);
  }

  onMount(async () => {
    if (!$repoInfo || !$repoInfo.path) {
      try {
        const info = await fetchRepoInfo();
        repoInfo.set(info);
      } catch (err) {
        console.error('Failed to load repo info:', err);
      }
    }
    await loadCounts();
    await loadHistory(activeTab);
    loading = false;
  });

  async function loadCounts() {
    try {
      const data = await fetchContextCounts();
      counts = data.counts;
    } catch (err) {
      console.error('Failed to load counts:', err);
    }
  }

  async function loadHistory(contextType) {
    try {
      loadingHistory = true;
      const data = await fetchContextHistory(contextType);
      history = data.history || [];
    } catch (err) {
      showToast(`Failed to load history: ${err.message}`, 'error');
      history = [];
    } finally {
      loadingHistory = false;
    }
  }

  async function handleTabChange(tab) {
    activeTab = tab;
    selectedEntry = null;
    await loadHistory(tab);
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
      const data = await fetchContextPrompt(activeTab);
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
      await saveContextSummary(activeTab, saveContent);
      showToast('Summary saved successfully!', 'success');
      showSaveModal = false;
      saveContent = '';
      await loadCounts();
      await loadHistory(activeTab);
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
      await loadCounts();
      await loadHistory(activeTab);
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

<main class="context-page">
  <Topbar activeView="context" />

  <div class="page-content">
    <div class="context-container">
      <div class="context-header">
        <div class="header-left">
          <h2>Context Library</h2>
          <p class="context-description">
            Store and manage AI-generated summaries of your codebase for consistent context.
          </p>
        </div>
      </div>

      {#if loading}
        <div class="loading-state">Loading...</div>
      {:else}
        <div class="context-body">
          <!-- Tabs -->
          <div class="tabs">
            {#each CONTEXT_TYPES as type}
              <button
                class="tab"
                class:active={activeTab === type}
                on:click={() => handleTabChange(type)}
              >
                <span class="tab-label">{TYPE_LABELS[type]}</span>
                <span class="tab-count">{counts[type]}</span>
              </button>
            {/each}
          </div>

          <!-- Tab Content -->
          <div class="tab-content">
            <div class="tab-header">
              <div class="tab-info">
                <h4>{TYPE_LABELS[activeTab]} Summaries</h4>
                <p class="tab-description">{TYPE_DESCRIPTIONS[activeTab]}</p>
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
                <div class="history-header">History</div>
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
        </div>
      {/if}
    </div>
  </div>

  <footer class="app-footer">
    <div class="footer-left"></div>
    <div class="footer-center"></div>
    <div class="footer-right">
      <ThemePicker compact={true} />
    </div>
  </footer>

  <Toast />

  <!-- Prompt Modal -->
  {#if showPromptModal}
    <div class="modal-backdrop" on:click={() => showPromptModal = false}>
      <div class="modal" on:click|stopPropagation>
        <div class="modal-header">
          <h4>AI Prompt for {TYPE_LABELS[activeTab]}</h4>
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
          <h4>Save {TYPE_LABELS[activeTab]} Summary</h4>
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
</main>

<style>
  .context-page {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .page-content {
    flex: 1;
    min-height: 0;
    overflow: auto;
    padding: 24px;
  }

  .context-container {
    max-width: 1400px;
    margin: 0 auto;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .context-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    gap: 24px;
  }

  .header-left h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .context-description {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }

  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    color: var(--text-secondary);
  }

  .context-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    overflow: hidden;
  }

  .tabs {
    display: flex;
    border-bottom: 1px solid var(--border-primary);
    padding: 0 16px;
    flex-shrink: 0;
  }

  .tab {
    padding: 12px 20px;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.15s;
  }

  .tab:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
  }

  .tab.active {
    color: var(--text-primary);
    border-bottom-color: var(--accent-primary);
  }

  .tab-count {
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 10px;
  }

  .tab.active .tab-count {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .tab-content {
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

  .tab-info h4 {
    margin: 0 0 4px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
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
    border-radius: 4px;
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
    grid-template-columns: 300px 1fr;
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
    border-radius: 4px;
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

  .app-footer {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 24px;
    align-items: center;
    padding: 8px 24px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-primary);
    box-shadow: var(--shadow-small);
  }

  .footer-left {
    display: flex;
    justify-content: flex-start;
  }

  .footer-center {
    display: flex;
    justify-content: center;
  }

  .footer-right {
    display: flex;
    justify-content: flex-end;
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
    border-radius: 4px;
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
    border-radius: 4px;
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
    border-radius: 4px;
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

    .tabs {
      overflow-x: auto;
    }

    .app-footer {
      grid-template-columns: 1fr;
      gap: 8px;
      padding: 8px 16px;
    }

    .footer-left,
    .footer-center,
    .footer-right {
      justify-content: center;
    }
  }
</style>
