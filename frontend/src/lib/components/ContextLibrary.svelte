<script>
  import { onMount } from 'svelte';
  import { fetchContextStatus, fetchContextFile, updateAllContext } from '../services/api.js';
  import { showToast } from '../stores/store.js';

  export let onClose = () => {};

  let contextFiles = [];
  let loading = true;
  let updating = false;
  let error = null;
  let selectedFile = null;
  let selectedContent = null;
  let loadingContent = false;

  onMount(async () => {
    await loadContextStatus();
  });

  async function loadContextStatus() {
    try {
      loading = true;
      const data = await fetchContextStatus();
      contextFiles = data.files || [];
    } catch (err) {
      error = err.message;
      showToast(`Failed to load context status: ${err.message}`, 'error');
    } finally {
      loading = false;
    }
  }

  async function handleUpdateAll() {
    try {
      updating = true;
      await updateAllContext();
      showToast('Context files updated successfully', 'success');
      await loadContextStatus();
      // Reload selected file if any
      if (selectedFile) {
        await loadFileContent(selectedFile);
      }
    } catch (err) {
      showToast(`Failed to update context: ${err.message}`, 'error');
    } finally {
      updating = false;
    }
  }

  async function loadFileContent(fileName) {
    try {
      loadingContent = true;
      selectedFile = fileName;
      const data = await fetchContextFile(fileName);
      selectedContent = data.content;
    } catch (err) {
      showToast(`Failed to load file: ${err.message}`, 'error');
      selectedContent = null;
    } finally {
      loadingContent = false;
    }
  }

  function handleCopyContent() {
    if (selectedContent) {
      navigator.clipboard.writeText(selectedContent);
      showToast('Content copied to clipboard', 'success');
    }
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function formatDate(isoString) {
    if (!isoString) return '-';
    return new Date(isoString).toLocaleString();
  }

  function getFileLabel(fileName) {
    const labels = {
      'codebase_summary.md': 'Codebase Summary',
      'architecture_summary.md': 'Architecture Summary',
      'prompts_summary.md': 'Prompts Summary'
    };
    return labels[fileName] || fileName;
  }

  function getFileDescription(fileName) {
    const descriptions = {
      'codebase_summary.md': 'File structure, key components, and file types',
      'architecture_summary.md': 'Project type, patterns, and architectural overview',
      'prompts_summary.md': 'Summary of AI prompts used in this repository'
    };
    return descriptions[fileName] || '';
  }
</script>

<div class="context-library-backdrop" on:click={onClose}>
  <div class="context-library-panel" on:click|stopPropagation>
    <div class="panel-header">
      <h3>Context Library</h3>
      <div class="header-actions">
        <button
          class="update-all-btn"
          on:click={handleUpdateAll}
          disabled={updating}
        >
          {updating ? 'Updating...' : 'Update All'}
        </button>
        <button class="close-btn" on:click={onClose}>X</button>
      </div>
    </div>

    <div class="panel-content">
      {#if loading}
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading context status...</p>
        </div>
      {:else if error}
        <div class="error">
          <p>{error}</p>
        </div>
      {:else}
        <div class="context-layout">
          <!-- File List -->
          <div class="file-list">
            <div class="list-header">Context Files</div>
            {#each contextFiles as file}
              <button
                class="file-item"
                class:selected={selectedFile === file.file_name}
                class:missing={!file.exists}
                on:click={() => loadFileContent(file.file_name)}
              >
                <div class="file-info">
                  <span class="file-name">{getFileLabel(file.file_name)}</span>
                  <span class="file-desc">{getFileDescription(file.file_name)}</span>
                </div>
                <div class="file-meta">
                  {#if file.exists}
                    <span class="file-status exists">Ready</span>
                    <span class="file-size">{formatFileSize(file.size_bytes)}</span>
                  {:else}
                    <span class="file-status missing">Not generated</span>
                  {/if}
                </div>
              </button>
            {/each}
          </div>

          <!-- Content Viewer -->
          <div class="content-viewer">
            {#if loadingContent}
              <div class="loading">
                <div class="spinner"></div>
                <p>Loading content...</p>
              </div>
            {:else if selectedFile && selectedContent}
              <div class="content-header">
                <span class="content-title">{getFileLabel(selectedFile)}</span>
                <button class="copy-btn" on:click={handleCopyContent}>Copy</button>
              </div>
              <div class="content-body">
                <pre>{selectedContent}</pre>
              </div>
            {:else if selectedFile && !selectedContent}
              <div class="empty-content">
                <p>File not generated yet</p>
                <p class="empty-hint">Click "Update All" to generate context files</p>
              </div>
            {:else}
              <div class="empty-content">
                <p>Select a file to view its content</p>
                <p class="empty-hint">Context files help AI assistants understand your codebase</p>
              </div>
            {/if}
          </div>
        </div>

        <div class="panel-footer">
          <span class="info-text">
            Files stored in: <code>.branch_monkey/</code>
          </span>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .context-library-backdrop {
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
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .context-library-panel {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 95%;
    max-width: 1200px;
    max-height: 85vh;
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

  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .update-all-btn {
    padding: 6px 16px;
    background: var(--accent-primary);
    border: none;
    color: var(--bg-primary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 1px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .update-all-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .update-all-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 16px;
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
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .loading,
  .error,
  .empty-content {
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
    to { transform: rotate(360deg); }
  }

  .context-layout {
    display: grid;
    grid-template-columns: 300px 1fr;
    height: 100%;
    overflow: hidden;
  }

  .file-list {
    border-right: 1px solid var(--border-primary);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .list-header {
    padding: 12px 16px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .file-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    border: none;
    border-bottom: 1px solid var(--border-secondary);
    background: transparent;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
    width: 100%;
  }

  .file-item:hover {
    background: var(--bg-hover);
  }

  .file-item.selected {
    background: var(--bg-secondary);
    border-left: 3px solid var(--accent-primary);
    padding-left: 13px;
  }

  .file-item.missing {
    opacity: 0.6;
  }

  .file-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .file-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .file-desc {
    font-size: 10px;
    color: var(--text-tertiary);
    line-height: 1.4;
  }

  .file-meta {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .file-status {
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 2px 6px;
    border-radius: 1px;
  }

  .file-status.exists {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
  }

  .file-status.missing {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
  }

  .file-size {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .content-viewer {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .content-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-secondary);
  }

  .content-title {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
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
    transition: all 0.15s;
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

  .panel-footer {
    padding: 12px 24px;
    border-top: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .info-text {
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .info-text code {
    font-family: 'Courier New', Courier, monospace;
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 2px;
  }

  @media (max-width: 768px) {
    .context-layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }

    .file-list {
      border-right: none;
      border-bottom: 1px solid var(--border-primary);
      max-height: 200px;
    }
  }
</style>
