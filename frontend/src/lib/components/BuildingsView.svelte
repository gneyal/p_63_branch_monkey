<script>
  import { writable } from 'svelte/store';
  import { SvelteFlow, Background, Controls, MiniMap } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import BuildingNode from './BuildingNode.svelte';

  export let commits = [];

  let groupBy = 'day'; // 'day' or 'week'

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    building: BuildingNode
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

    // Convert to Svelte Flow nodes
    const newNodes = buildings.map((building, index) => {
      const height = getBuildingHeight(building.commits.length);

      return {
        id: `building-${building.date}`,
        type: 'building',
        position: {
          x: index * 150,  // Horizontal spacing
          y: 600 - height  // Align bottoms (baseline at y=600)
        },
        data: {
          date: building.date,
          commits: building.commits,
          formattedDate: formatDate(building.date),
          height: height
        }
      };
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

  function getBuildingHeight(commitCount) {
    return Math.min(commitCount * 40, 600); // 40px per commit, max 600px
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
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{ type: 'smoothstep' }}
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
