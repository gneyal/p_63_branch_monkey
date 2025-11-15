<script>
  import { onMount } from 'svelte';
  import { fetchBranches } from '../services/api.js';
  import { showToast } from '../stores/store.js';

  export let onClose = () => {};
  export let onBranchClick = (branch) => {};

  let branches = [];
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      const data = await fetchBranches();
      branches = data.branches || [];
    } catch (err) {
      error = err.message;
      showToast(`Failed to load branches: ${err.message}`, 'error');
    } finally {
      loading = false;
    }
  });

  function handleBranchClick(branch) {
    onBranchClick(branch);
    onClose();
  }

  function getBranchColor(name) {
    if (name === 'main' || name === 'master') return 'var(--branch-main)';
    if (name.startsWith('experiment/')) return 'var(--branch-experiment)';
    if (name.startsWith('feature/')) return 'var(--branch-feature)';
    if (name.startsWith('fix/') || name.startsWith('bugfix/')) return 'var(--branch-fix)';
    return 'var(--branch-default)';
  }
</script>

<div class="branches-list-backdrop" on:click={onClose}>
  <div class="branches-list-panel" on:click|stopPropagation>
    <div class="panel-header">
      <h3>All Branches</h3>
      <button class="close-btn" on:click={onClose}>✕</button>
    </div>

    <div class="panel-content">
      {#if loading}
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading branches...</p>
        </div>
      {:else if error}
        <div class="error">
          <p>{error}</p>
        </div>
      {:else if branches.length === 0}
        <div class="empty">
          <p>No branches found</p>
        </div>
      {:else}
        <div class="branches-grid">
          {#each branches as branch}
            <button
              class="branch-item"
              class:current={branch.is_current}
              on:click={() => handleBranchClick(branch)}
            >
              <div class="branch-header">
                <span class="branch-name" style="color: {getBranchColor(branch.name)};">
                  {branch.name}
                </span>
                {#if branch.is_current}
                  <span class="current-badge">HEAD</span>
                {/if}
              </div>
              <div class="branch-details">
                <span class="branch-sha">{branch.sha}</span>
                <span class="branch-age">{branch.age}</span>
              </div>
              <div class="branch-message">{branch.message}</div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .branches-list-backdrop {
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

  .branches-list-panel {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
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

  .branches-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
  }

  .branch-item {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    padding: 12px 16px;
    text-align: left;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .branch-item:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    box-shadow: var(--shadow-small);
  }

  .branch-item.current {
    border-width: 2px;
    border-color: var(--accent-primary);
  }

  .branch-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }

  .branch-name {
    font-size: 13px;
    font-weight: 500;
    font-family: 'Courier', monospace;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .current-badge {
    font-size: 9px;
    padding: 2px 6px;
    background: var(--accent-primary);
    color: var(--bg-primary);
    border-radius: 1px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .branch-details {
    display: flex;
    gap: 12px;
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .branch-sha {
    font-family: 'Courier', monospace;
  }

  .branch-message {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
