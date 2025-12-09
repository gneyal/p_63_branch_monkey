<script>
  import { writable } from 'svelte/store';
  import { onMount } from 'svelte';
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    MiniMap
  } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import GraphNode from './GraphNode.svelte';

  export let commits = [];
  export let onNodeClick = null;
  export let remoteSha = null;

  let selectedCommit = null;

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    graph: GraphNode
  };

  // Layout constants - spacing for larger nodes
  const LANE_WIDTH = 60;
  const ROW_HEIGHT = 55;

  // Calculate which commits are ahead of remote
  $: aheadShas = calculateAheadShas(commits, remoteSha);

  function calculateAheadShas(commits, remoteSha) {
    if (!remoteSha || !commits || commits.length === 0) return new Set();
    const remoteIndex = commits.findIndex(c => c.sha === remoteSha);
    if (remoteIndex === -1) return new Set();
    const ahead = new Set();
    for (let i = 0; i < remoteIndex; i++) {
      ahead.add(commits[i].sha);
    }
    return ahead;
  }

  function calculateLanes(commits) {
    const lanes = {};
    const branchLanes = new Map();
    branchLanes.set('main', 0);
    branchLanes.set('master', 0);
    let nextLane = 1;

    commits.forEach((commit, index) => {
      let lane = null;

      if (commit.branches && commit.branches.length > 0) {
        const branchName = commit.branches[0];
        if (branchLanes.has(branchName)) {
          lane = branchLanes.get(branchName);
        } else {
          lane = nextLane++;
          branchLanes.set(branchName, lane);
        }
      } else {
        for (let i = 0; i < index; i++) {
          const child = commits[i];
          if (child.parents && child.parents.includes(commit.sha)) {
            if (lanes[child.sha] !== undefined) {
              lane = lanes[child.sha];
              break;
            }
          }
        }
        if (lane === null) lane = 0;
      }

      lanes[commit.sha] = lane;
    });

    return lanes;
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

  // Build nodes and edges when commits change
  $: if (commits && commits.length > 0) {
    const commitLanes = calculateLanes(commits);
    const commitMap = new Map(commits.map(c => [c.sha, c]));

    // Calculate centering offset
    const maxLane = Math.max(0, ...Object.values(commitLanes));
    const totalWidth = maxLane * LANE_WIDTH;
    const startX = -totalWidth / 2;

    const newNodes = commits.map((commit, index) => {
      const lane = commitLanes[commit.sha] || 0;
      return {
        id: commit.sha,
        type: 'graph',
        position: { x: startX + lane * LANE_WIDTH, y: index * ROW_HEIGHT },
        data: {
          sha: commit.sha.substring(0, 7),
          fullSha: commit.sha,
          message: commit.message,
          author: commit.author,
          age: commit.age,
          branches: commit.branches,
          is_head: commit.is_head,
          isAhead: aheadShas.has(commit.sha),
          isRemote: commit.sha === remoteSha,
          has_stash: commit.has_stash,
          has_notes: commit.has_notes
        }
      };
    });

    const newEdges = [];
    commits.forEach((commit) => {
      if (commit.parents) {
        commit.parents.forEach(parentSha => {
          if (commitMap.has(parentSha)) {
            newEdges.push({
              id: `${commit.sha}-${parentSha}`,
              source: commit.sha,
              target: parentSha,
              type: 'straight',
              animated: false,
              style: 'stroke: var(--text-tertiary); stroke-width: 3px;'
            });
          }
        });
      }
    });

    nodes.set(newNodes);
    edges.set(newEdges);
  } else {
    nodes.set([]);
    edges.set([]);
  }

  function handleNodeClick(event) {
    const nodeId = event.detail.node.id;
    const commit = commits.find(c => c.sha === nodeId);
    if (commit) {
      selectedCommit = selectedCommit?.sha === commit.sha ? null : commit;
      if (onNodeClick) {
        onNodeClick(commit);
      }
    }
  }
</script>

<div class="train-station-graph">
  <div class="graph-content" class:with-details={selectedCommit}>
    {#if $nodes.length > 0}
      <SvelteFlow
        nodes={$nodes}
        edges={$edges}
        {nodeTypes}
        fitView
        fitViewOptions={{
          padding: 0.3,
          maxZoom: 1.5,
          nodes: $nodes.slice(0, 8)
        }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
        panOnDrag={true}
        zoomOnScroll={true}
        zoomOnPinch={true}
        zoomOnDoubleClick={true}
        minZoom={0.2}
        maxZoom={4}
        on:nodeclick={handleNodeClick}
      >
        <Controls showZoom={true} showFitView={true} showInteractive={false} />
        <Background variant={BackgroundVariant.Dots} />
        <MiniMap />
      </SvelteFlow>
    {:else}
      <div class="loading">
        <div class="spinner"></div>
        <p>Loading graph...</p>
      </div>
    {/if}
  </div>

  {#if selectedCommit}
    <div class="details-panel">
      <div class="details-header">
        <h3>Commit Details</h3>
        <button class="close-btn" on:click={() => selectedCommit = null}>×</button>
      </div>
      <div class="details-content">
        <div class="detail-section">
          <label>SHA</label>
          <div class="detail-value monospace">{selectedCommit.sha}</div>
        </div>

        <div class="detail-section">
          <label>Message</label>
          <div class="detail-value">{selectedCommit.message}</div>
        </div>

        <div class="detail-section">
          <label>Author</label>
          <div class="detail-value">{selectedCommit.author}</div>
        </div>

        <div class="detail-section">
          <label>Date</label>
          <div class="detail-value">{selectedCommit.age}</div>
        </div>

        {#if selectedCommit.branches && selectedCommit.branches.length > 0}
          <div class="detail-section">
            <label>Branches</label>
            <div class="detail-value">
              <div class="branches-list">
                {#each selectedCommit.branches as branch}
                  <span class="branch-badge" style="background: {getBranchColor(branch)}">{branch}</span>
                {/each}
              </div>
            </div>
          </div>
        {/if}

        {#if selectedCommit.is_head}
          <div class="detail-section">
            <div class="head-badge">HEAD</div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .train-station-graph {
    height: 100%;
    width: 100%;
    display: flex;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .graph-content {
    flex: 1;
    min-height: 0;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    margin: 0 32px;
  }

  .graph-content.with-details {
    flex: 1;
    max-width: calc(100% - 370px);
  }

  .loading {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
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
    to { transform: rotate(360deg); }
  }

  /* SvelteFlow overrides */
  :global(.svelte-flow) {
    background: var(--bg-secondary) !important;
  }

  :global(.svelte-flow__controls) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
  }

  :global(.svelte-flow__controls button) {
    background: var(--bg-primary) !important;
    border-bottom: 1px solid var(--border-secondary) !important;
    color: var(--text-secondary) !important;
  }

  :global(.svelte-flow__controls button:hover) {
    background: var(--bg-hover) !important;
  }

  :global(.svelte-flow__minimap) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
    transform: scale(0.6);
    transform-origin: bottom right;
    transition: transform 0.2s ease;
    opacity: 0.7;
  }

  :global(.svelte-flow__minimap:hover) {
    transform: scale(1);
    opacity: 1;
  }

  :global(.svelte-flow__edge-path) {
    stroke: var(--text-tertiary) !important;
    stroke-width: 3px !important;
    stroke-linecap: round !important;
  }

  /* Details panel */
  .details-panel {
    flex: 0 0 350px;
    background: var(--bg-primary);
    border-radius: 8px;
    border: 1px solid var(--border-primary);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: slideIn 0.3s ease;
    margin-right: 16px;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .details-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-secondary);
  }

  .details-header h3 {
    margin: 0;
    font-size: 16px;
    color: var(--text-primary);
    font-weight: 600;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 24px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s;
    line-height: 1;
  }

  .close-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .details-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .detail-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .detail-section label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    font-weight: 600;
  }

  .detail-value {
    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
  }

  .monospace {
    font-family: 'Monaco', 'Courier New', monospace;
    background: var(--bg-secondary);
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
  }

  .branches-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .branch-badge {
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    color: white;
    font-weight: 600;
  }

  .head-badge {
    display: inline-block;
    padding: 6px 12px;
    background: rgba(var(--accent-primary-rgb, 250, 189, 47), 0.15);
    border: 1px solid var(--accent-primary);
    border-radius: 4px;
    color: var(--accent-primary);
    font-weight: 700;
    font-size: 12px;
  }

  @media (max-width: 1024px) {
    .train-station-graph {
      flex-direction: column;
    }

    .graph-content.with-details {
      max-width: 100%;
      flex: 1;
    }

    .details-panel {
      flex: 0 0 250px;
      max-height: 35vh;
      margin: 0 16px 16px;
    }
  }
</style>
