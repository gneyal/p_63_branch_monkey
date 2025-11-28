<script>
  import { Handle, Position } from '@xyflow/svelte';

  export let data;

  // Node type determines styling and icon
  $: nodeType = data.nodeType || 'default';
  $: icon = getIcon(nodeType);
  $: colors = getColors(nodeType);

  function getIcon(type) {
    switch (type) {
      case 'tech': return ''; // gear
      case 'endpoint': return ''; // api/network
      case 'entity': return ''; // cube
      case 'table': return ''; // table
      case 'ui': return ''; // window
      default: return '';
    }
  }

  function getColors(type) {
    switch (type) {
      case 'tech':
        return { border: '#9c27b0', bg: 'rgba(156, 39, 176, 0.1)', text: '#ce93d8' };
      case 'endpoint':
        return { border: '#2196f3', bg: 'rgba(33, 150, 243, 0.1)', text: '#90caf9' };
      case 'entity':
        return { border: '#4caf50', bg: 'rgba(76, 175, 80, 0.1)', text: '#a5d6a7' };
      case 'table':
        return { border: '#ff9800', bg: 'rgba(255, 152, 0, 0.1)', text: '#ffcc80' };
      case 'ui':
        return { border: '#00bcd4', bg: 'rgba(0, 188, 212, 0.1)', text: '#80deea' };
      default:
        return { border: '#757575', bg: 'rgba(117, 117, 117, 0.1)', text: '#bdbdbd' };
    }
  }

  function getMethodColor(method) {
    switch (method?.toUpperCase()) {
      case 'GET': return '#4caf50';
      case 'POST': return '#2196f3';
      case 'PUT': return '#ff9800';
      case 'PATCH': return '#9c27b0';
      case 'DELETE': return '#f44336';
      default: return '#757575';
    }
  }
</script>

<div
  class="arch-node"
  style="border-color: {colors.border}; background: {colors.bg};"
>
  <Handle type="target" position={Position.Top} />

  <div class="node-header">
    <span class="node-type-badge" style="background: {colors.border};">
      {#if nodeType === 'tech'}
        Tech
      {:else if nodeType === 'endpoint'}
        API
      {:else if nodeType === 'entity'}
        Entity
      {:else if nodeType === 'table'}
        Table
      {:else if nodeType === 'ui'}
        UI
      {:else}
        Node
      {/if}
    </span>
  </div>

  <div class="node-content">
    {#if nodeType === 'endpoint' && data.method}
      <span class="method-badge" style="background: {getMethodColor(data.method)};">
        {data.method}
      </span>
    {/if}

    <div class="node-title" style="color: {colors.text};">
      {data.name || data.path || 'Unnamed'}
    </div>

    {#if data.description}
      <div class="node-description">
        {data.description.length > 80 ? data.description.substring(0, 80) + '...' : data.description}
      </div>
    {/if}

    {#if nodeType === 'tech' && data.category}
      <div class="node-meta">
        {data.category}
        {#if data.version}
          <span class="version">v{data.version}</span>
        {/if}
      </div>
    {/if}

    {#if nodeType === 'endpoint' && data.path}
      <div class="node-path">{data.path}</div>
    {/if}

    {#if nodeType === 'ui' && data.type}
      <div class="node-meta">{data.type}</div>
    {/if}

    {#if nodeType === 'table' && data.columns}
      <div class="node-meta">{data.columns.length} columns</div>
    {/if}

    {#if nodeType === 'entity' && data.fields}
      <div class="node-meta">{data.fields.length} fields</div>
    {/if}
  </div>

  <Handle type="source" position={Position.Bottom} />
</div>

<style>
  .arch-node {
    position: relative;
    border-radius: 4px;
    padding: 12px 16px;
    border: 2px solid;
    background: var(--bg-primary);
    min-width: 180px;
    max-width: 280px;
    box-shadow: var(--shadow-small);
    transition: all 0.15s ease;
    cursor: pointer;
  }

  .arch-node:hover {
    box-shadow: var(--shadow-medium);
    transform: translateY(-2px);
  }

  .node-header {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 8px;
  }

  .node-type-badge {
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 2px;
    color: white;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .node-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .method-badge {
    display: inline-block;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 2px;
    color: white;
    font-weight: 600;
    margin-bottom: 4px;
    width: fit-content;
  }

  .node-title {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.3;
    word-wrap: break-word;
  }

  .node-description {
    font-size: 11px;
    color: var(--text-tertiary);
    line-height: 1.4;
    margin-top: 4px;
  }

  .node-path {
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'Courier', monospace;
    margin-top: 4px;
    padding: 4px 6px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 2px;
  }

  .node-meta {
    font-size: 10px;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-top: 4px;
  }

  .version {
    margin-left: 4px;
    opacity: 0.8;
  }

  :global(.svelte-flow__handle) {
    width: 8px;
    height: 8px;
    background: var(--border-hover);
    border: 2px solid var(--bg-primary);
  }
</style>
