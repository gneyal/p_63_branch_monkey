<script>
  import { writable } from 'svelte/store';
  import { SvelteFlow, Background, Controls, MiniMap } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import CommitNode from './CommitNode.svelte';
  import WorkingTreeNode from './WorkingTreeNode.svelte';
  import { workingTreeStatus } from '../stores/store.js';

  export let commits = [];
  export let onNodeClick = null;
  export let groupBy = 'day'; // 'day' or 'week'

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    commit: CommitNode,
    workingTree: WorkingTreeNode
  };

  $: if (commits && commits.length > 0) {
    buildTimeline();
  }

  // Also rebuild when working tree status changes
  $: if ($workingTreeStatus) {
    if (commits && commits.length > 0) {
      buildTimeline();
    }
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

    // Find date range and fill in empty days/weeks
    const allDates = Array.from(groups.keys()).sort();
    if (allDates.length === 0) {
      nodes.set([]);
      edges.set([]);
      return;
    }

    const startDate = new Date(allDates[0]);
    const endDate = new Date(allDates[allDates.length - 1]);
    const buildings = [];

    // Generate all dates in range
    const currentDate = new Date(startDate);
    while (currentDate <= endDate) {
      let key;
      if (groupBy === 'day') {
        key = currentDate.toISOString().split('T')[0];
        // Add existing group or empty placeholder
        buildings.push(groups.get(key) || { date: key, commits: [] });
        // Move to next day
        currentDate.setDate(currentDate.getDate() + 1);
      } else {
        const weekStart = getWeekStart(currentDate);
        key = weekStart.toISOString().split('T')[0];
        // Only add if we haven't added this week yet
        if (!buildings.find(b => b.date === key)) {
          buildings.push(groups.get(key) || { date: key, commits: [] });
        }
        // Move to next week
        currentDate.setDate(currentDate.getDate() + 7);
      }
    }

    // Convert to Svelte Flow nodes - one node per commit, stacked vertically by date
    const newNodes = [];
    const commitHeight = 180; // Height per commit node (increased for more spacing)
    const columnWidth = 500; // Width between date columns (increased for more spacing)
    const baseY = 600; // Baseline for alignment

    // Check if we should show working tree node (uncommitted changes)
    const showWorkingTreeNode = $workingTreeStatus && !$workingTreeStatus.clean;

    buildings.forEach((building, columnIndex) => {
      const xPos = columnIndex * columnWidth;
      const commitCount = building.commits.length;
      const isEmpty = commitCount === 0;

      // Add date label node (centered with commits)
      // CommitNode is ~220px wide, date label is 150px, so offset by (220-150)/2 = 35px
      newNodes.push({
        id: `date-${building.date}`,
        type: 'input',
        position: { x: xPos + 35, y: baseY + 20 },
        data: {
          label: `${formatDate(building.date)}${isEmpty ? '\n0 commits' : ''}`
        },
        draggable: false,
        selectable: false,
        style: `background: var(--bg-secondary); border: 1px solid var(--border-primary); padding: 8px 12px; font-size: 10px; font-weight: 600; color: ${isEmpty ? 'var(--text-tertiary)' : 'var(--text-secondary)'}; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 1px; text-align: center; width: 150px; opacity: ${isEmpty ? '0.5' : '1'};`
      });

      // Add commit nodes stacked vertically (bottom to top, oldest to newest)
      // Reverse so oldest commits are at bottom, newest at top
      const reversedCommits = [...building.commits].reverse();
      reversedCommits.forEach((commit, commitIndex) => {
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

      // Add working tree node at the top of the last (most recent) column
      if (columnIndex === buildings.length - 1 && showWorkingTreeNode) {
        const topCommitCount = reversedCommits.length;
        const workingTreeY = baseY - ((topCommitCount + 1) * commitHeight);

        newNodes.push({
          id: 'working-tree',
          type: 'workingTree',
          position: { x: xPos, y: workingTreeY },
          zIndex: 1,
          data: {
            status: $workingTreeStatus
          }
        });
      }
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
