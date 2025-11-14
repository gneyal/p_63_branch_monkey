<script>
  import { onMount } from 'svelte';
  import { fetchRemoteStatus } from '../services/api.js';

  export let onClose = () => {};

  let status = {
    has_remote: false,
    current_branch: '',
    remote_branch: '',
    remote_name: '',
    ahead: 0,
    behind: 0,
    synced: false
  };
  let loading = true;
  let error = null;

  async function loadStatus() {
    try {
      loading = true;
      error = null;
      const data = await fetchRemoteStatus();
      status = data;
    } catch (err) {
      console.error('Failed to load remote status:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadStatus();
  });
</script>

<div class="overlay" on:click={onClose}>
  <div class="modal" on:click|stopPropagation>
    <div class="modal-header">
      <h2>Cloud Sync Status</h2>
      <button class="close-btn" on:click={onClose}>×</button>
    </div>

    <div class="modal-content">
      {#if loading}
        <div class="loading">Loading remote status...</div>
      {:else if error}
        <div class="error">Error: {error}</div>
      {:else if !status.has_remote}
        <div class="no-remote">
          <div class="monkey">☁️</div>
          <p>Not Connected to Cloud</p>
          <p class="hint">Your work: <code>{status.current_branch}</code></p>
          <p class="hint">This work is only on your computer, not backed up to the cloud.</p>
        </div>
      {:else}
        <div class="status-info">
          <div class="branch-info">
            <div class="label">Your Computer</div>
            <div class="value">
              <span class="branch-icon">💻</span>
              {status.current_branch}
            </div>
          </div>

          <div class="arrow">→</div>

          <div class="branch-info">
            <div class="label">Cloud Backup</div>
            <div class="value">
              <span class="branch-icon">☁️</span>
              {status.remote_branch}
            </div>
          </div>
        </div>

        <div class="sync-status">
          {#if status.synced}
            <div class="synced">
              <span class="monkey">✓</span>
              <span>Everything is synced!</span>
            </div>
          {:else}
            <div class="diverged">
              {#if status.ahead > 0}
                <div class="ahead">
                  <span class="monkey">↑</span>
                  <span>{status.ahead} change{status.ahead === 1 ? '' : 's'} to upload</span>
                  <span class="hint">(you have new work to share)</span>
                </div>
              {/if}
              {#if status.behind > 0}
                <div class="behind">
                  <span class="monkey">↓</span>
                  <span>{status.behind} update{status.behind === 1 ? '' : 's'} available</span>
                  <span class="hint">(others made changes)</span>
                </div>
              {/if}
            </div>
          {/if}
        </div>

        <div class="remote-name">
          Cloud Server: <code>{status.remote_name}</code>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .overlay {
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
    backdrop-filter: blur(4px);
  }

  .modal {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    box-shadow: var(--shadow-large);
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .modal-header h2 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-primary);
  }

  .close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 2px;
    transition: all 0.2s ease;
  }

  .close-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .modal-content {
    padding: 24px;
  }

  .loading, .error {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-secondary);
    font-size: 12px;
  }

  .error {
    color: #ef4444;
  }

  .no-remote {
    text-align: center;
    padding: 40px 20px;
  }

  .no-remote .monkey {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .no-remote p {
    margin: 8px 0;
    color: var(--text-secondary);
    font-size: 12px;
  }

  .no-remote .hint {
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .no-remote code {
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 2px;
    font-family: 'Courier New', 'Courier', 'Monaco', 'Menlo', monospace;
    font-size: 11px;
  }

  .status-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;
    padding: 20px;
    background: var(--bg-secondary);
    border-radius: 2px;
  }

  .branch-info {
    flex: 1;
  }

  .branch-info .label {
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-tertiary);
    margin-bottom: 8px;
  }

  .branch-info .value {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    font-family: 'Courier New', 'Courier', 'Monaco', 'Menlo', monospace;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .branch-icon {
    font-size: 16px;
  }

  .arrow {
    font-size: 20px;
    color: var(--text-tertiary);
  }

  .sync-status {
    margin-bottom: 24px;
  }

  .synced {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 20px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 2px;
    color: #10b981;
    font-size: 13px;
    font-weight: 500;
  }

  .synced .monkey {
    font-size: 24px;
  }

  .diverged {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .ahead, .behind {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-radius: 2px;
  }

  .ahead {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #10b981;
  }

  .behind {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #f59e0b;
  }

  .ahead .monkey, .behind .monkey {
    font-size: 24px;
  }

  .ahead span, .behind span {
    font-size: 12px;
    font-weight: 500;
  }

  .hint {
    font-size: 10px;
    opacity: 0.7;
    margin-left: 4px;
  }

  .remote-name {
    text-align: center;
    font-size: 11px;
    color: var(--text-tertiary);
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 2px;
  }

  .remote-name code {
    font-family: 'Courier New', 'Courier', 'Monaco', 'Menlo', monospace;
    color: var(--text-secondary);
  }
</style>
