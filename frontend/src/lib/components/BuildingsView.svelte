<script>
  import { writable } from 'svelte/store';
  import { SvelteFlow, Background, Controls, MiniMap } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import CommitNode from './CommitNode.svelte';

  export let commits = [];
  export let onNodeClick = null;

  let groupBy = 'day'; // 'day' or 'week'

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    commit: CommitNode
  };

  $: if (commits && commits.length > 0) {
    buildTimeline();
  }

  function buildTimeline() {
    // Group commits by date
    const groups = new Map();

    commits.forEach(commit => {
      const date = new Date(commit.timestamp || Date.now());
      let key;

      if (groupBy === 'day') {
        key = date.toISOString().split('T')[0]; // YYYY-MM-DD
      } else {
        // Week grouping
        const weekStart = getWeekStart(date);
        key = weekStart.toISOString().split('T')[0];
      }

      if (!groups.has(key)) {
        groups.set(key, {
          date: key,
          commits: []
        });
      }

      groups.get(key).commits.push(commit);
    });

    // Convert to array and sort by date
    const buildings = Array.from(groups.values()).sort((a, b) =>
      new Date(a.date) - new Date(b.date)
    );

    // Convert to Svelte Flow nodes - one node per commit, stacked vertically by date
    const newNodes = [];
    const commitHeight = 120; // Height per commit node (increased for more spacing)
    const columnWidth = 500; // Width between date columns (increased for more spacing)
    const baseY = 600; // Baseline for alignment

    buildings.forEach((building, columnIndex) => {
      const xPos = columnIndex * columnWidth;

      // Add date label node
      newNodes.push({
        id: `date-${building.date}`,
        type: 'input',
        position: { x: xPos, y: baseY + 20 },
        data: {
          label: formatDate(building.date)
        },
        draggable: false,
        selectable: false,
        style: 'background: var(--bg-secondary); border: 1px solid var(--border-primary); padding: 8px 12px; font-size: 10px; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.5px; border-radius: 1px;'
      });

      // Add commit nodes stacked vertically (bottom to top)
      building.commits.forEach((commit, commitIndex) => {
        const yPos = baseY - ((commitIndex + 1) * commitHeight);

        newNodes.push({
          id: commit.sha,
          type: 'commit',
          position: { x: xPos, y: yPos },
          zIndex: 1,
          data: {
            sha: commit.sha.substring(0, 7),
            fullSha: commit.fullSha,
            message: commit.message,
            author: commit.author,
            age: commit.age,
            branches: commit.branches,
            is_head: commit.is_head
          }
        });
      });
    });

    nodes.set(newNodes);
    edges.set([]);  // No edges needed for buildings view
  }

  function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr);
    if (groupBy === 'day') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else {
      return `Week of ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
    }
  }

  function handleNodeClickInternal(event) {
    if (onNodeClick) {
      onNodeClick(event.detail);
    }
  }
</script>

<div class="buildings-view">
  <div class="view-controls">
    <div class="group-toggle">
      <button
        class="toggle-btn"
        class:active={groupBy === 'day'}
        on:click={() => groupBy = 'day'}
      >
        Day
      </button>
      <button
        class="toggle-btn"
        class:active={groupBy === 'week'}
        on:click={() => groupBy = 'week'}
      >
        Week
      </button>
    </div>
  </div>

  <div class="flow-container">
    {#if $nodes.length > 0}
      <SvelteFlow
        nodes={$nodes}
        edges={$edges}
        {nodeTypes}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
        panOnDrag={true}
        zoomOnScroll={true}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{ type: 'smoothstep' }}
        on:nodeclick={handleNodeClickInternal}
      >
        <Background />
        <Controls />
        <MiniMap nodeColor="#94a3b8" />
      </SvelteFlow>
    {:else}
      <div class="loading">Loading buildings...</div>
    {/if}
  </div>
</div>

<style>
  .buildings-view {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
  }

  .view-controls {
    padding: 16px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: center;
    z-index: 10;
  }

  .group-toggle {
    display: flex;
    gap: 4px;
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    overflow: hidden;
  }

  .toggle-btn {
    padding: 6px 16px;
    background: var(--bg-primary);
    border: none;
    color: var(--text-secondary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .toggle-btn.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .flow-container {
    flex: 1;
    min-height: 0;
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-tertiary);
    font-size: 14px;
  }

  /* Minimap styling */
  :global(.buildings-view .svelte-flow__minimap) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
    transform: scale(0.6);
    transform-origin: bottom right;
    transition: transform 0.2s ease;
    opacity: 0.7;
  }

  :global(.buildings-view .svelte-flow__minimap:hover) {
    transform: scale(1);
    opacity: 1;
  }
</style>
