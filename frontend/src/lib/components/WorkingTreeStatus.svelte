<script>
  import { onMount } from 'svelte';
  import { fetchWorkingTreeStatus } from '../services/api.js';

  let status = {
    clean: true,
    staged: 0,
    modified: 0,
    untracked: 0,
    total_changes: 0
  };
  let loading = true;
  let error = null;

  async function loadStatus() {
    try {
      loading = true;
      error = null;
      const data = await fetchWorkingTreeStatus();
      status = data;
    } catch (err) {
      console.error('Failed to load working tree status:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadStatus();
    // Refresh every 5 seconds
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  });
</script>

<div class="working-tree-status">
  {#if loading && status.total_changes === 0}
    <span class="status-item loading">Loading...</span>
  {:else if error}
    <span class="status-item error" title={error}>⚠️ Error</span>
  {:else if status.clean}
    <span class="status-item clean" title="No changes">Clean</span>
  {:else}
    <div class="status-items">
      {#if status.staged > 0}
        <span class="status-item staged" title="{status.staged} {status.staged === 1 ? 'file' : 'files'} ready to save">
          {status.staged} Ready
        </span>
      {/if}
      {#if status.modified > 0}
        <span class="status-item modified" title="{status.modified} {status.modified === 1 ? 'file has' : 'files have'} changes">
          {status.modified} Changed
        </span>
      {/if}
      {#if status.untracked > 0}
        <span class="status-item untracked" title="{status.untracked} new {status.untracked === 1 ? 'file' : 'files'}">
          {status.untracked} New
        </span>
      {/if}
    </div>
  {/if}
</div>

<style>
  .working-tree-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .status-items {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  }

  .status-item.loading {
    color: var(--text-tertiary);
  }

  .status-item.error {
    color: #ef4444;
  }

  .status-item.clean {
    color: #10b981;
  }

  .status-item.staged {
    color: #10b981;
  }

  .status-item.modified {
    color: #f59e0b;
  }

  .status-item.untracked {
    color: var(--text-tertiary);
  }
</style>
