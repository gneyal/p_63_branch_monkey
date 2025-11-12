<script>
  import { commitTree } from '../stores/store.js';
  import { writable } from 'svelte/store';
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    MiniMap,
    useSvelteFlow
  } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import CommitNode from './CommitNode.svelte';

  export let onNodeClick = null;

  let selectedCommit = null;

  const nodes = writable([]);
  const edges = writable([]);
  const nodeTypes = {
    commit: CommitNode
  };

  // Transform commits to nodes and edges for Svelte Flow
  $: if ($commitTree && $commitTree.commits && $commitTree.commits.length > 0) {
    const commits = $commitTree.commits;
    const newNodes = [];
    const newEdges = [];

    // Create a map for quick lookup
    const commitMap = new Map(commits.map(c => [c.sha, c]));

    // Assign lanes to commits (vertical lines for each branch)
    const commitLanes = new Map(); // sha -> lane number
    const branchLanes = new Map(); // branch name -> lane number

    // Main branch always gets lane 0 (center)
    branchLanes.set('main', 0);
    branchLanes.set('master', 0);
    let nextLane = 1;

    // Process commits to assign lanes
    // Commits come newest to oldest, so we need to track lanes as we go
    commits.forEach((commit, index) => {
      let lane = null;

      // If this commit has a branch label (it's a branch tip)
      if (commit.branches && commit.branches.length > 0) {
        const branchName = commit.branches[0];

        // Check if this branch already has a lane assigned
        if (branchLanes.has(branchName)) {
          lane = branchLanes.get(branchName);
        } else {
          // New branch - assign it to the right of main
          lane = nextLane++;
          branchLanes.set(branchName, lane);
        }
      } else {
        // No branch label - inherit lane from children (commits that point to this as parent)
        // Look ahead to find which commit has this as a parent
        for (let i = 0; i < index; i++) {
          const child = commits[i];
          if (child.parents && child.parents.includes(commit.sha)) {
            if (commitLanes.has(child.sha)) {
              lane = commitLanes.get(child.sha);
              break;
            }
          }
        }

        // If still no lane, default to main lane
        if (lane === null) {
          lane = 0;
        }
      }

      commitLanes.set(commit.sha, lane);
    });

    // Layout settings
    const laneSpacing = 420;
    const commitSpacing = 150;

    // Calculate centering offset
    const maxLane = Math.max(...commitLanes.values());
    const totalWidth = maxLane * laneSpacing;
    const startX = -totalWidth / 2;

    // Create nodes with proper lane positioning
    commits.forEach((commit, index) => {
      const lane = commitLanes.get(commit.sha) || 0;
      const xOffset = startX + (lane * laneSpacing);

      newNodes.push({
        id: commit.sha,
        type: 'commit',
        position: { x: xOffset, y: index * commitSpacing },
        data: {
          sha: commit.sha.substring(0, 7),
          fullSha: commit.sha,
          message: commit.message,
          author: commit.author,
          age: commit.age,
          branches: commit.branches,
          is_head: commit.is_head
        }
      });

      // Create edges from this commit to its parents
      if (commit.parents && commit.parents.length > 0) {
        commit.parents.forEach(parentSha => {
          if (commitMap.has(parentSha)) {
            newEdges.push({
              id: `${commit.sha}-${parentSha}`,
              source: commit.sha,
              target: parentSha,
              type: 'smoothstep',
              animated: false,
              style: 'stroke: #888; stroke-width: 6px;'
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

  function handleNodeClickInternal(event) {
    const nodeId = event.detail.node.id;
    const commit = $commitTree?.commits?.find(c => c.sha === nodeId);
    if (commit) {
      selectedCommit = commit;
      if (onNodeClick) {
        onNodeClick(commit);
      }
    }
  }
</script>

<div class="commit-tree">
  <div class="tree-header">
    <h2 class="tree-title">🌳 Commit Tree</h2>
    <p class="tree-subtitle">Pan and zoom to explore • Click nodes for details</p>
  </div>

  <div class="tree-main">
    {#if $commitTree && $commitTree.commits}
      <div class="tree-content" class:with-details={selectedCommit}>
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
            zoomOnPinch={true}
            zoomOnDoubleClick={true}
            minZoom={0.3}
            maxZoom={3}
            defaultZoom={1}
            on:nodeclick={handleNodeClickInternal}
          >
            <Controls showZoom={true} showFitView={true} showInteractive={false} />
            <Background variant={BackgroundVariant.Dots} />
            <MiniMap />
          </SvelteFlow>
        {:else}
          <div style="color: yellow; padding: 10px;">
            Loading nodes...
          </div>
        {/if}
      </div>
    {:else}
      <div class="tree-loading">
        <div class="spinner"></div>
        <p>Loading commit tree...</p>
      </div>
    {/if}

    {#if selectedCommit}
      <div class="details-panel">
        <div class="details-header">
          <h3>Commit Details</h3>
          <button class="close-btn" on:click={() => selectedCommit = null}>✕</button>
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
                    <span class="branch-badge">{branch}</span>
                  {/each}
                </div>
              </div>
            </div>
          {/if}

          {#if selectedCommit.parents && selectedCommit.parents.length > 0}
            <div class="detail-section">
              <label>Parents</label>
              <div class="detail-value">
                {#each selectedCommit.parents as parent}
                  <div class="parent-sha monospace">{parent}</div>
                {/each}
              </div>
            </div>
          {/if}

          {#if selectedCommit.is_head}
            <div class="detail-section">
              <div class="head-badge">🔸 HEAD</div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .commit-tree {
    background: #1e1e1e;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .tree-header {
    padding: 20px 20px 16px 20px;
    background: #1a1a1a;
    border-bottom: 1px solid #333;
  }

  .tree-title {
    margin: 0;
    font-size: 28px;
    color: #e0e0e0;
    font-weight: 600;
  }

  .tree-subtitle {
    margin: 4px 0 0 0;
    font-size: 14px;
    color: #808080;
  }

  .tree-main {
    flex: 1;
    min-height: 0;
    display: flex;
    gap: 16px;
    overflow: hidden;
  }

  .tree-content {
    flex: 1;
    min-height: 0;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .tree-content.with-details {
    flex: 1;
    max-width: calc(100% - 370px);
  }

  @media (max-width: 1024px) {
    .tree-main {
      flex-direction: column;
    }

    .tree-content.with-details {
      max-width: 100%;
      flex: 1;
    }

    .details-panel {
      flex: 0 0 300px;
      max-height: 40vh;
    }
  }

  .tree-loading {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #808080;
    gap: 16px;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #333;
    border-top-color: #2196f3;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Override Svelte Flow dark theme styles */
  :global(.svelte-flow) {
    background: #121212 !important;
  }

  :global(.svelte-flow__controls) {
    background: #2d2d2d !important;
    border: 1px solid #444 !important;
  }

  :global(.svelte-flow__controls button) {
    background: #2d2d2d !important;
    border-bottom: 1px solid #444 !important;
    color: #e0e0e0 !important;
  }

  :global(.svelte-flow__controls button:hover) {
    background: #333 !important;
  }

  :global(.svelte-flow__minimap) {
    background: #2d2d2d !important;
    border: 1px solid #444 !important;
  }

  :global(.svelte-flow__edge-path) {
    stroke: #888 !important;
    stroke-width: 6px !important;
    stroke-linecap: square !important;
    stroke-linejoin: miter !important;
  }

  .details-panel {
    flex: 0 0 350px;
    background: #2d2d2d;
    border-radius: 8px;
    border: 1px solid #444;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: slideIn 0.3s ease;
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
    border-bottom: 1px solid #444;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .details-header h3 {
    margin: 0;
    font-size: 20px;
    color: #e0e0e0;
    font-weight: 600;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: #808080;
    font-size: 24px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .close-btn:hover {
    background: #3d3d3d;
    color: #e0e0e0;
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
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #808080;
    font-weight: 600;
  }

  .detail-value {
    color: #e0e0e0;
    font-size: 16px;
    line-height: 1.6;
    word-wrap: break-word;
  }

  .monospace {
    font-family: 'Monaco', 'Courier New', monospace;
    background: #1e1e1e;
    padding: 8px;
    border-radius: 4px;
    font-size: 14px;
  }

  .branches-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .branch-badge {
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 6px;
    background: #4caf50;
    color: white;
    font-weight: 600;
  }

  .parent-sha {
    margin-top: 4px;
  }

  .head-badge {
    display: inline-block;
    padding: 8px 16px;
    background: rgba(255, 215, 0, 0.2);
    border: 2px solid #ffd700;
    border-radius: 8px;
    color: #ffd700;
    font-weight: 700;
    font-size: 15px;
  }
</style>
