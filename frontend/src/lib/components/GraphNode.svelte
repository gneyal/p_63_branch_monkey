<script>
  import { Handle, Position } from '@xyflow/svelte';

  export let data = {};

  $: isHead = data.is_head;
  $: isRemote = data.isRemote;
  $: isAhead = data.isAhead;
  $: branches = data.branches || [];

  function getNodeColor() {
    if (isHead) return 'var(--accent-primary)';
    if (isRemote) return '#10b981';
    if (isAhead) return '#60a5fa';
    return 'var(--text-secondary)';
  }

  function getBranchColor(branchName) {
    const colors = [
      '#10b981', '#f59e0b', '#8b5cf6',
      '#ef4444', '#06b6d4', '#ec4899',
    ];
    let hash = 0;
    for (let i = 0; i < branchName.length; i++) {
      hash = branchName.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  }
</script>

<div class="graph-node" class:is-head={isHead}>
  <Handle type="target" position={Position.Top} />

  <div class="node-dot" style="background: {getNodeColor()}">
    {#if isHead}
      <div class="head-ring"></div>
    {/if}
  </div>

  {#if branches.length > 0}
    <div class="branches">
      {#each branches as branch}
        <span class="branch-badge" style="background: {getBranchColor(branch)}">{branch}</span>
      {/each}
    </div>
  {/if}

  {#if data.has_stash || data.has_notes}
    <div class="badges">
      {#if data.has_stash}
        <span class="badge stash-badge" title="Has stashed changes">stash</span>
      {/if}
      {#if data.has_notes}
        <span class="badge notes-badge" title="Has notes">notes</span>
      {/if}
    </div>
  {/if}

  <Handle type="source" position={Position.Bottom} />
</div>

<!-- Tooltip shown on hover via CSS -->
<div class="node-tooltip">
  <div class="tooltip-sha">{data.sha}</div>
  <div class="tooltip-message">{data.message}</div>
  <div class="tooltip-meta">
    <span>{data.author}</span>
    <span class="sep">·</span>
    <span>{data.age}</span>
  </div>
</div>

<style>
  .graph-node {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0;
    cursor: pointer;
  }

  .node-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    position: relative;
    transition: transform 0.15s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .graph-node:hover .node-dot {
    transform: scale(1.2);
  }

  .head-ring {
    position: absolute;
    top: -6px;
    left: -6px;
    right: -6px;
    bottom: -6px;
    border: 2px dashed var(--accent-primary);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .branches {
    display: flex;
    gap: 4px;
    flex-wrap: nowrap;
  }

  .branch-badge {
    font-size: 9px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 3px;
    color: white;
    white-space: nowrap;
  }

  .badges {
    display: flex;
    gap: 4px;
  }

  .badge {
    font-size: 8px;
    padding: 2px 5px;
    border-radius: 3px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .stash-badge {
    background: #7c3aed;
    color: white;
  }

  .notes-badge {
    background: #0891b2;
    color: white;
  }

  /* Tooltip - hidden by default, shown on hover */
  .node-tooltip {
    position: absolute;
    left: calc(100% + 12px);
    top: 50%;
    transform: translateY(-50%);
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    padding: 10px 12px;
    box-shadow: var(--shadow-medium);
    pointer-events: none;
    z-index: 1000;
    min-width: 200px;
    max-width: 300px;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.15s ease, visibility 0.15s ease;
  }

  .graph-node:hover + .node-tooltip {
    opacity: 1;
    visibility: visible;
  }

  .tooltip-sha {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 11px;
    color: var(--accent-primary);
    font-weight: 600;
    margin-bottom: 4px;
  }

  .tooltip-message {
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.4;
    margin-bottom: 6px;
    word-break: break-word;
  }

  .tooltip-meta {
    font-size: 10px;
    color: var(--text-tertiary);
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .sep {
    opacity: 0.5;
  }

  /* Handle styling */
  :global(.graph-node .svelte-flow__handle) {
    width: 1px !important;
    height: 1px !important;
    min-width: 1px !important;
    min-height: 1px !important;
    background: transparent !important;
    border: none !important;
  }
</style>
