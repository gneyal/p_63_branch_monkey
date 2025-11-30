<script>
  import { Handle, Position } from '@xyflow/svelte';

  export let data;

  $: layerType = data.layerType || 'default';
  $: config = getLayerConfig(layerType);

  function getLayerConfig(type) {
    switch (type) {
      case 'page':
        return {
          color: '#00bcd4',
          bgColor: 'rgba(0, 188, 212, 0.1)',
          label: 'PAGE',
          icon: '◻'
        };
      case 'component':
        return {
          color: '#9c27b0',
          bgColor: 'rgba(156, 39, 176, 0.1)',
          label: 'COMPONENT',
          icon: '▣'
        };
      case 'endpoint':
        return {
          color: '#2196f3',
          bgColor: 'rgba(33, 150, 243, 0.1)',
          label: 'API',
          icon: '⟷'
        };
      case 'entity':
        return {
          color: '#4caf50',
          bgColor: 'rgba(76, 175, 80, 0.1)',
          label: 'ENTITY',
          icon: '◆'
        };
      case 'table':
        return {
          color: '#ff9800',
          bgColor: 'rgba(255, 152, 0, 0.1)',
          label: 'TABLE',
          icon: '▤'
        };
      default:
        return {
          color: '#757575',
          bgColor: 'rgba(117, 117, 117, 0.1)',
          label: 'NODE',
          icon: '○'
        };
    }
  }

  function getMethodBadge(method) {
    const colors = {
      GET: '#4caf50',
      POST: '#2196f3',
      PUT: '#ff9800',
      PATCH: '#9c27b0',
      DELETE: '#f44336'
    };
    return colors[method] || '#757575';
  }
</script>

<div
  class="layer-node"
  style="
    --layer-color: {config.color};
    --layer-bg: {config.bgColor};
  "
>
  <!-- Top handle for incoming connections -->
  <Handle type="target" position={Position.Top} />

  <!-- Node content -->
  <div class="node-badge">{config.label}</div>

  <div class="node-body">
    {#if data.method}
      <span class="method-tag" style="background: {getMethodBadge(data.method)}">{data.method}</span>
    {/if}

    <div class="node-name">{data.name || 'Unnamed'}</div>

    {#if data.path}
      <div class="node-path">{data.path}</div>
    {/if}

    {#if data.description}
      <div class="node-desc">{data.description}</div>
    {/if}

    {#if data.meta}
      <div class="node-meta">{data.meta}</div>
    {/if}
  </div>

  <!-- Bottom handle for outgoing connections -->
  <Handle type="source" position={Position.Bottom} />
</div>

<style>
  .layer-node {
    min-width: 160px;
    max-width: 200px;
    background: var(--bg-primary);
    border: 2px solid var(--layer-color);
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  .node-badge {
    background: var(--layer-color);
    color: white;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 4px 8px;
    text-align: center;
  }

  .node-body {
    padding: 10px 12px;
    background: var(--layer-bg);
  }

  .method-tag {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 2px;
    color: white;
    margin-bottom: 6px;
  }

  .node-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    word-wrap: break-word;
    line-height: 1.3;
  }

  .node-path {
    font-size: 10px;
    font-family: 'SF Mono', Monaco, monospace;
    color: var(--layer-color);
    margin-top: 4px;
    padding: 3px 6px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
  }

  .node-desc {
    font-size: 10px;
    color: var(--text-tertiary);
    margin-top: 6px;
    line-height: 1.3;
  }

  .node-meta {
    font-size: 9px;
    color: var(--text-tertiary);
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid var(--border-secondary);
  }

  :global(.svelte-flow__handle) {
    width: 10px;
    height: 10px;
    background: var(--layer-color);
    border: 2px solid var(--bg-primary);
  }
</style>
