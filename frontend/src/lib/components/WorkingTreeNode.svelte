<script>
  export let data;
</script>

<div class="working-tree-node">
  <div class="node-header">
    <span class="uncommitted-label">Uncommitted Changes</span>
  </div>

  <div class="status-grid">
    {#if data.status.staged > 0}
      <div class="status-item staged">
        <span class="count">{data.status.staged}</span>
        <span class="label">Ready</span>
      </div>
    {/if}

    {#if data.status.modified > 0}
      <div class="status-item modified">
        <span class="count">{data.status.modified}</span>
        <span class="label">Changed</span>
      </div>
    {/if}

    {#if data.status.untracked > 0}
      <div class="status-item untracked">
        <span class="count">{data.status.untracked}</span>
        <span class="label">New</span>
      </div>
    {/if}
  </div>
</div>

<style>
  .working-tree-node {
    background: var(--bg-primary);
    border: 2px dashed var(--border-hover);
    border-radius: 2px;
    padding: 16px;
    min-width: 280px;
    max-width: 280px;
    box-shadow: var(--shadow-medium);
    transition: all 0.2s ease;
  }

  .working-tree-node:hover {
    box-shadow: var(--shadow-large);
    border-color: var(--accent-primary);
  }

  .node-header {
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .uncommitted-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .status-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    border-radius: 1px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
  }

  .status-item.staged {
    border-left: 3px solid #4caf50;
  }

  .status-item.modified {
    border-left: 3px solid #ff9800;
  }

  .status-item.untracked {
    border-left: 3px solid #2196f3;
  }

  .count {
    font-size: 16px;
    font-weight: 700;
    font-family: 'Courier New', 'Courier', 'Monaco', 'Menlo', monospace;
    min-width: 24px;
    text-align: center;
  }

  .status-item.staged .count {
    color: #4caf50;
  }

  .status-item.modified .count {
    color: #ff9800;
  }

  .status-item.untracked .count {
    color: #2196f3;
  }

  .label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    flex: 1;
  }
</style>
