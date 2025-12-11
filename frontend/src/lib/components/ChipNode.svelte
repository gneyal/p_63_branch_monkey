<script>
  import { Handle, Position } from '@xyflow/svelte';

  export let data;
  export let selected = false;

  $: layerType = data.layerType || 'default';
  $: config = getLayerConfig(layerType);

  // Classic vim colors
  function getLayerConfig(type) {
    switch (type) {
      case 'page':
        return {
          color: '#56b6c2',  // vim cyan
          bgColor: 'rgba(86, 182, 194, 0.1)',
          label: 'PAGE',
          icon: '◻'
        };
      case 'component':
        return {
          color: '#c678dd',  // vim magenta
          bgColor: 'rgba(198, 120, 221, 0.1)',
          label: 'COMPONENT',
          icon: '▣'
        };
      case 'endpoint':
        return {
          color: '#61afef',  // vim blue
          bgColor: 'rgba(97, 175, 239, 0.1)',
          label: 'API',
          icon: '⟷'
        };
      case 'entity':
        return {
          color: '#98c379',  // vim green
          bgColor: 'rgba(152, 195, 121, 0.1)',
          label: 'ENTITY',
          icon: '◆'
        };
      case 'table':
        return {
          color: '#e5c07b',  // vim yellow
          bgColor: 'rgba(229, 192, 123, 0.1)',
          label: 'TABLE',
          icon: '▤'
        };
      default:
        return {
          color: '#abb2bf',  // vim foreground
          bgColor: 'rgba(171, 178, 191, 0.1)',
          label: 'NODE',
          icon: '○'
        };
    }
  }

  function getMethodBadge(method) {
    const colors = {
      GET: '#98c379',     // vim green
      POST: '#61afef',    // vim blue
      PUT: '#e5c07b',     // vim yellow
      PATCH: '#c678dd',   // vim magenta
      DELETE: '#e06c75'   // vim red
    };
    return colors[method] || '#abb2bf';
  }
</script>

<div
  class="layer-node"
  class:selected
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
    transition: box-shadow 0.15s ease, transform 0.15s ease;
  }

  .layer-node.selected {
    box-shadow: 0 0 0 3px #61afef, 0 4px 12px rgba(97, 175, 239, 0.3);
    transform: scale(1.02);
  }

  .node-badge {
    background: var(--layer-color);
    color: #282c34;  /* vim dark background for contrast */
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
    color: #282c34;  /* vim dark background for contrast */
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
